from datetime import datetime
from typing import Any

from app.models.example import ExampleModel
from app.db.session import SessionLocal


class CaseService:
    def __init__(self) -> None:
        self.db = SessionLocal()

    def get_case_summary(self, case_id: int) -> dict[str, Any]:
        # TODO: implement real case lookup logic.
        return {"case_id": case_id, "summary": "Case summary not implemented."}

    def create_example(self, name: str) -> ExampleModel:
        example = ExampleModel(name=name)
        self.db.add(example)
        self.db.commit()
        self.db.refresh(example)
        return example
