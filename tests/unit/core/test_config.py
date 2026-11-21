import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_app_environment_is_validated() -> None:
    with pytest.raises(ValidationError):
        Settings.model_validate({"APP_ENV": "invalid"})


def test_missing_database_url_is_rejected_at_startup() -> None:
    configured_settings = Settings.model_validate({"DATABASE_URL": None})

    with pytest.raises(ValueError, match="DATABASE_URL must be configured"):
        configured_settings.validate_required_settings()


def test_redacted_settings_excludes_connection_secrets() -> None:
    configured_settings = Settings.model_validate(
        {
            "DATABASE_URL": "postgresql+psycopg://user@localhost/alibi",
            "TEST_DATABASE_URL": ("postgresql+psycopg://user@localhost/alibi_test"),
        }
    )

    assert "DATABASE_URL" not in configured_settings.redacted_settings()
    assert "TEST_DATABASE_URL" not in configured_settings.redacted_settings()
