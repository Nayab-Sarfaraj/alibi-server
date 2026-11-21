"""User application services."""

import logging
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import AuthenticatedIdentity
from app.core.exceptions import ConflictError, DatabaseError, NotFoundError
from app.modules.users import repository as user_repository
from app.modules.users.models import User

logger = logging.getLogger(__name__)


async def get_or_create_user(
    user: AuthenticatedIdentity,
    db: AsyncSession,
) -> User:
    """Idempotently resolve an existing user or create a new one."""
    existing_user = await user_repository.find_user_auth_subject(user, db)
    if existing_user is not None:
        return existing_user

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
]
