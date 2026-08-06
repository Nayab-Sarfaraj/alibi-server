from pathlib import Path
from typing import Any

from pydantic import Field
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent


def as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


class Settings(BaseSettings):
    PROJECT_NAME: str = Field(default="courtroom-server", validation_alias="PROJECT_NAME")
    VERSION: str = Field(default="0.1.0", validation_alias="VERSION")
    APP_ENV: str = Field(default="development", validation_alias="APP_ENV")
    APP_HOST: str = Field(default="0.0.0.0", validation_alias="APP_HOST")
    APP_PORT: int = Field(default=8000, validation_alias="APP_PORT")
    LOG_LEVEL: str = Field(default="info", validation_alias="LOG_LEVEL")
    DATABASE_URL: str = Field(default="sqlite:///./courtroom.db", validation_alias="DATABASE_URL")
    SQL_ECHO: bool = Field(default=False, validation_alias="SQL_ECHO")
    SECRET_KEY: str = Field(default="your-secret-key", validation_alias="SECRET_KEY")

    model_config = {
        "env_file": BASE_DIR / ".." / ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


settings = Settings()
