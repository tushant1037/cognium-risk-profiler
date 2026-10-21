from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class NaturalLanguageRequest(BaseModel):
    prompt: str = Field(min_length=3, max_length=2000)

    @field_validator("prompt")
    @classmethod
    def prompt_must_not_be_blank(cls, value: str) -> str:
        prompt = value.strip()
        if not prompt:
            raise ValueError("Prompt must not be blank.")
        return prompt


class ParsedInvestmentIntent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    preferred_sleeves: list[str] = Field(
        default_factory=list,
        max_length=20,
        description="Preferred exact sleeve values from the ETF universe.",
    )
    preferred_categories: list[str] = Field(
        default_factory=list,
        max_length=63,
        description="Preferred exact category values from the ETF universe.",
    )
    preferred_regions: list[str] = Field(
        default_factory=list,
        max_length=19,
        description="Preferred exact region values from the ETF universe.",
    )
    max_expense_ratio_pct: Optional[float] = Field(
        default=None,
        ge=0,
        le=100,
        description="Maximum annual expense ratio, expressed as a percentage.",
    )
    min_distribution_yield_pct: Optional[float] = Field(
        default=None,
        ge=0,
        le=100,
        description="Minimum distribution yield, expressed as a percentage.",
    )
    exclude_crypto: bool = Field(
        default=False,
        description="Exclude instruments unless crypto is explicitly false.",
    )
    require_esg: bool = Field(
        default=False,
        description="Require instruments explicitly marked ESG compliant.",
    )
    require_sharia_compliant: bool = Field(
        default=False,
        description="Require instruments explicitly marked Sharia compliant.",
    )


class MatchedInstrument(BaseModel):
    ticker: str
    name: str
    sleeve: str
    region: str
    category: Optional[str] = None
    expense_ratio_pct: Optional[float] = None
    distribution_yield_pct: Optional[float] = None
    sharia_compliant: bool
    esg: bool
    crypto: bool
    justification: str


class NaturalLanguageRecommendationResponse(BaseModel):
    filters: ParsedInvestmentIntent
    count: int
    matched_instruments: list[MatchedInstrument]
    narrative: str
