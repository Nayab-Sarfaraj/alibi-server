import os
from ipaddress import ip_address
from pathlib import Path
from typing import Literal
from urllib.parse import urlparse

from dotenv import dotenv_values
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[2]
AppEnvironment = Literal["development", "testing", "staging", "production"]

INSECURE_SECRET_KEYS = {"", "your-secret-key", "change-me"}


def resolve_secrets_dir() -> Path:
    """Read SECRETS_DIR from the process or the project's dotenv file."""
    configured_dir = os.getenv("SECRETS_DIR")
    if configured_dir is None:
        configured_dir = dotenv_values(BASE_DIR / ".env").get("SECRETS_DIR")
    return Path(configured_dir or "/run/secrets")


SECRETS_DIR = resolve_secrets_dir()
CONFIGURED_SECRETS_DIR = SECRETS_DIR if SECRETS_DIR.is_dir() else None


class Settings(BaseSettings):
    PROJECT_NAME: str = Field(default="alibi-server", validation_alias="PROJECT_NAME")
    VERSION: str = Field(default="0.1.0", validation_alias="VERSION")
    APP_ENV: AppEnvironment = Field(default="development", validation_alias="APP_ENV")
    APP_HOST: str = Field(default="0.0.0.0", validation_alias="APP_HOST")
    APP_PORT: int = Field(default=8000, validation_alias="APP_PORT")
    LOG_LEVEL: str = Field(default="info", validation_alias="LOG_LEVEL")
    CORS_ORIGINS: list[str] = Field(default_factory=list)
    TRUSTED_HOSTS: list[str] = Field(
        default_factory=lambda: ["localhost", "127.0.0.1", "testserver"]
    )
    MAX_REQUEST_BODY_BYTES: int = Field(
        default=1_048_576,
        ge=1024,
        le=10_485_760,
    )
    DATABASE_URL: SecretStr | None = Field(
        default=None, validation_alias="DATABASE_URL"
    )
    TEST_DATABASE_URL: SecretStr | None = Field(
        default=None, validation_alias="TEST_DATABASE_URL"
    )
    DB_POOL_SIZE: int = Field(default=5, ge=1)
    DB_MAX_OVERFLOW: int = Field(default=10, ge=0)
    DB_POOL_TIMEOUT: int = Field(default=10, gt=0)
    DB_POOL_RECYCLE: int = Field(default=1800, gt=0)
    REDIS_URL: SecretStr = SecretStr("redis://localhost:6379/0")
    REDIS_MAX_CONNECTIONS: int = Field(default=20, ge=1)
    REDIS_SOCKET_TIMEOUT: float = Field(default=2.0, gt=0)
    RABBITMQ_URL: SecretStr = SecretStr("amqp://guest:guest@localhost:5672/")
    RABBITMQ_PREFETCH: int = Field(default=10, ge=1)
    RABBITMQ_MAX_RETRIES: int = Field(default=3, ge=0)
    SQL_ECHO: bool = Field(default=False, validation_alias="SQL_ECHO")
    APP_DEBUG: bool = Field(default=False, validation_alias="APP_DEBUG")
    SECRET_KEY: SecretStr = Field(
        default=SecretStr("your-secret-key"), validation_alias="SECRET_KEY"
    )
    SUPABASE_URL: str = Field(default="", validation_alias="SUPABASE_URL")
    SUPABASE_PUBLISHABLE_KEY: str = Field(
        default="", validation_alias="SUPABASE_PUBLISHABLE_KEY"
    )
    SUPABASE_JWT_ISSUER: str = Field(default="", validation_alias="SUPABASE_JWT_ISSUER")
    SUPABASE_JWKS_URL: str = Field(default="", validation_alias="SUPABASE_JWKS_URL")
    SUPABASE_JWT_AUDIENCE: str = Field(
        default="authenticated", validation_alias="SUPABASE_JWT_AUDIENCE"
    )

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        secrets_dir=CONFIGURED_SECRETS_DIR,
    )

    def model_post_init(self, __context: object) -> None:
        """Derive default Supabase auth endpoints if SUPABASE_URL is provided."""
        if self.SUPABASE_URL:
            base_url = self.SUPABASE_URL.rstrip("/")
            if not self.SUPABASE_JWT_ISSUER:
                self.SUPABASE_JWT_ISSUER = f"{base_url}/auth/v1"
            if not self.SUPABASE_JWKS_URL:
                self.SUPABASE_JWKS_URL = f"{base_url}/auth/v1/.well-known/jwks.json"

        """Give mounted deployment secrets precedence over environment values."""
        if self.APP_ENV not in {"staging", "production"}:
            return

        for name in ("DATABASE_URL", "SECRET_KEY"):
            secret_file = SECRETS_DIR / name
            if secret_file.is_file():
                setattr(self, name, SecretStr(secret_file.read_text().strip()))

    @property
    def database_url(self) -> str:
        """Return the database URL only for consumers that require its plaintext value."""
        if self.DATABASE_URL is None:
            raise RuntimeError(
                "DATABASE_URL must be configured before initializing the database"
            )
        return self.DATABASE_URL.get_secret_value()

    @property
    def secret_key(self) -> str:
        """Return the application secret only for cryptographic operations."""
        return self.SECRET_KEY.get_secret_value()

    def redacted_settings(self) -> dict[str, object]:
        """Return safe configuration metadata suitable for diagnostic logs."""
        return self.model_dump(
            exclude={
                "DATABASE_URL",
                "TEST_DATABASE_URL",
                "REDIS_URL",
                "RABBITMQ_URL",
                "SECRET_KEY",
            }
        )

    def validate_required_settings(self) -> None:
        """Reject unsafe placeholder configuration in deployed environments."""
        errors: list[str] = []

        if self.DATABASE_URL is None:
            errors.append("DATABASE_URL must be configured")

        if self.SUPABASE_URL:
            parsed_url = urlparse(self.SUPABASE_URL)
            is_loopback = parsed_url.hostname == "localhost"
            if parsed_url.hostname and not is_loopback:
                try:
                    is_loopback = ip_address(parsed_url.hostname).is_loopback
                except ValueError:
                    pass
            if parsed_url.scheme == "https" and parsed_url.hostname:
                pass
            elif (
                self.APP_ENV == "development"
                and parsed_url.scheme == "http"
                and is_loopback
            ):
                pass
            else:
                errors.append(
                    "SUPABASE_URL must use HTTPS outside development; "
                    "development HTTP URLs must use a loopback host"
                )

        if self.APP_ENV in {"staging", "production"}:
            if not self.TRUSTED_HOSTS or "*" in self.TRUSTED_HOSTS:
                errors.append(
                    "TRUSTED_HOSTS must contain explicit hostnames outside development"
                )
            required_secret_files = ("DATABASE_URL", "SECRET_KEY")
            if not SECRETS_DIR.is_dir():
                errors.append(f"SECRETS_DIR does not exist: {SECRETS_DIR}")
            else:
                missing_files = [
                    secret_name
                    for secret_name in required_secret_files
                    if not (SECRETS_DIR / secret_name).is_file()
                ]
                if missing_files:
                    errors.append(
                        "missing required secret files: " + ", ".join(missing_files)
                    )
            if self.secret_key in INSECURE_SECRET_KEYS or len(self.secret_key) < 32:
                errors.append(
                    "SECRET_KEY must be a non-placeholder value of at least 32 characters"
                )

        if errors:
            raise ValueError("Invalid application settings: " + "; ".join(errors))


class DevelopmentSettings(Settings):
    APP_ENV: Literal["development"] = "development"
    SQL_ECHO: bool = False
    APP_DEBUG: bool = True


class TestingSettings(Settings):
    APP_ENV: Literal["testing"] = "testing"


class StagingSettings(Settings):
    APP_ENV: Literal["staging"] = "staging"


class ProductionSettings(Settings):
    APP_ENV: Literal["production"] = "production"


SETTINGS_BY_ENVIRONMENT: dict[AppEnvironment, type[Settings]] = {
    "development": DevelopmentSettings,
    "testing": TestingSettings,
    "staging": StagingSettings,
    "production": ProductionSettings,
}


def get_settings() -> Settings:
    """Load the settings class matching the configured deployment environment."""
    environment = Settings().APP_ENV
    return SETTINGS_BY_ENVIRONMENT[environment]()


settings = get_settings()
