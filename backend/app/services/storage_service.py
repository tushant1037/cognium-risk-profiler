import json
import os
from pathlib import Path
from typing import Dict, List, Optional
from app.config import settings
from app.models.record import AssessmentRecord

class StorageService:
    """
    Unified Storage Service:
    Saves and retrieves immutable assessment records.
    """

    def __init__(self):
        self.local_dir = settings.LOCAL_STORAGE_DIR / "assessments"
        os.makedirs(self.local_dir, exist_ok=True)

    def save_record(self, record: AssessmentRecord) -> str:
        """Saves an immutable assessment record."""
        self._save_local(record)
        return record.id

    def get_record(self, record_id: str) -> Optional[AssessmentRecord]:
        """Retrieves an immutable assessment record by its ID."""
        local_path = self.local_dir / f"{record_id}.json"
        if local_path.exists():
            with open(local_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return AssessmentRecord.model_validate(data)
        return None

    def list_records_for_user(self, user_id: str) -> List[AssessmentRecord]:
        """Lists records for a given user ID."""
        records: List[AssessmentRecord] = []

        for file in self.local_dir.glob("*.json"):
            try:
                with open(file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if data.get("user_id") == user_id:
                        records.append(AssessmentRecord.model_validate(data))
            except Exception:
                continue

        return records

    def list_recent_records(self, limit: int = 50) -> List[AssessmentRecord]:
        """Lists recent assessment records (useful for demo/local evaluation mode)."""
        records: List[AssessmentRecord] = []

        # Local search sorted by modified / creation time descending
        local_files = sorted(
            self.local_dir.glob("*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        for file in local_files[:limit]:
            try:
                with open(file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    records.append(AssessmentRecord.model_validate(data))
            except Exception:
                continue

        return records

    def _save_local(self, record: AssessmentRecord) -> None:
        local_path = self.local_dir / f"{record.id}.json"
        with open(local_path, "w", encoding="utf-8") as f:
            json.dump(record.model_dump(mode="json"), f, indent=2)
        print(f"Record {record.id} saved locally to {local_path}.")


storage_service = StorageService()
