from typing import Any

from sqlalchemy.orm import Session

from app.models.example import ExampleModel


class CaseRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(self, case_id: int) -> ExampleModel | None:
        return self.session.query(ExampleModel).filter(ExampleModel.id == case_id).first()

    def list_all(self) -> list[ExampleModel]:
        return self.session.query(ExampleModel).all()

    def save(self, example: ExampleModel) -> ExampleModel:
        self.session.add(example)
        self.session.commit()
        self.session.refresh(example)
        return example
