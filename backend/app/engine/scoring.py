from typing import List
from app.models.questionnaire import (
    QuestionnaireSubmission,
    InvestmentHorizon,
    EmergencyFund,
    IncomeStability,
    ShareOfLiquidNetWorth,
    PrimaryGoal,
    ReactionToDrawdown,
    MaxAcceptableLoss,
    PortfolioPreference,
    InvestmentExperience,
)
from app.models.assessment import (
    RiskProfile,
    CapacityScoreBreakdown,
    ToleranceScoreBreakdown,
    KnockoutRuleTriggered,
    AssessmentResult,
)

ENGINE_VERSION = "1.0.0"


def calculate_capacity_score(
    sub: QuestionnaireSubmission, current_year: int = 2026
) -> CapacityScoreBreakdown:
    details = {}

    # 1. Age Score (Max 20 pts)
    age = current_year - sub.capacity.birth_year
    if age < 35:
        age_score = 20.0
        age_note = f"Age {age} (<35): Maximum human capital runway (20 pts)"
    elif age < 50:
        age_score = 15.0
        age_note = f"Age {age} (35-49): Strong earning and compounding years (15 pts)"
    elif age < 65:
        age_score = 10.0
        age_note = f"Age {age} (50-64): Maturing runway, transition towards wealth preservation (10 pts)"
    else:
        age_score = 5.0
        age_note = f"Age {age} (65+): Decumulation phase; capital preservation prioritised (5 pts)"
    details["age"] = age_note

    # 2. Investment Horizon (Max 20 pts)
    horizon_map = {
        InvestmentHorizon.UNDER_2_YEARS: (0.0, "Under 2 years: Very short duration, cannot absorb market cycles (0 pts)"),
        InvestmentHorizon.TWO_TO_FIVE: (7.0, "2–5 years: Medium-short duration (7 pts)"),
        InvestmentHorizon.FIVE_TO_TEN: (14.0, "5–10 years: Solid medium-to-long term horizon (14 pts)"),
        InvestmentHorizon.TEN_PLUS: (20.0, "10+ years: Multi-decade compounding horizon (20 pts)"),
    }
    horizon_score, horizon_note = horizon_map[sub.capacity.investment_horizon]
    details["horizon"] = horizon_note

    # 3. Emergency Fund (Max 15 pts)
    efund_map = {
        EmergencyFund.NONE: (0.0, "No emergency fund: Extreme liquidity vulnerability (0 pts)"),
        EmergencyFund.UNDER_3_MONTHS: (5.0, "Under 3 months: Modest reserve buffer (5 pts)"),
        EmergencyFund.THREE_TO_SIX_MONTHS: (12.0, "3–6 months: Solid standard safety buffer (12 pts)"),
        EmergencyFund.SIX_PLUS_MONTHS: (15.0, "6+ months: Robust liquidity buffer against forced selling (15 pts)"),
    }
    efund_score, efund_note = efund_map[sub.capacity.emergency_fund]
    details["emergency_fund"] = efund_note

    # 4. Income Stability (Max 15 pts)
    income_map = {
        IncomeStability.NO_EARNED_INCOME: (0.0, "No earned income: Low capacity to replenish losses (0 pts)"),
        IncomeStability.VARIABLE_COMMISSION: (5.0, "Variable or commission: Fluctuating cash flow (5 pts)"),
        IncomeStability.SELF_EMPLOYED: (10.0, "Self-employed: Entrepreneurial cash flow (10 pts)"),
        IncomeStability.SALARIED: (15.0, "Salaried: Highly predictable regular income (15 pts)"),
    }
    income_score, income_note = income_map[sub.capacity.income_stability]
    details["income_stability"] = income_note

    # 5. Share of Liquid Net Worth (Max 15 pts)
    networth_map = {
        ShareOfLiquidNetWorth.OVER_50_PCT: (3.0, "Over 50%: Large fraction of wealth committed (3 pts)"),
        ShareOfLiquidNetWorth.TWENTY_FIVE_TO_50_PCT: (7.0, "25–50%: Moderate concentration of liquid assets (7 pts)"),
        ShareOfLiquidNetWorth.TEN_TO_25_PCT: (11.0, "10–25%: Controlled allocation of net worth (11 pts)"),
        ShareOfLiquidNetWorth.UNDER_10_PCT: (15.0, "Under 10%: Minor fraction of wealth, high loss buffer (15 pts)"),
    }
    networth_score, networth_note = networth_map[sub.capacity.share_of_liquid_net_worth]
    details["share_of_liquid_net_worth"] = networth_note

    # 6. Withdrawal Expectation (Max 15 pts)
    if sub.capacity.withdrawal_expectation:
        withdrawal_score = 0.0
        withdrawal_note = "Expects to withdraw >25% within 3 years: Significant liquidity requirement (0 pts)"
    else:
        withdrawal_score = 15.0
        withdrawal_note = "No near-term large withdrawal expected: Capital is unencumbered (15 pts)"
    details["withdrawal_expectation"] = withdrawal_note

    total_capacity = round(
        age_score + horizon_score + efund_score + income_score + networth_score + withdrawal_score,
        1
    )

    return CapacityScoreBreakdown(
        age_score=age_score,
        horizon_score=horizon_score,
        emergency_fund_score=efund_score,
        income_stability_score=income_score,
        share_of_net_worth_score=networth_score,
        withdrawal_score=withdrawal_score,
        total_capacity_score=total_capacity,
        details=details,
    )


