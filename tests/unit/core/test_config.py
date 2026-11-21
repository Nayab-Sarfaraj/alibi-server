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


def test_supabase_settings_defaults_and_derivation() -> None:
    settings_with_url = Settings(
        _env_file=None,
        SUPABASE_URL="https://test-project.supabase.co",
    )
    assert settings_with_url.SUPABASE_URL == "https://test-project.supabase.co"
    assert (
        settings_with_url.SUPABASE_JWT_ISSUER
        == "https://test-project.supabase.co/auth/v1"
    )
    assert (
        settings_with_url.SUPABASE_JWKS_URL
        == "https://test-project.supabase.co/auth/v1/.well-known/jwks.json"
    )
    assert settings_with_url.SUPABASE_JWT_AUDIENCE == "authenticated"


def test_supabase_settings_explicit_override() -> None:
    settings_custom = Settings(
        _env_file=None,
        SUPABASE_URL="https://test-project.supabase.co",
        SUPABASE_PUBLISHABLE_KEY="test-publishable-key",
        SUPABASE_JWT_ISSUER="https://custom-issuer.example.com",
        SUPABASE_JWKS_URL="https://custom-issuer.example.com/jwks.json",
        SUPABASE_JWT_AUDIENCE="custom-audience",
    )
    assert settings_custom.SUPABASE_URL == "https://test-project.supabase.co"
    assert settings_custom.SUPABASE_PUBLISHABLE_KEY == "test-publishable-key"
    assert settings_custom.SUPABASE_JWT_ISSUER == "https://custom-issuer.example.com"
    assert (
        settings_custom.SUPABASE_JWKS_URL
        == "https://custom-issuer.example.com/jwks.json"
    )
    assert settings_custom.SUPABASE_JWT_AUDIENCE == "custom-audience"


@pytest.mark.parametrize(
    ("environment", "url"),
    [
        ("development", "http://supabase.example.com"),
        ("testing", "http://127.0.0.1:54321"),
        ("production", "http://supabase.example.com"),
        ("production", "https:///missing-host"),
    ],
)
def test_supabase_url_rejects_cleartext_or_invalid_hosts(
    environment: str,
    url: str,
) -> None:
    configured_settings = Settings(
        _env_file=None,
        APP_ENV=environment,
        DATABASE_URL="postgresql+psycopg://user@localhost/alibi",
        SUPABASE_URL=url,
    )

    with pytest.raises(ValueError, match="SUPABASE_URL"):
        configured_settings.validate_required_settings()


def test_development_allows_loopback_http_supabase_url() -> None:
    configured_settings = Settings(
        _env_file=None,
        APP_ENV="development",
        DATABASE_URL="postgresql+psycopg://user@localhost/alibi",
        SUPABASE_URL="http://127.0.0.1:54321",
    )

    configured_settings.validate_required_settings()
