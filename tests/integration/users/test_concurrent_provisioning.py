"""PostgreSQL concurrency coverage for user provisioning."""

import asyncio
from uuid import uuid4

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.api.dependencies import AuthenticatedIdentity
from app.core.config import Settings
from app.modules.users import service
from app.modules.users.models import User


async def test_concurrent_first_requests_create_one_user(
    test_settings: Settings,
) -> None:
    url = test_settings.database_url
    engine = create_async_engine(url)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    identity = AuthenticatedIdentity(auth_subject=uuid4(), is_guest=False)

    async def provision() -> User:
        async with session_factory() as session:
            return await service.get_or_create_user(identity, session)

    try:
        first_user, second_user = await asyncio.gather(provision(), provision())

        async with session_factory() as session:
            count = await session.scalar(
                select(func.count())
                .select_from(User)
                .where(User.auth_subject == identity.auth_subject)
            )

        assert first_user.id == second_user.id
        assert count == 1
    finally:
        async with engine.begin() as connection:
            await connection.execute(
                delete(User).where(User.auth_subject == identity.auth_subject)
            )
        await engine.dispose()
