export type InvestmentHorizon = "under 2 years" | "2–5" | "5–10" | "10+";
export type EmergencyFund =
  | "none"
  | "under 3 months"
  | "3–6 months"
  | "6+ months of expenses";
export type IncomeStability =
  | "salaried"
  | "variable or commission"
  | "self-employed"
  | "no earned income";
export type ShareOfLiquidNetWorth =
  | "under 10%"
  | "10–25%"
  | "25–50%"
  | "over 50%";
export type PrimaryGoal =
  | "capital preservation"
  | "income"
  | "balanced growth"
  | "aggressive growth";
export type DrawdownReaction = "sell everything" | "sell some" | "hold" | "buy more";
export type MaxAcceptableLoss = "0%" | "−5%" | "−15%" | "−30% or more";
export type PortfolioPreference = "A" | "B" | "C";
export type InvestmentExperience =
  | "none"
  | "funds only"
  | "individual stocks and ETFs"
  | "derivatives or leverage";
export type BaseCurrency = "USD" | "AED" | "EUR" | "GBP";
export type Exclusion =
  | "none"
  | "no crypto"
  | "sharia-compliant only"
  | "ESG preference";
export type RiskProfile =
  | "conservative"
  | "moderately_conservative"
  | "balanced"
  | "growth"
  | "aggressive";

export interface QuestionnaireSubmission {
  capacity: {
    birth_year: number;
    investment_horizon: InvestmentHorizon;
    initial_investment_amount: number;
    planned_monthly_contribution: number;
    emergency_fund: EmergencyFund;
    income_stability: IncomeStability;
    share_of_liquid_net_worth: ShareOfLiquidNetWorth;
    withdrawal_expectation: boolean;
  };
  tolerance: {
    primary_goal: PrimaryGoal;
    reaction_to_drawdown: DrawdownReaction;
    max_acceptable_loss: MaxAcceptableLoss;
    portfolio_preference: PortfolioPreference;
    investment_experience: InvestmentExperience;
  };
  constraints: {
    base_currency: BaseCurrency;
    exclusions: Exclusion[];
  };
  additional_circumstances?: string | null;
}

export interface KnockoutRule {
  rule_id: string;
  field: string;
  trigger_value: string;
  capped_to_profile: RiskProfile;
  reason: string;
}

export interface ScoreBreakdown {
  total_capacity_score?: number;
  total_tolerance_score?: number;
  details: Record<string, string>;
}

export interface AssessmentResult {
  capacity_score: number;
  capacity_tier: RiskProfile;
  tolerance_score: number;
  tolerance_tier: RiskProfile;
  unconstrained_profile: RiskProfile;
  final_profile: RiskProfile;
  knockout_rules_applied: KnockoutRule[];
  explanation: string;
  capacity_breakdown: ScoreBreakdown;
  tolerance_breakdown: ScoreBreakdown;
}

export interface SleeveAllocation {
  sleeve: string;
  display_name: string;
  asset_class: string;
  target_pct: number;
  notional_initial: number;
  notional_monthly: number;
}

export interface Holding {
  ticker: string;
  name: string;
  sleeve: string;
  region: string;
  asset_class: string;
  weight_pct: number;
  notional_initial: number;
  notional_monthly: number;
  last_close: number | null;
  last_close_date: string | null;
  expense_ratio_pct: number | null;
  distribution_yield_pct: number | null;
  fund_net_assets_usd: number | null;
  return_1y_pct: number | null;
  return_3y_annualised_pct: number | null;
  volatility_1y_pct: number | null;
  max_drawdown_3y_pct: number | null;
  sharia_compliant: boolean;
  esg: boolean;
  crypto: boolean;
  provider: string | null;
  category: string | null;
  rationale: string;
}

export interface PortfolioMetrics {
  weighted_expense_ratio_pct: number;
  weighted_distribution_yield_pct: number;
  weighted_return_1y_pct: number | null;
  weighted_return_3y_annualised_pct: number | null;
  weighted_volatility_1y_pct: number | null;
  weighted_max_drawdown_3y_pct: number | null;
  equity_pct: number;
  fixed_income_pct: number;
  cash_pct: number;
  alternatives_pct: number;
}

export interface RecommendationResult {
  risk_profile: RiskProfile;
  base_currency: string;
  initial_investment: number;
  planned_monthly_contribution: number;
  sleeve_allocations: SleeveAllocation[];
  holdings: Holding[];
  portfolio_metrics: PortfolioMetrics;
  market_data_source: "live_yfinance" | "snapshot_fallback" | "mixed" | string;
  narrative_summary: string | null;
  constraint_notes: string[];
}

export interface AssessmentPreview {
  assessment: AssessmentResult;
  recommendation: RecommendationResult;
}

export interface AssessmentRecord extends AssessmentPreview {
  id: string;
  created_at: string;
  user_id: string | null;
  user_email: string | null;
  schema_version: string;
  scoring_engine_version: string;
  inputs: QuestionnaireSubmission;
  integrity_hash: string;
}

export interface RecordVerification {
  record: AssessmentRecord;
  integrity_status: string;
  verified: boolean;
  audit_notes: string;
}

export interface NaturalLanguageInstrument {
  ticker: string;
  name: string;
  sleeve: string;
  region: string;
  category: string | null;
  expense_ratio_pct: number | null;
  distribution_yield_pct: number | null;
  sharia_compliant: boolean;
  esg: boolean;
  crypto: boolean;
  justification: string;
}

export interface ParsedIntent {
  preferred_sleeves: string[];
  preferred_categories: string[];
  preferred_regions: string[];
  max_expense_ratio_pct: number | null;
  min_distribution_yield_pct: number | null;
  exclude_crypto: boolean;
  require_esg: boolean;
  require_sharia_compliant: boolean;
}

export interface NaturalLanguageResponse {
  filters: ParsedIntent;
  count: number;
  matched_instruments: NaturalLanguageInstrument[];
  narrative: string;
}
