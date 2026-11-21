from pathlib import Path

import pytest
from pydantic import ValidationError

from app.core import config
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


def test_deployed_secret_files_override_environment_values(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    (tmp_path / "DATABASE_URL").write_text("postgresql+psycopg://file:secret@db/alibi")
    (tmp_path / "SECRET_KEY").write_text("s" * 32)
    monkeypatch.setattr(config, "SECRETS_DIR", tmp_path)

    configured_settings = Settings(
        APP_ENV="production",
        DATABASE_URL="postgresql+psycopg://environment:secret@db/alibi",
        SECRET_KEY="e" * 32,
    )

    assert (
        configured_settings.database_url == "postgresql+psycopg://file:secret@db/alibi"
    )
    assert configured_settings.secret_key == "s" * 32
