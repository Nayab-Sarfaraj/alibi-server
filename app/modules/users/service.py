"""User application services."""

import logging
from typing import Any, cast
from uuid import UUID

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import AuthenticatedIdentity
from app.core.config import settings
from app.core.exceptions import (
    AppException,
    ConflictError,
    DatabaseError,
    ExternalServiceError,
    NotFoundError,
)
from app.modules.users import repository as user_repository
from app.modules.users.models import User

logger = logging.getLogger(__name__)


async def _supabase_request(
    method: str,
    path: str,
    access_token: str,
    payload: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Make a user-scoped Supabase Auth request without logging sensitive data."""
    if not settings.SUPABASE_URL or not settings.SUPABASE_PUBLISHABLE_KEY:
        raise ExternalServiceError(
            message="Supabase authentication is not configured",
            code="SUPABASE_NOT_CONFIGURED",
        )
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.request(
                method,
                f"{settings.SUPABASE_URL.rstrip('/')}{path}",
                headers={
                    "apikey": settings.SUPABASE_PUBLISHABLE_KEY,
                    "Authorization": f"Bearer {access_token}",
                },
                json=payload,
            )
    except httpx.RequestError as exc:
        logger.warning(
            "Supabase Auth request unavailable",
            extra={"failure_category": type(exc).__name__},
        )
        raise ExternalServiceError(
            message="Supabase authentication is temporarily unavailable",
            code="SUPABASE_UNAVAILABLE",
        ) from exc

    if response.is_success:
        try:
            return cast(dict[str, Any], response.json())
        except ValueError:
            return {}

    try:
        error_code = str(response.json().get("code", "")).lower()
    except (TypeError, ValueError):
        error_code = ""
    if response.status_code == 409 or error_code in {
        "email_exists",
        "email_already_exists",
        "user_already_exists",
    }:
        raise ConflictError(
            message="An account already uses this email address",
            code="SUPABASE_EMAIL_CONFLICT",
        )
    if response.status_code in {400, 422}:
        raise AppException(
            status_code=response.status_code,
            code="SUPABASE_INVALID_REQUEST",
            message="Supabase rejected the request",
        )
    if response.status_code in {401, 403}:
        raise AppException(
            status_code=response.status_code,
            code="SUPABASE_AUTHENTICATION_FAILED",
            message="Supabase rejected the authenticated session",
            headers={"WWW-Authenticate": "Bearer"}
            if response.status_code == 401
            else None,
        )
    if response.status_code == 429:
        raise AppException(
            status_code=429,
            code="SUPABASE_RATE_LIMITED",
            message="Too many authentication requests",
        )
    logger.warning(
        "Supabase Auth request failed",
        extra={"status_code": response.status_code, "failure_category": "upstream"},
    )
    raise ExternalServiceError(
        message="Supabase authentication is temporarily unavailable",
        code="SUPABASE_UNAVAILABLE",
    )


async def request_supabase_email_change(access_token: str, email: str) -> None:
    """Ask Supabase Auth to send its authenticated email-change confirmation."""
    await _supabase_request("PUT", "/auth/v1/user", access_token, {"email": email})


async def verify_supabase_email_change(
    identity: AuthenticatedIdentity,
    email: str,
    otp: str,
) -> dict[str, Any]:
    """Verify an email-change OTP and ensure Supabase returned the same user."""
    session = await _supabase_request(
        "POST",
        "/auth/v1/verify",
        identity.access_token,
        {"email": email, "token": otp, "type": "email_change"},
    )
    user = session.get("user")
    if not isinstance(user, dict) or str(user.get("id")) != str(identity.auth_subject):
        raise AppException(
            status_code=403,
            code="SUPABASE_IDENTITY_MISMATCH",
            message="Verified identity does not match the authenticated guest",
        )
    return session


async def set_supabase_password(identity: AuthenticatedIdentity, password: str) -> None:
    """Set a password only after Supabase confirms the email is verified."""
    user = await _supabase_request("GET", "/auth/v1/user", identity.access_token)
    if not user.get("email_confirmed_at"):
        raise AppException(
            status_code=403,
            code="EMAIL_NOT_VERIFIED",
            message="Verify the email address before setting a password",
        )
    await _supabase_request(
        "PUT", "/auth/v1/user", identity.access_token, {"password": password}
    )


async def get_or_create_user(
    user: AuthenticatedIdentity,
    db: AsyncSession,
) -> User:
    """Idempotently resolve an existing user or create a new one."""
    existing_user = await user_repository.find_user_auth_subject(user, db)
    if existing_user is not None:
        return await user_repository.synchronize_guest_identity(existing_user, user, db)

    created_user = await user_repository.create_user(user, db)
    if created_user is not None:
        return created_user

    # A concurrent request inserted this subject. The unique index and the
    # PostgreSQL conflict clause ensure there can only be one persisted row.
    existing_user = await user_repository.find_user_auth_subject(user, db)
    if existing_user is not None:
        return existing_user
    raise DatabaseError(
        message="User creation conflicted but the persisted user was unavailable",
        code="DATABASE_ERROR",
    )


async def create_new_user(
    user: AuthenticatedIdentity,
    db: AsyncSession,
) -> User:
    """Create a new user, raising ConflictError if already present."""
    existing_user = await user_repository.find_user_auth_subject(user, db)
    if existing_user is not None:
        raise ConflictError(
            message="User already exists for this identity",
            code="USER_ALREADY_EXISTS",
        )
    created_user = await user_repository.create_user(user, db)
    if created_user is None:
        raise ConflictError(
            message="User already exists for this identity",
            code="USER_ALREADY_EXISTS",
        )
    return created_user


async def upgrade_user_email(
    identity: AuthenticatedIdentity,
    email: str,
) -> None:
    """Request Supabase's verified email-change flow for this JWT session."""
    if not identity.is_guest:
        raise AppException(
            status_code=403,
            code="GUEST_IDENTITY_REQUIRED",
            message="Only anonymous users can request an account upgrade",
        )
    await request_supabase_email_change(identity.access_token, email)


async def get_user_by_id(
    user_id: UUID,
    db: AsyncSession,
) -> User:
    """Retrieve user by internal ID, raising NotFoundError if missing."""
    user = await user_repository.get_user_by_id(user_id, db)
    if user is None:
        raise NotFoundError(
            message=f"User with id {user_id} not found",
            code="USER_NOT_FOUND",
        )
    return user


__all__ = [
    "create_new_user",
    "get_or_create_user",
    "get_user_by_id",
    "upgrade_user_email",
]
