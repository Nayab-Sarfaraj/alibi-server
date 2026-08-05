from pathlib import Path
from typing import Any

from pydantic import BaseSettings, Field

BASE_DIR = Path(__file__).resolve().parent.parent


def as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


class Settings(BaseSettings):
    PROJECT_NAME: str = Field("courtroom-server", env="PROJECT_NAME")
    VERSION: str = Field("0.1.0", env="VERSION")
    APP_ENV: str = Field("development", env="APP_ENV")
    APP_HOST: str = Field("0.0.0.0", env="APP_HOST")
    APP_PORT: int = Field(8000, env="APP_PORT")
    LOG_LEVEL: str = Field("info", env="LOG_LEVEL")
    DATABASE_URL: str = Field("sqlite:///./courtroom.db", env="DATABASE_URL")
    SQL_ECHO: bool = Field(False, env="SQL_ECHO")

    class Config:
        env_file = BASE_DIR / ".." / ".env"
        env_file_encoding = "utf-8"


settings = Settings()
