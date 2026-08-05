from typing import Any


class EvidenceService:
    def collect_evidence(self, case_id: int) -> dict[str, Any]:
        # TODO: implement evidence aggregation, indexing, and validation.
        return {"case_id": case_id, "evidence": []}