def calculate_tolerance_score(sub: QuestionnaireSubmission) -> ToleranceScoreBreakdown:
    details = {}

    # 1. Primary Goal (Max 20 pts)
    goal_map = {
        PrimaryGoal.CAPITAL_PRESERVATION: (4.0, "Capital preservation: High aversion to nominal loss (4 pts)"),
        PrimaryGoal.INCOME: (10.0, "Income: Focus on steady cash distributions (10 pts)"),
        PrimaryGoal.BALANCED_GROWTH: (16.0, "Balanced growth: Moderate appetite for capital appreciation (16 pts)"),
        PrimaryGoal.AGGRESSIVE_GROWTH: (20.0, "Aggressive growth: Maximum capital accumulation target (20 pts)"),
    }
    goal_score, goal_note = goal_map[sub.tolerance.primary_goal]
    details["primary_goal"] = goal_note

    # 2. Reaction to Drawdown (Max 25 pts)
    reaction_map = {
        ReactionToDrawdown.SELL_EVERYTHING: (0.0, "Sell everything: High behavioral risk of panic-selling at troughs (0 pts)"),
        ReactionToDrawdown.SELL_SOME: (8.0, "Sell some: Aversion to prolonged volatility (8 pts)"),
        ReactionToDrawdown.HOLD: (16.0, "Hold: Disciplined pass-through through market cycles (16 pts)"),
        ReactionToDrawdown.BUY_MORE: (25.0, "Buy more: Opportunistic risk-seeking behavior during downturns (25 pts)"),
    }
    reaction_score, reaction_note = reaction_map[sub.tolerance.reaction_to_drawdown]
    details["reaction_to_drawdown"] = reaction_note

    # 3. Maximum Acceptable One-Year Loss (Max 25 pts)
    loss_map = {
        MaxAcceptableLoss.ZERO_PCT: (0.0, "0%: Zero nominal drawdown tolerance (0 pts)"),
        MaxAcceptableLoss.MINUS_5_PCT: (8.0, "-5%: Low tolerance for downward fluctuation (8 pts)"),
        MaxAcceptableLoss.MINUS_15_PCT: (16.0, "-15%: Moderate tolerance for normal cyclical drawdowns (16 pts)"),
        MaxAcceptableLoss.MINUS_30_PCT_OR_MORE: (25.0, "-30% or more: High drawdown tolerance (25 pts)"),
    }
    loss_score, loss_note = loss_map[sub.tolerance.max_acceptable_loss]
    details["max_acceptable_loss"] = loss_note

    # 4. Portfolio Preference (Max 18 pts)
    pref_map = {
        PortfolioPreference.A: (5.0, "Portfolio A (5% return, -19% worst drawdown): Prefers conservative bond-heavy profile (5 pts)"),
        PortfolioPreference.B: (12.0, "Portfolio B (10% return, -22% worst drawdown): Balanced risk/reward tradeoff (12 pts)"),
        PortfolioPreference.C: (18.0, "Portfolio C (15% return, -32% worst drawdown): Willing to absorb steep drawdowns for high returns (18 pts)"),
    }
    pref_score, pref_note = pref_map[sub.tolerance.portfolio_preference]
    details["portfolio_preference"] = pref_note

    # 5. Investment Experience (Max 12 pts)
    exp_map = {
        InvestmentExperience.NONE: (2.0, "None: First-time investor (2 pts)"),
        InvestmentExperience.FUNDS_ONLY: (5.0, "Funds only: Familiar with collective investment schemes (5 pts)"),
        InvestmentExperience.STOCKS_AND_ETFS: (9.0, "Individual stocks & ETFs: Direct market experience (9 pts)"),
        InvestmentExperience.DERIVATIVES_LEVERAGE: (12.0, "Derivatives or leverage: Sophisticated market understanding (12 pts)"),
    }
    exp_score, exp_note = exp_map[sub.tolerance.investment_experience]
    details["investment_experience"] = exp_note

    total_tolerance = round(
        goal_score + reaction_score + loss_score + pref_score + exp_score,
        1
    )

    return ToleranceScoreBreakdown(
        primary_goal_score=goal_score,
        reaction_to_drawdown_score=reaction_score,
        max_acceptable_loss_score=loss_score,
        portfolio_preference_score=pref_score,
        investment_experience_score=exp_score,
        total_tolerance_score=total_tolerance,
        details=details,
    )


