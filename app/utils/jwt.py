from datetime import datetime, timedelta
import uuid
from typing import Any

from jose import jwt

from app.core.config import settings

Token_Types: dict[str, str] = {"ACCESS_TOKEN": "access", "REFRESH_TOKEN": "refresh"}


def create_access_token(data: dict[str, Any]) -> str:
    token, _ = _create_token(data, timedelta(minutes=15), Token_Types["ACCESS_TOKEN"])
    return token


def create_refresh_token(data: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    return _create_token(data, timedelta(days=7), Token_Types["REFRESH_TOKEN"])


def _create_token(data: dict[str, Any], expires_delta: timedelta, token_type: str) -> tuple[str, dict[str, Any]]:
    to_encode = data.copy()
    expire = datetime.now() + expires_delta
    jti = str(uuid.uuid4())
    to_encode["exp"] = expire
    to_encode["token_type"] = token_type
    to_encode["jti"] = jti
    token = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    return token, to_encode


def decode_token(token: str) -> dict[str, Any]:
    return jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])

