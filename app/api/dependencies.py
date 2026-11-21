"""Dependencies shared across API versions and feature routers."""

import urllib.error
from dataclasses import dataclass
from typing import Annotated
from uuid import UUID

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import (
    PyJWKClient,
    PyJWKClientConnectionError,
    PyJWKClientError,
    PyJWKSetError,
)

from app.core.config import settings

_jwk_client: PyJWKClient | None = None


def get_jwk_client() -> PyJWKClient:
    """Lazily initialize and return the PyJWKClient with JWKS caching."""
    global _jwk_client
    if _jwk_client is None:
        if not settings.SUPABASE_JWKS_URL:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="SUPABASE_JWKS_URL is not configured",
            )
        _jwk_client = PyJWKClient(
            settings.SUPABASE_JWKS_URL,
            cache_jwk_set=True,
            lifespan=300,
        )
    return _jwk_client


@dataclass(frozen=True)
class AuthenticatedIdentity:
    """Authenticated Supabase principal identity."""

    auth_subject: UUID
    is_guest: bool
    email: str | None = None


@dataclass(frozen=True)
class AuthenticatedUser:
    """Authenticated principal shape for future protected endpoints."""

    id: str
    role: str


bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(bearer_scheme),
    ],
) -> AuthenticatedIdentity:
    """Verify Supabase JWT and return authenticated subject identity."""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    raw_jwt_token = credentials.credentials
    jwk_client = get_jwk_client()
    print("token", raw_jwt_token)
    try:
        signing_key = jwk_client.get_signing_key_from_jwt(raw_jwt_token)
        print("key", signing_key)
    except (
        PyJWKClientConnectionError,
        PyJWKSetError,
        urllib.error.URLError,
        TimeoutError,
    ) as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service temporarily unavailable",
        ) from exc
    except (PyJWKClientError, jwt.PyJWTError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=(
                str(exc)
                if settings.APP_ENV == "development"
                else "Invalid or expired access token"
            ),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    try:
        payload = jwt.decode(
            raw_jwt_token,
            key=signing_key.key,
            algorithms=["ES256"],
            issuer=settings.SUPABASE_JWT_ISSUER,
            audience=settings.SUPABASE_JWT_AUDIENCE,
            options={"require": ["exp", "iss", "aud", "sub"]},
        )
        print("payload", payload)
    except jwt.PyJWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=(
                str(exc)
                if settings.APP_ENV == "development"
                else "Invalid or expired access token"
            ),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    sub = payload.get("sub")
    if not sub:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing subject claim in token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        auth_subject = UUID(str(sub))
    except (ValueError, TypeError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid subject claim format: expected a valid UUID",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    is_guest = payload.get("is_anonymous", False)
    if not isinstance(is_guest, bool):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid is_anonymous claim format: expected a boolean",
            headers={"WWW-Authenticate": "Bearer"},
        )

    email = payload.get("email")
    if email is not None and not isinstance(email, str):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email claim format: expected a string",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return AuthenticatedIdentity(
        auth_subject=auth_subject,
        is_guest=is_guest,
        email=email,
    )


CurrentUser = Annotated[AuthenticatedIdentity, Depends(get_current_user)]


def get_request_id(request: Request) -> str | None:
    """Return a caller-provided request identifier when one is available."""
    return request.headers.get("X-Request-ID")
