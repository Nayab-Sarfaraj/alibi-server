import pytest
from sqlalchemy import text

from app.db.session import AsyncSessionLocal


@pytest.mark.asyncio
async def test_database_connection() -> None:
    async with AsyncSessionLocal() as session:
        result = await session.execute(text("SELECT 1"))
        assert result.scalar_one() == 1


@pytest.mark.asyncio
async def test_transaction_rollback() -> None:
    async with AsyncSessionLocal() as session:
        with pytest.raises(ValueError):
            async with session.begin():
                await session.execute(text("SELECT 1"))
                raise ValueError("Simulated failure")

        assert not session.in_transaction()
