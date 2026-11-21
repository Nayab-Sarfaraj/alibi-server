"""Integration checks for case persistence wiring."""


def test_cases_repository_module_imports() -> None:
    from app.modules.cases import repository

    assert repository is not None
