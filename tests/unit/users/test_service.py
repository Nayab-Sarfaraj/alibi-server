"""Unit tests for user application services."""


def test_users_service_module_imports() -> None:
    from app.modules.users import service

    assert service is not None
