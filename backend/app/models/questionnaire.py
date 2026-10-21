from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator

class InvestmentHorizon(str, Enum):
    UNDER_2_YEARS = "under 2 years"
    TWO_TO_FIVE = "2–5"
    FIVE_TO_TEN = "5–10"
    TEN_PLUS = "10+"

class EmergencyFund(str, Enum):
    NONE = "none"
    UNDER_3_MONTHS = "under 3 months"
    THREE_TO_SIX_MONTHS = "3–6 months"
    SIX_PLUS_MONTHS = "6+ months of expenses"

class IncomeStability(str, Enum):
    SALARIED = "salaried"
    VARIABLE_COMMISSION = "variable or commission"
    SELF_EMPLOYED = "self-employed"
    NO_EARNED_INCOME = "no earned income"

class ShareOfLiquidNetWorth(str, Enum):
    UNDER_10_PCT = "under 10%"
    TEN_TO_25_PCT = "10–25%"
    TWENTY_FIVE_TO_50_PCT = "25–50%"
    OVER_50_PCT = "over 50%"

class PrimaryGoal(str, Enum):
    CAPITAL_PRESERVATION = "capital preservation"
    INCOME = "income"
    BALANCED_GROWTH = "balanced growth"
    AGGRESSIVE_GROWTH = "aggressive growth"

class ReactionToDrawdown(str, Enum):
    SELL_EVERYTHING = "sell everything"
    SELL_SOME = "sell some"
    HOLD = "hold"
    BUY_MORE = "buy more"

class MaxAcceptableLoss(str, Enum):
    ZERO_PCT = "0%"
    MINUS_5_PCT = "−5%"
    MINUS_15_PCT = "−15%"
    MINUS_30_PCT_OR_MORE = "−30% or more"

class PortfolioPreference(str, Enum):
    A = "A"  # 5% a year, worst fall -19% (20/80 stock/bond)
    B = "B"  # 10% a year, worst fall -22% (60/40 stock/bond)
    C = "C"  # 15% a year, worst fall -32% (90/10 stock/bond)

class InvestmentExperience(str, Enum):
    NONE = "none"
    FUNDS_ONLY = "funds only"
    STOCKS_AND_ETFS = "individual stocks and ETFs"
    DERIVATIVES_LEVERAGE = "derivatives or leverage"

class BaseCurrency(str, Enum):
    USD = "USD"
    AED = "AED"
    EUR = "EUR"
    GBP = "GBP"

class ExclusionOption(str, Enum):
    NONE = "none"
    NO_CRYPTO = "no crypto"
    SHARIA_COMPLIANT_ONLY = "sharia-compliant only"
    ESG_PREFERENCE = "ESG preference"

class RiskCapacity(BaseModel):
    birth_year: int = Field(..., ge=1900, le=2015, description="Year of birth")
    investment_horizon: InvestmentHorizon
    initial_investment_amount: float = Field(..., ge=100.0, description="Initial investment amount in base currency")
    planned_monthly_contribution: float = Field(default=0.0, ge=0.0, description="Planned monthly contribution")
    emergency_fund: EmergencyFund
    income_stability: IncomeStability
    share_of_liquid_net_worth: ShareOfLiquidNetWorth
    withdrawal_expectation: bool = Field(
        ...,
        description="True if customer expects to withdraw more than 25% within 3 years, else False"
    )

    @field_validator("birth_year")
    @classmethod
    def validate_birth_year(cls, v: int) -> int:
        from datetime import datetime
        current_year = datetime.now().year
        age = current_year - v
        if age < 18:
            raise ValueError(f"Investor must be at least 18 years old (birth year {v} indicates age {age})")
        if age > 105:
            raise ValueError(f"Please enter a valid birth year (age {age} is out of bounds)")
        return v


class RiskTolerance(BaseModel):
    primary_goal: PrimaryGoal
    reaction_to_drawdown: ReactionToDrawdown
    max_acceptable_loss: MaxAcceptableLoss
    portfolio_preference: PortfolioPreference
    investment_experience: InvestmentExperience


class Constraints(BaseModel):
    base_currency: BaseCurrency = BaseCurrency.USD
    exclusions: List[ExclusionOption] = Field(default_factory=lambda: [ExclusionOption.NONE])

    @field_validator("exclusions")
    @classmethod
    def sanitize_exclusions(cls, v: List[ExclusionOption]) -> List[ExclusionOption]:
        # If specific exclusions are selected alongside 'none', drop 'none'
        non_none = [e for e in v if e != ExclusionOption.NONE]
        if non_none:
            return list(set(non_none))
        return [ExclusionOption.NONE]


class QuestionnaireSubmission(BaseModel):
    capacity: RiskCapacity
    tolerance: RiskTolerance
    constraints: Constraints
    additional_circumstances: Optional[str] = Field(
        default=None,
        max_length=1500,
        description="Optional free-text circumstances provided by client"
    )
    user_id: Optional[str] = Field(default=None, description="Optional authenticated user ID")
    user_email: Optional[str] = Field(default=None, description="Optional user email from Google SSO")
