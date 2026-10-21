import json, time, math, sys
from datetime import datetime, timezone
import numpy as np
import pandas as pd
import yfinance as yf
from tickers import U

SYMS = [t for t, *_ in U]
META = {t: {"sleeve": s, "region": r, "flags": f} for t, s, r, f in U}

# ---------- history ----------
print(f"fetching history for {len(SYMS)} symbols...", flush=True)
px = yf.download(SYMS, period="3y", interval="1d", auto_adjust=True,
                 progress=False, threads=True)["Close"]
print("history shape:", px.shape, flush=True)

missing = [s for s in SYMS if s not in px.columns or px[s].dropna().empty]
print("no history:", missing, flush=True)


def metrics(series):
    s = series.dropna()
    if len(s) < 30:
        return None
    last = float(s.iloc[-1])
    out = {"last_close": round(last, 4),
           "last_close_date": s.index[-1].strftime("%Y-%m-%d")}

    def ret_over(days):
        cutoff = s.index[-1] - pd.Timedelta(days=days)
        w = s[s.index >= cutoff]
        if len(w) < 20:
            return None
        yrs = days / 365.25
        total = float(w.iloc[-1] / w.iloc[0])
        return round((total ** (1 / yrs) - 1) * 100, 2) if yrs > 1 else round((total - 1) * 100, 2)

    out["return_1y_pct"] = ret_over(365)
    out["return_3y_annualised_pct"] = ret_over(365 * 3) if len(s) > 600 else None

    rets = s.pct_change().dropna()
    out["volatility_1y_pct"] = (
        round(float(rets.tail(252).std() * math.sqrt(252) * 100), 2)
        if len(rets) >= 60 else None
    )
    dd = s / s.cummax() - 1
    out["max_drawdown_3y_pct"] = round(float(dd.min() * 100), 2)
    return out


# ---------- metadata ----------
FIELDS = {"longName": "name", "category": "category", "netExpenseRatio": "expense_ratio_pct",
          "totalAssets": "aum_usd", "fundInceptionDate": "inception",
          "fundFamily": "provider", "currency": "currency", "yield": "yield_pct"}

info = {}
for n, sym in enumerate(SYMS, 1):
    for attempt in range(3):
        try:
            i = yf.Ticker(sym).info
            info[sym] = i
            break
        except Exception as e:
            if attempt == 2:
                print(f"  !! {sym}: {e}", flush=True)
                info[sym] = {}
            time.sleep(2 * (attempt + 1))
    if n % 25 == 0:
        print(f"  info {n}/{len(SYMS)}", flush=True)
    time.sleep(0.15)

# ---------- emit ----------
universe, snapshot = [], []
dropped = []

for sym in SYMS:
    i = info.get(sym) or {}
    m = metrics(px[sym]) if sym in px.columns else None
    if m is None:
        dropped.append(sym)
        continue

    inception = i.get("fundInceptionDate")
    if inception:
        inception = datetime.fromtimestamp(inception, tz=timezone.utc).strftime("%Y-%m-%d")

    aum = i.get("totalAssets")
    universe.append({
        "ticker": sym,
        "name": i.get("longName") or sym,
        "sleeve": META[sym]["sleeve"],
        "region": META[sym]["region"],
        "category": i.get("category"),
        "provider": i.get("fundFamily"),
        "currency": i.get("currency", "USD"),
        "expense_ratio_pct": i.get("netExpenseRatio"),
        "fund_net_assets_usd": int(aum) if isinstance(aum, (int, float)) else None,
        "distribution_yield_pct": round(i.get("yield") * 100, 2) if isinstance(i.get("yield"), float) else None,
        "inception_date": inception,
        "sharia_compliant": "sharia" in META[sym]["flags"],
        "esg": "esg" in META[sym]["flags"],
        "crypto": "crypto" in META[sym]["flags"],
    })
    snapshot.append({"ticker": sym, **m})

asof = datetime.now(timezone.utc).strftime("%Y-%m-%d")
json.dump({"as_of": asof, "count": len(universe), "instruments": universe},
          open("universe.json", "w"), indent=2)
json.dump({"as_of": asof, "source": f"yfinance {yf.__version__}",
           "note": "Fallback price snapshot. Regenerate with build.py.",
           "count": len(snapshot), "prices": snapshot},
          open("snapshot.json", "w"), indent=2)

print(f"\nuniverse: {len(universe)}  dropped: {dropped}")
miss_er = [u["ticker"] for u in universe if u["expense_ratio_pct"] is None]
print(f"missing expense ratio: {len(miss_er)} {miss_er[:20]}")
miss_aum = [u["ticker"] for u in universe if u["fund_net_assets_usd"] is None]
print(f"missing net assets: {len(miss_aum)} {miss_aum[:20]}")
