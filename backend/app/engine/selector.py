from typing import List
from app.engine.allocation import (
    BASE_ALLOCATIONS,
    SLEEVE_METADATA,
    adapt_allocation_for_constraints,
)
from app.engine.market_data import market_data_service
from app.engine.universe import universe_service
from app.models.assessment import AssessmentResult
from app.models.questionnaire import (
    QuestionnaireSubmission,
)
from app.models.recommendation import (
    HoldingRecommendation,
    PortfolioMetrics,
    RecommendationResult,
    SleeveAllocation,
)


def build_recommendation(
    submission: QuestionnaireSubmission,
    assessment: AssessmentResult
) -> RecommendationResult:
    """
    Constructs a complete portfolio recommendation:
    1. Base asset allocation from final risk profile.
    2. Dynamic constraint adaptation (Sharia, ESG, Crypto).
    3. Sleeve narrowing & ETF selection.
    4. Notional calculations ($ initial & monthly).
    5. Aggregate weighted portfolio metrics.
    """
    profile = assessment.final_profile
    base_alloc = BASE_ALLOCATIONS[profile]
    adapted_alloc, constraint_notes = adapt_allocation_for_constraints(
        base_alloc, submission.constraints
    )

    initial_inv = submission.capacity.initial_investment_amount
    monthly_contrib = submission.capacity.planned_monthly_contribution
    currency = submission.constraints.base_currency.value

    # Build SleeveAllocations list
    sleeve_allocations: List[SleeveAllocation] = []
    for sleeve_key, target_pct in adapted_alloc.items():
        meta = SLEEVE_METADATA.get(sleeve_key, (sleeve_key.replace("_", " ").title(), "Other"))
        disp_name, asset_class = meta
        sleeve_allocations.append(
            SleeveAllocation(
                sleeve=sleeve_key,
                display_name=disp_name,
                asset_class=asset_class,
                target_pct=target_pct,
                notional_initial=round(initial_inv * (target_pct / 100.0), 2),
                notional_monthly=round(monthly_contrib * (target_pct / 100.0), 2),
            )
        )

    # Sort sleeves logically: Equity -> Fixed Income -> Real Assets -> Cash
    class_order = {"Equity": 1, "Fixed Income": 2, "Real Assets & Alts": 3, "Cash": 4, "Multi-Asset": 5}
    sleeve_allocations.sort(key=lambda s: (class_order.get(s.asset_class, 99), -s.target_pct))

    # Select Holdings per Sleeve
    holdings: List[HoldingRecommendation] = []
    all_tickers_selected: List[str] = []

    for sleeve_alloc in sleeve_allocations:
        sleeve_key = sleeve_alloc.sleeve
        weight = sleeve_alloc.target_pct
        if weight <= 0.0:
            continue

        candidates = universe_service.filter_and_rank_for_sleeve(
            sleeve_key, submission.constraints
        )

        if not candidates:
            continue

        # Top pick
        best_pick = candidates[0]
        ticker = best_pick["ticker"]
        all_tickers_selected.append(ticker)

        # Rationale formulation
        rationale_parts = []
        if best_pick.get("expense_ratio_pct") is not None:
            rationale_parts.append(f"Low expense ratio of {best_pick['expense_ratio_pct']}%")
        if best_pick.get("provider"):
            rationale_parts.append(f"Institutional provider ({best_pick['provider']})")
        if best_pick.get("sharia_compliant"):
            rationale_parts.append("Certified Sharia-compliant")
        if best_pick.get("esg"):
            rationale_parts.append("ESG sustainability screened")
        rationale = "; ".join(rationale_parts) or f"Target {sleeve_alloc.display_name} representation"

        holdings.append(
            HoldingRecommendation(
                ticker=ticker,
                name=best_pick.get("name") or ticker,
                sleeve=sleeve_key,
                region=best_pick.get("region", "Global"),
                asset_class=sleeve_alloc.asset_class,
                weight_pct=weight,
                notional_initial=sleeve_alloc.notional_initial,
                notional_monthly=sleeve_alloc.notional_monthly,
                expense_ratio_pct=best_pick.get("expense_ratio_pct"),
                distribution_yield_pct=best_pick.get("distribution_yield_pct"),
                fund_net_assets_usd=best_pick.get("fund_net_assets_usd"),
                sharia_compliant=best_pick.get("sharia_compliant", False),
                esg=best_pick.get("esg", False),
                crypto=best_pick.get("crypto", False),
                provider=best_pick.get("provider"),
                category=best_pick.get("category"),
                rationale=rationale,
            )
        )

    # Enrich holdings with market metrics
    metrics_map, data_source = market_data_service.get_metrics_batch(all_tickers_selected)
    for h in holdings:
        m = metrics_map.get(h.ticker, {})
        h.last_close = m.get("last_close")
        h.last_close_date = m.get("last_close_date")
        h.return_1y_pct = m.get("return_1y_pct")
        h.return_3y_annualised_pct = m.get("return_3y_annualised_pct")
        h.volatility_1y_pct = m.get("volatility_1y_pct")
        h.max_drawdown_3y_pct = m.get("max_drawdown_3y_pct")

    # Aggregate Portfolio Metrics
    weighted_er = sum(
        (h.expense_ratio_pct or 0.0) * (h.weight_pct / 100.0) for h in holdings
    )
    weighted_yield = sum(
        (h.distribution_yield_pct or 0.0) * (h.weight_pct / 100.0) for h in holdings
    )

    # 1Y Return
    rets_1y = [
        (h.return_1y_pct, h.weight_pct) for h in holdings if h.return_1y_pct is not None
    ]
    total_wt_1y = sum(w for _, w in rets_1y)
    weighted_1y = (
        round(sum(r * w for r, w in rets_1y) / total_wt_1y, 2)
        if total_wt_1y > 0
        else None
    )

    # 3Y Annualized Return
    rets_3y = [
        (h.return_3y_annualised_pct, h.weight_pct)
        for h in holdings
        if h.return_3y_annualised_pct is not None
    ]
    total_wt_3y = sum(w for _, w in rets_3y)
    weighted_3y = (
        round(sum(r * w for r, w in rets_3y) / total_wt_3y, 2)
        if total_wt_3y > 0
        else None
    )

    # Volatility
    vols = [
        (h.volatility_1y_pct, h.weight_pct)
        for h in holdings
        if h.volatility_1y_pct is not None
    ]
    total_wt_vol = sum(w for _, w in vols)
    weighted_vol = (
        round(sum(v * w for v, w in vols) / total_wt_vol, 2)
        if total_wt_vol > 0
        else None
    )

    # Max Drawdown
    dds = [
        (h.max_drawdown_3y_pct, h.weight_pct)
        for h in holdings
        if h.max_drawdown_3y_pct is not None
    ]
    total_wt_dd = sum(w for _, w in dds)
    weighted_dd = (
        round(sum(d * w for d, w in dds) / total_wt_dd, 2)
        if total_wt_dd > 0
        else None
    )

    # Asset class totals
    equity_pct = round(sum(h.weight_pct for h in holdings if h.asset_class == "Equity"), 1)
    fixed_inc_pct = round(sum(h.weight_pct for h in holdings if h.asset_class == "Fixed Income"), 1)
    cash_pct = round(sum(h.weight_pct for h in holdings if h.asset_class == "Cash"), 1)
    alts_pct = round(sum(h.weight_pct for h in holdings if h.asset_class in ("Real Assets & Alts", "Multi-Asset")), 1)

    portfolio_metrics = PortfolioMetrics(
        weighted_expense_ratio_pct=round(weighted_er, 4),
        weighted_distribution_yield_pct=round(weighted_yield, 2),
        weighted_return_1y_pct=weighted_1y,
        weighted_return_3y_annualised_pct=weighted_3y,
        weighted_volatility_1y_pct=weighted_vol,
        weighted_max_drawdown_3y_pct=weighted_dd,
        equity_pct=equity_pct,
        fixed_income_pct=fixed_inc_pct,
        cash_pct=cash_pct,
        alternatives_pct=alts_pct,
    )

    # Build concise narrative summary
    narrative = (
        f"Recommended a {profile.display_name} portfolio consisting of {equity_pct}% Equities, "
        f"{fixed_inc_pct}% Fixed Income, {alts_pct}% Real Assets/Alternatives, and {cash_pct}% Cash. "
        f"The portfolio is constructed with {len(holdings)} low-cost ETFs with a weighted expense ratio of "
        f"{weighted_er:.2f}% and an estimated distribution yield of {weighted_yield:.2f}%."
    )

    return RecommendationResult(
        risk_profile=profile,
        base_currency=currency,
        initial_investment=initial_inv,
        planned_monthly_contribution=monthly_contrib,
        sleeve_allocations=sleeve_allocations,
        holdings=holdings,
        portfolio_metrics=portfolio_metrics,
        market_data_source=data_source,
        narrative_summary=narrative,
        constraint_notes=constraint_notes,
    )
