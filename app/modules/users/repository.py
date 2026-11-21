"""User persistence operations."""

import logging
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import AuthenticatedIdentity
from app.core.exceptions import DatabaseError
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
            email=user.email,
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


__all__ = [
    "create_user",
    "find_user_auth_subject",
    "get_user_by_auth_subject",
    "get_user_by_id",
]