def score_to_risk_tier(score: float) -> RiskProfile:
    """Map a 0-100 score to one of the 5 risk profiles."""
    if score < 25.0:
        return RiskProfile.CONSERVATIVE
    elif score < 45.0:
        return RiskProfile.MODERATELY_CONSERVATIVE
    elif score < 65.0:
        return RiskProfile.BALANCED
    elif score < 85.0:
        return RiskProfile.GROWTH
    else:
        return RiskProfile.AGGRESSIVE


def evaluate_knockout_rules(sub: QuestionnaireSubmission) -> List[KnockoutRuleTriggered]:
    """
    Evaluates hard knockout constraints where specific answers strictly constrain
    the outcome regardless of how high other questions scored.
    """
    triggered: List[KnockoutRuleTriggered] = []

    # Knockout 1: Horizon under 2 years -> Must be Conservative
    if sub.capacity.investment_horizon == InvestmentHorizon.UNDER_2_YEARS:
        triggered.append(
            KnockoutRuleTriggered(
                rule_id="KO_HORIZON_SHORT",
                field="investment_horizon",
                trigger_value=sub.capacity.investment_horizon.value,
                capped_to_profile=RiskProfile.CONSERVATIVE,
                reason="Investment horizon under 2 years provides insufficient time to recover from equity drawdowns; capped at Conservative.",
            )
        )

    # Knockout 2: Drawdown reaction is 'sell everything' -> Must be Conservative
    if sub.tolerance.reaction_to_drawdown == ReactionToDrawdown.SELL_EVERYTHING:
        triggered.append(
            KnockoutRuleTriggered(
                rule_id="KO_PANIC_SELLER",
                field="reaction_to_drawdown",
                trigger_value=sub.tolerance.reaction_to_drawdown.value,
                capped_to_profile=RiskProfile.CONSERVATIVE,
                reason="Client stated they would sell all holdings in a 20% drawdown. Allocating to volatile assets poses severe behavioral panic-selling risk; capped at Conservative.",
            )
        )

    # Knockout 3: Max acceptable loss is 0% -> Must be Conservative
    if sub.tolerance.max_acceptable_loss == MaxAcceptableLoss.ZERO_PCT:
        triggered.append(
            KnockoutRuleTriggered(
                rule_id="KO_ZERO_LOSS_TOLERANCE",
                field="max_acceptable_loss",
                trigger_value=sub.tolerance.max_acceptable_loss.value,
                capped_to_profile=RiskProfile.CONSERVATIVE,
                reason="Client has zero tolerance for 1-year capital loss; portfolio must be strictly capped at Conservative capital-preservation instruments.",
            )
        )

    # Knockout 4: Expected withdrawal >25% within 3 years -> Capped at Moderately Conservative
    if sub.capacity.withdrawal_expectation:
        triggered.append(
            KnockoutRuleTriggered(
                rule_id="KO_WITHDRAWAL_EXPECTATION",
                field="withdrawal_expectation",
                trigger_value="true",
                capped_to_profile=RiskProfile.MODERATELY_CONSERVATIVE,
                reason="Anticipated withdrawal exceeding 25% within 3 years demands liquidity buffer; capped at Moderately Conservative.",
            )
        )

    # Knockout 5: No emergency fund -> Capped at Moderately Conservative
    if sub.capacity.emergency_fund == EmergencyFund.NONE:
        triggered.append(
            KnockoutRuleTriggered(
                rule_id="KO_NO_EMERGENCY_FUND",
                field="emergency_fund",
                trigger_value=sub.capacity.emergency_fund.value,
                capped_to_profile=RiskProfile.MODERATELY_CONSERVATIVE,
                reason="Absence of an emergency fund creates high risk of involuntary asset liquidation during personal financial distress; capped at Moderately Conservative.",
            )
        )

    return triggered


