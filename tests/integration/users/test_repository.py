"""Integration checks for user persistence wiring."""

from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import AuthenticatedIdentity
from app.modules.users.repository import create_user


def test_users_repository_module_imports() -> None:
    from app.modules.users import repository

    assert repository is not None


async def test_create_user_normalizes_empty_emails_to_null(
    db_session: AsyncSession,
) -> None:
    first = await create_user(
        AuthenticatedIdentity(auth_subject=uuid4(), is_guest=True, email=""),
        db_session,
    )
    second = await create_user(
        AuthenticatedIdentity(auth_subject=uuid4(), is_guest=True, email=""),
        db_session,
    )

    assert first is not None
    assert second is not None
    assert first.id != second.id
    assert first.email is None
    assert second.email is None
