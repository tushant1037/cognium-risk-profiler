from typing import List, Optional
from pydantic import BaseModel, Field
from app.models.assessment import RiskProfile

class SleeveAllocation(BaseModel):
    sleeve: str
    display_name: str
    asset_class: str  # "Equity", "Fixed Income", "Cash", "Real Assets & Alts"
    target_pct: float = Field(..., ge=0.0, le=100.0)
    notional_initial: float = Field(..., ge=0.0)
    notional_monthly: float = Field(..., ge=0.0)

class HoldingRecommendation(BaseModel):
    ticker: str
    name: str
    sleeve: str
    region: str
    asset_class: str
    weight_pct: float = Field(..., ge=0.0, le=100.0)
    notional_initial: float = Field(..., ge=0.0)
    notional_monthly: float = Field(..., ge=0.0)
    last_close: Optional[float] = None
    last_close_date: Optional[str] = None
    expense_ratio_pct: Optional[float] = None
    distribution_yield_pct: Optional[float] = None
    fund_net_assets_usd: Optional[int] = None
    return_1y_pct: Optional[float] = None
    return_3y_annualised_pct: Optional[float] = None
    volatility_1y_pct: Optional[float] = None
    max_drawdown_3y_pct: Optional[float] = None
    sharia_compliant: bool = False
    esg: bool = False
    crypto: bool = False
    provider: Optional[str] = None
    category: Optional[str] = None
    rationale: str

class PortfolioMetrics(BaseModel):
    weighted_expense_ratio_pct: float
    weighted_distribution_yield_pct: float
    weighted_return_1y_pct: Optional[float] = None
    weighted_return_3y_annualised_pct: Optional[float] = None
    weighted_volatility_1y_pct: Optional[float] = None
    weighted_max_drawdown_3y_pct: Optional[float] = None
    equity_pct: float
    fixed_income_pct: float
    cash_pct: float
    alternatives_pct: float

class RecommendationResult(BaseModel):
    risk_profile: RiskProfile
    base_currency: str
    initial_investment: float
    planned_monthly_contribution: float
    sleeve_allocations: List[SleeveAllocation]
    holdings: List[HoldingRecommendation]
    portfolio_metrics: PortfolioMetrics
    market_data_source: str  # "live_yfinance" | "snapshot_fallback" | "mixed"
    narrative_summary: Optional[str] = None
    constraint_notes: List[str] = Field(default_factory=list)
