from enum import Enum

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
