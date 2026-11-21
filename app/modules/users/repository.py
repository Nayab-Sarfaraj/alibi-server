"""User persistence operations."""

import logging
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import AuthenticatedIdentity
from app.core.exceptions import ConflictError, DatabaseError
from app.modules.users.models import User

logger = logging.getLogger(__name__)


async def find_user_auth_subject(
    user: AuthenticatedIdentity,
    db: AsyncSession,
) -> User | None:
    """Look up an existing user by their unique Supabase auth_subject."""
    return await get_user_by_auth_subject(user.auth_subject, db)


async def get_user_by_auth_subject(
    auth_subject: UUID,
    db: AsyncSession,
) -> User | None:
    """Find a user record by their Supabase authentication UUID."""
    try:
        statement = select(User).where(User.auth_subject == auth_subject)
        return await db.scalar(statement)
    except SQLAlchemyError as exc:
        logger.exception("Database error finding user by auth_subject=%s", auth_subject)
        raise DatabaseError(
            message="Database query failed while looking up user",
            code="DATABASE_ERROR",
        ) from exc


async def get_user_by_id(
    user_id: UUID,
    db: AsyncSession,
) -> User | None:
    """Find a user record by internal application UUID."""
    try:
        statement = select(User).where(User.id == user_id)
        return await db.scalar(statement)
    except SQLAlchemyError as exc:
        logger.exception("Database error finding user by id=%s", user_id)
        raise DatabaseError(
            message="Database query failed while fetching user",
            code="DATABASE_ERROR",
        ) from exc


async def create_user(
    user: AuthenticatedIdentity,
    db: AsyncSession,
) -> User | None:
    """Atomically insert a user, returning ``None`` when the subject exists."""
    statement = (
        insert(User)
        .values(
            auth_subject=user.auth_subject,
            email=user.email or None,
            is_guest=user.is_guest,
        )
        .on_conflict_do_nothing(index_elements=[User.auth_subject])
        .returning(User)
    )
    try:
        result = await db.execute(statement)
        created_user = result.scalar_one_or_none()
        await db.commit()
        return created_user
    except SQLAlchemyError as exc:
        await db.rollback()
        logger.exception("Database error creating user")
        raise DatabaseError(
            message="Failed to persist user to database",
            code="DATABASE_ERROR",
        ) from exc


async def synchronize_guest_identity(
    user: User,
    identity: AuthenticatedIdentity,
    db: AsyncSession,
) -> User:
    """Persist the email only when a guest identity becomes an email identity."""
    if not (
        user.is_guest
        and user.email is None
        and not identity.is_guest
        and identity.email
    ):
        return user

    user.email = identity.email
    user.is_guest = False
    try:
        await db.flush()
        await db.commit()
        await db.refresh(user)
        return user
    except IntegrityError as exc:
        await db.rollback()
        raise ConflictError(
            message="An account already uses this email address",
            code="EMAIL_ALREADY_IN_USE",
        ) from exc
    except SQLAlchemyError as exc:
        await db.rollback()
        logger.exception("Database error synchronizing guest identity")
        raise DatabaseError(
            message="Failed to synchronize authenticated user identity",
            code="DATABASE_ERROR",
        ) from exc


async def update_user_profile(
    user: User,
    changes: dict[str, str | None],
    db: AsyncSession,
) -> User:
    """Persist an allowlisted set of profile fields for the resolved user."""
    for field, value in changes.items():
        setattr(user, field, value)
    try:
        await db.commit()
        await db.refresh(user)
        return user
    except SQLAlchemyError as exc:
        await db.rollback()
        logger.exception("Database error updating user profile")
        raise DatabaseError(
            message="Failed to update user profile",
            code="DATABASE_ERROR",
        ) from exc


__all__ = [
    "create_user",
    "find_user_auth_subject",
    "get_user_by_auth_subject",
    "get_user_by_id",
    "synchronize_guest_identity",
    "update_user_profile",
]
