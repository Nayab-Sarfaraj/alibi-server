from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parents[2]
AppEnvironment = Literal["development", "testing", "staging", "production"]

DEFAULT_DATABASE_URL = ""
INSECURE_SECRET_KEYS = {"", "your-secret-key", "change-me"}


class Settings(BaseSettings):
    PROJECT_NAME: str = Field(default="alibi-server", validation_alias="PROJECT_NAME")
    VERSION: str = Field(default="0.1.0", validation_alias="VERSION")
    APP_ENV: AppEnvironment = Field(default="development", validation_alias="APP_ENV")
    APP_HOST: str = Field(default="0.0.0.0", validation_alias="APP_HOST")
    APP_PORT: int = Field(default=8000, validation_alias="APP_PORT")
    LOG_LEVEL: str = Field(default="info", validation_alias="LOG_LEVEL")
    DATABASE_URL: str = Field(
        default=DEFAULT_DATABASE_URL, validation_alias="DATABASE_URL"
    )
    SQL_ECHO: bool = Field(default=False, validation_alias="SQL_ECHO")
    SECRET_KEY: str = Field(default="your-secret-key", validation_alias="SECRET_KEY")

    model_config = {
        "env_file": BASE_DIR / ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }

    def validate_required_settings(self) -> None:
        """Reject unsafe placeholder configuration in deployed environments."""
        errors: list[str] = []

        if not self.DATABASE_URL:
            errors.append("DATABASE_URL must be configured")

        if self.APP_ENV in {"staging", "production"}:
            if self.DATABASE_URL == DEFAULT_DATABASE_URL:
                errors.append("DATABASE_URL must not use the development default")
            if self.SECRET_KEY in INSECURE_SECRET_KEYS or len(self.SECRET_KEY) < 32:
                errors.append(
                    "SECRET_KEY must be a non-placeholder value of at least 32 characters"
                )

        if errors:
            raise ValueError("Invalid application settings: " + "; ".join(errors))


class DevelopmentSettings(Settings):
    APP_ENV: Literal["development"] = "development"
    SQL_ECHO: bool = True


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
