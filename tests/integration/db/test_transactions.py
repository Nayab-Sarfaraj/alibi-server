import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_database_connection(db_session: AsyncSession) -> None:
    result = await db_session.execute(text("SELECT 1"))
    assert result.scalar_one() == 1


@pytest.mark.asyncio
async def test_transaction_rollback(db_session: AsyncSession) -> None:
    with pytest.raises(ValueError):
        async with db_session.begin():
            await db_session.execute(text("SELECT 1"))
            raise ValueError("Simulated failure")

    assert not db_session.in_transaction()
