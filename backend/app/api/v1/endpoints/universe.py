from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status

from app.engine.allocation import SLEEVE_METADATA
from app.engine.market_data import market_data_service
from app.engine.universe import universe_service

router = APIRouter()


@router.get("/universe")
def get_universe(
    sleeve: Optional[str] = Query(None, description="Filter by asset sleeve"),
    region: Optional[str] = Query(None, description="Filter by geographic region"),
    sharia_only: bool = Query(False, description="Filter for Sharia-compliant instruments"),
    esg_only: bool = Query(False, description="Filter for ESG-screened instruments"),
    crypto_only: bool = Query(False, description="Filter for crypto instruments"),
    limit: int = Query(250, ge=1, le=500),
):
    """
    Returns ETF universe instruments with applied filters and fallback market metrics.
    """
    instruments = universe_service.instruments

    if sleeve:
        instruments = [i for i in instruments if i.get("sleeve") == sleeve]
    if region:
        instruments = [i for i in instruments if i.get("region") == region]
    if sharia_only:
        instruments = [i for i in instruments if i.get("sharia_compliant") is True]
    if esg_only:
        instruments = [i for i in instruments if i.get("esg") is True]
    if crypto_only:
        instruments = [i for i in instruments if i.get("crypto") is True]

    # Enrich with latest price snapshot
    results = []
    for inst in instruments[:limit]:
        m, _ = market_data_service.get_metrics_for_ticker(inst["ticker"])
        results.append({**inst, "metrics": m})

    return {
        "count": len(results),
        "total_universe_count": len(universe_service.instruments),
        "instruments": results
    }


@router.get("/universe/sleeves")
def get_sleeves():
    """
    Returns all 20 investment sleeves with asset classes and instrument counts.
    """
    from collections import Counter
    counts = Counter(i["sleeve"] for i in universe_service.instruments)

    sleeves = []
    for sleeve_key, (name, asset_class) in SLEEVE_METADATA.items():
        sleeves.append({
            "sleeve": sleeve_key,
            "name": name,
            "asset_class": asset_class,
            "instrument_count": counts.get(sleeve_key, 0)
        })

    return {"sleeves": sleeves}


@router.get("/universe/instruments/{ticker}")
def get_instrument_detail(ticker: str):
    """
    Returns detailed information for a single ticker.
    """
    ticker_upper = ticker.upper()
    inst = universe_service.instruments_by_ticker.get(ticker_upper)
    if not inst:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Instrument '{ticker_upper}' not found in universe."
        )

    metrics, src = market_data_service.get_metrics_for_ticker(ticker_upper)
    return {
        "instrument": inst,
        "metrics": metrics,
        "metrics_source": src
    }
