from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

class RiskProfile(str, Enum):
    CONSERVATIVE = "conservative"
    MODERATELY_CONSERVATIVE = "moderately_conservative"
    BALANCED = "balanced"
    GROWTH = "growth"
    AGGRESSIVE = "aggressive"

    @property
    def display_name(self) -> str:
        names = {
            RiskProfile.CONSERVATIVE: "Conservative",
            RiskProfile.MODERATELY_CONSERVATIVE: "Moderately Conservative",
            RiskProfile.BALANCED: "Balanced",
            RiskProfile.GROWTH: "Growth",
            RiskProfile.AGGRESSIVE: "Aggressive",
        }
        return names.get(self, self.value)

    @property
    def numeric_tier(self) -> int:
        tiers = {
            RiskProfile.CONSERVATIVE: 1,
            RiskProfile.MODERATELY_CONSERVATIVE: 2,
            RiskProfile.BALANCED: 3,
            RiskProfile.GROWTH: 4,
            RiskProfile.AGGRESSIVE: 5,
        }
        return tiers[self]

    @classmethod
    def from_numeric_tier(cls, tier: int) -> "RiskProfile":
        clamped = max(1, min(5, round(tier)))
        mapping = {
            1: cls.CONSERVATIVE,
            2: cls.MODERATELY_CONSERVATIVE,
            3: cls.BALANCED,
            4: cls.GROWTH,
            5: cls.AGGRESSIVE,
        }
        return mapping[clamped]

class KnockoutRuleTriggered(BaseModel):
    rule_id: str
    field: str
    trigger_value: str
    capped_to_profile: RiskProfile
    reason: str

class CapacityScoreBreakdown(BaseModel):
    age_score: float
    horizon_score: float
    emergency_fund_score: float
    income_stability_score: float
    share_of_net_worth_score: float
    withdrawal_score: float
    total_capacity_score: float = Field(..., ge=0.0, le=100.0)
    details: Dict[str, str] = Field(default_factory=dict)

class ToleranceScoreBreakdown(BaseModel):
    primary_goal_score: float
    reaction_to_drawdown_score: float
    max_acceptable_loss_score: float
    portfolio_preference_score: float
    investment_experience_score: float
    total_tolerance_score: float = Field(..., ge=0.0, le=100.0)
    details: Dict[str, str] = Field(default_factory=dict)

class AssessmentResult(BaseModel):
    capacity_score: float = Field(..., ge=0.0, le=100.0)
    capacity_tier: RiskProfile
    tolerance_score: float = Field(..., ge=0.0, le=100.0)
    tolerance_tier: RiskProfile
    unconstrained_profile: RiskProfile
    final_profile: RiskProfile
    knockout_rules_applied: List[KnockoutRuleTriggered] = Field(default_factory=list)
    explanation: str
    capacity_breakdown: CapacityScoreBreakdown
    tolerance_breakdown: ToleranceScoreBreakdown
