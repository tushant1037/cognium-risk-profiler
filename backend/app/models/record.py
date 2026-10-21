import hashlib
import json
from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field
from app.models.questionnaire import QuestionnaireSubmission
from app.models.assessment import AssessmentResult
from app.models.recommendation import RecommendationResult


class AssessmentRecord(BaseModel):
    id: str = Field(..., description="Unique assessment record ID")
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="Immutable timestamp of assessment creation in UTC"
    )
    user_id: Optional[str] = Field(default=None, description="Authenticated Firebase UID if present")
    user_email: Optional[str] = Field(default=None, description="User email if authenticated")
    schema_version: str = "1.0.0"
    scoring_engine_version: str = "1.0.0"
    inputs: QuestionnaireSubmission
    assessment: AssessmentResult
    recommendation: RecommendationResult
    integrity_hash: str = Field(..., description="SHA-256 hash of inputs, scoring engine version, and results")

    @classmethod
    def compute_integrity_hash(
        cls,
        inputs: QuestionnaireSubmission,
        scoring_engine_version: str,
        final_profile: str,
        created_at: str
    ) -> str:
        payload = {
            "inputs": inputs.model_dump(mode="json"),
            "scoring_engine_version": scoring_engine_version,
            "final_profile": final_profile,
            "created_at": created_at
        }
        serialized = json.dumps(payload, sort_keys=True)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()
