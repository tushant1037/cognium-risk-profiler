import json
import math
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import pandas as pd
from app.config import settings
import yfinance as yf

class MarketDataService:
    def __init__(self, snapshot_path: Optional[Path] = None):
        self.snapshot_path = snapshot_path or settings.SNAPSHOT_PATH
        self.fallback_data: Dict[str, dict] = {}
        self.cache: Dict[str, Tuple[dict, float]] = {}  # ticker -> (metrics, timestamp)
        self.load_snapshot()

    def load_snapshot(self) -> None:
        """Loads snapshot.json as the baseline ground truth and fallback."""
        try:
            if self.snapshot_path and self.snapshot_path.exists():
                with open(self.snapshot_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for item in data.get("prices", []):
                        ticker = item.get("ticker")
                        if ticker:
                            self.fallback_data[ticker] = item
            else:
                print(f"Snapshot path does not exist: {self.snapshot_path}")
        except Exception as e:
            print(f"Error loading snapshot.json: {e}")

    def compute_metrics_from_series(self, series: pd.Series) -> Optional[dict]:
        """Derives financial metrics using the exact methodology from build.py."""
        s = series.dropna()
        if len(s) < 30:
            return None

        last = float(s.iloc[-1])
        out = {
            "last_close": round(last, 4),
            "last_close_date": s.index[-1].strftime("%Y-%m-%d"),
        }

        def ret_over(days: int) -> Optional[float]:
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
            if len(rets) >= 60
            else None
        )
        dd = s / s.cummax() - 1
        out["max_drawdown_3y_pct"] = round(float(dd.min() * 100), 2)
        return out

    def get_metrics_for_ticker(self, ticker: str) -> Tuple[dict, str]:
        """
        Retrieves market metrics for a ticker with multi-layer resilience:
        1. In-memory cache
        2. Live yfinance fetch (if enabled and within timeout)
        3. Local snapshot.json fallback
        """
        now = time.time()

        # Check Cache
        if ticker in self.cache:
            cached_data, cached_at = self.cache[ticker]
            if now - cached_at < settings.MARKET_DATA_CACHE_TTL_SECONDS:
                return cached_data, "cache"

        # Attempt live yfinance if enabled
        if settings.ENABLE_LIVE_YFINANCE:
            try:
                t = yf.Ticker(ticker)
                hist = t.history(period="3y", interval="1d", auto_adjust=True)
                if not hist.empty and "Close" in hist.columns:
                    metrics = self.compute_metrics_from_series(hist["Close"])
                    if metrics:
                        metrics["ticker"] = ticker
                        self.cache[ticker] = (metrics, now)
                        return metrics, "live_yfinance"
            except Exception as e:
                print(f"Live yfinance fetch failed for {ticker}: {e}; falling back to snapshot.")

        # Fallback to Snapshot
        fallback = self.fallback_data.get(ticker)
        if fallback:
            self.cache[ticker] = (fallback, now)
            return fallback, "snapshot_fallback"

        # Default empty if symbol not found anywhere
        empty = {
            "ticker": ticker,
            "last_close": None,
            "last_close_date": None,
            "return_1y_pct": None,
            "return_3y_annualised_pct": None,
            "volatility_1y_pct": None,
            "max_drawdown_3y_pct": None,
        }
        return empty, "missing"

    def get_metrics_batch(self, tickers: List[str]) -> Tuple[Dict[str, dict], str]:
        """Batch metrics retrieval for portfolio construction."""
        results = {}
        sources = set()
        for t in tickers:
            m, src = self.get_metrics_for_ticker(t)
            results[t] = m
            sources.add(src)

        if len(sources) == 1:
            overall_source = list(sources)[0]
        else:
            overall_source = "mixed (" + ", ".join(sorted(sources)) + ")"

        return results, overall_source


market_data_service = MarketDataService()
