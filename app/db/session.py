from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.db.observability import register_db_observability

engine = create_async_engine(
    settings.database_url,
    echo=settings.SQL_ECHO,
    future=True,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_timeout=settings.DB_POOL_TIMEOUT,
    pool_recycle=settings.DB_POOL_RECYCLE,
)
register_db_observability(engine)

AsyncSessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
)


async def get_db() -> AsyncIterator[AsyncSession]:
    """Provide an async database session for one request."""
    async with AsyncSessionLocal() as session:
        yield session


async def close_db() -> None:
    """Release database connections held by the SQLAlchemy engine."""
    await engine.dispose()
