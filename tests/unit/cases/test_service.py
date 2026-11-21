"""Unit tests for case application services."""


def test_cases_service_module_imports() -> None:
    from app.modules.cases import service

    assert service is not None