def compute_assessment(sub: QuestionnaireSubmission) -> AssessmentResult:
    """
    Computes capacity and tolerance scores separately, applies fiduciary binding constraints,
    evaluates hard knockout rules, and produces an auditable, deterministic result.
    """
    capacity_breakdown = calculate_capacity_score(sub)
    tolerance_breakdown = calculate_tolerance_score(sub)

    cap_tier = score_to_risk_tier(capacity_breakdown.total_capacity_score)
    tol_tier = score_to_risk_tier(tolerance_breakdown.total_tolerance_score)

    # Fiduciary Binding Constraint:
    # A customer cannot take more risk than their capacity permits (financial ruin risk),
    # nor more risk than their tolerance permits (behavioral panic-selling risk).
    # Baseline profile is the minimum of capacity tier and tolerance tier.
    unconstrained_numeric = min(cap_tier.numeric_tier, tol_tier.numeric_tier)
    unconstrained_profile = RiskProfile.from_numeric_tier(unconstrained_numeric)

    # Evaluate knockout rules
    knockouts = evaluate_knockout_rules(sub)

    final_tier_num = unconstrained_numeric
    for ko in knockouts:
        ko_cap_num = ko.capped_to_profile.numeric_tier
        if ko_cap_num < final_tier_num:
            final_tier_num = ko_cap_num

    final_profile = RiskProfile.from_numeric_tier(final_tier_num)

    # Build human-readable audit explanation
    reasons = []
    reasons.append(
        f"Capacity Score: {capacity_breakdown.total_capacity_score}/100 ({cap_tier.display_name})."
    )
    reasons.append(
        f"Tolerance Score: {tolerance_breakdown.total_tolerance_score}/100 ({tol_tier.display_name})."
    )

    if cap_tier != tol_tier:
        reasons.append(
            f"Under fiduciary suitability standards, risk profile is bounded by the lower of capacity and tolerance ({unconstrained_profile.display_name})."
        )

    if knockouts:
        ko_descriptions = [f"{ko.field} ({ko.trigger_value}): {ko.reason}" for ko in knockouts]
        reasons.append(f"Hard constraints applied: {'; '.join(ko_descriptions)}")

    reasons.append(f"Final Assigned Risk Profile: {final_profile.display_name}.")
    explanation = " ".join(reasons)

    return AssessmentResult(
        capacity_score=capacity_breakdown.total_capacity_score,
        capacity_tier=cap_tier,
        tolerance_score=tolerance_breakdown.total_tolerance_score,
        tolerance_tier=tol_tier,
        unconstrained_profile=unconstrained_profile,
        final_profile=final_profile,
        knockout_rules_applied=knockouts,
        explanation=explanation,
        capacity_breakdown=capacity_breakdown,
        tolerance_breakdown=tolerance_breakdown,
    )
