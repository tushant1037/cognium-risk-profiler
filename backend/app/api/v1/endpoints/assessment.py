import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Header, HTTPException, status
from typing import Optional

from app.engine.scoring import compute_assessment, ENGINE_VERSION
from app.engine.selector import build_recommendation
from app.models.questionnaire import QuestionnaireSubmission
from app.models.record import AssessmentRecord
from app.services.storage_service import storage_service
from app.services.llm_service import llm_service

router = APIRouter()


@router.post("/assess", response_model=AssessmentRecord, status_code=status.HTTP_201_CREATED)
def create_assessment(
    submission: QuestionnaireSubmission,
):
    """
    Submits a suitability questionnaire, executes the 3-stage pipeline:
    1. Risk Assessment (Capacity vs Tolerance + Knockouts)
    2. Portfolio Recommendation (Allocation, Instrument Selection, Market Metrics)
    3. Immutable Record Creation with Cryptographic SHA-256 Non-Repudiation Hash
    """
    # 1. Handle optional Firebase Auth token if passed
    user_id = submission.user_id
    user_email = submission.user_email
    
    # 2. Stage 2: Assessment Engine
    assessment = compute_assessment(submission)

    # 3. Stage 3: Recommendation Engine
    recommendation = build_recommendation(submission, assessment)

    # 4. Generate contextual commentary
    commentary = llm_service.generate_investor_commentary(
        assessment=assessment,
        recommendation=recommendation,
        additional_circumstances=submission.additional_circumstances
    )
    recommendation.narrative_summary = commentary

    # 5. Build immutable record with integrity hash
    record_id = f"rec_{uuid.uuid4().hex[:12]}"
    created_at = datetime.now(timezone.utc).isoformat()
    integrity_hash = AssessmentRecord.compute_integrity_hash(
        inputs=submission,
        scoring_engine_version=ENGINE_VERSION,
        final_profile=assessment.final_profile.value,
        created_at=created_at
    )

    record = AssessmentRecord(
        id=record_id,
        created_at=created_at,
        user_id=user_id,
        user_email=user_email,
        schema_version="1.0.0",
        scoring_engine_version=ENGINE_VERSION,
        inputs=submission,
        assessment=assessment,
        recommendation=recommendation,
        integrity_hash=integrity_hash
    )

    # 6. Persist to Firestore / Local Storage
    storage_service.save_record(record)

    return record


@router.post("/assess/preview")
def preview_assessment(submission: QuestionnaireSubmission):
    """
    Interactive preview endpoint for instant frontend feedback without persisting.
    """
    assessment = compute_assessment(submission)
    recommendation = build_recommendation(submission, assessment)
    return {
        "assessment": assessment,
        "recommendation": recommendation
    }
