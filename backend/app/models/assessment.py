from enum import Enum


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
