from typing import List, Optional
from fastapi import APIRouter, Header, HTTPException, Query, status
from pydantic import BaseModel

from app.models.record import AssessmentRecord
from app.services.storage_service import storage_service

router = APIRouter()


class RecordVerificationResponse(BaseModel):
    record: AssessmentRecord
    integrity_status: str  # "VERIFIED" | "HASH_MISMATCH_TAMPERED"
    verified: bool
    audit_notes: str


@router.get("/records/{record_id}", response_model=RecordVerificationResponse)
def get_record(record_id: str):
    """
    Retrieves an immutable assessment record and cryptographically verifies
    its SHA-256 integrity hash to guarantee the recommendation has not been tampered with.
    """
    record = storage_service.get_record(record_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Assessment record '{record_id}' not found."
        )

    # Re-calculate hash to verify non-repudiation
    recalculated_hash = AssessmentRecord.compute_integrity_hash(
        inputs=record.inputs,
        scoring_engine_version=record.scoring_engine_version,
        final_profile=record.assessment.final_profile.value,
        created_at=record.created_at
    )

    is_valid = (record.integrity_hash == recalculated_hash)
    integrity_status = "VERIFIED" if is_valid else "HASH_MISMATCH_TAMPERED"
    audit_notes = (
        "Record cryptographic integrity confirmed. Inputs and scoring outputs are identical to creation state."
        if is_valid
        else "WARNING: Record content does not match the stored integrity hash. Potential data alteration detected."
    )

    return RecordVerificationResponse(
        record=record,
        integrity_status=integrity_status,
        verified=is_valid,
        audit_notes=audit_notes
    )


@router.get("/records", response_model=List[AssessmentRecord])
def list_records(
    user_id: Optional[str] = Query(None, description="Optional user ID filter"),
    limit: int = Query(50, ge=1, le=100, description="Max number of records to return"),
):
    resolved_uid = user_id
    if resolved_uid:
        return storage_service.list_records_for_user(resolved_uid)

    return storage_service.list_recent_records(limit=limit)
