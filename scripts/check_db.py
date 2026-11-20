import asyncio

from sqlalchemy import text

from app.db.session import engine


async def main() -> None:
    try:
        async with engine.connect() as connection:
            result = await connection.execute(text("SELECT 1"))
            assert result.scalar_one() == 1
            print("PostgreSQL connection successful")
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
