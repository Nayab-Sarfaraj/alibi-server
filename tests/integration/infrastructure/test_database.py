"""Integration checks for database infrastructure."""


def test_database_base_imports() -> None:
    from app.db.base import Base

    assert Base is not None
