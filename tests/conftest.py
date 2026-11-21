from collections.abc import AsyncIterator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import Settings
from app.db.session import get_db
from app.main import app


@pytest.fixture(scope="session")
def test_settings() -> Settings:
    return Settings(
        APP_ENV="testing",
        APP_DEBUG=False,
    )


@pytest.fixture
async def db_session(
    test_settings: Settings,
) -> AsyncIterator[AsyncSession]:
    """Yield a session isolated from the development database and other tests."""
    url = (
        test_settings.TEST_DATABASE_URL.get_secret_value()
        if test_settings.TEST_DATABASE_URL is not None
        else None
    )

    if not url or not url.endswith("/alibi_test"):
        raise RuntimeError("A dedicated alibi_test database is required")

    engine = create_async_engine(url)

    try:
        async with engine.connect() as connection:
            transaction = await connection.begin()
            factory = async_sessionmaker(
                bind=connection,
                expire_on_commit=False,
                join_transaction_mode="create_savepoint",
            )
            async with factory() as session:
                yield session
            await transaction.rollback()
    finally:
        await engine.dispose()


@pytest.fixture
async def client(
    db_session: AsyncSession,
) -> AsyncIterator[AsyncClient]:
    async def override_get_db() -> AsyncIterator[AsyncSession]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://testserver",
        ) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
