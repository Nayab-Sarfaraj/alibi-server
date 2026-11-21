from fastapi import APIRouter, HTTPException, Request
from sqlalchemy import text

from app.db.session import engine
from app.infrastructure.cache.redis_client import check_redis, create_redis_client

router = APIRouter(tags=["Health"])


@router.get("/health/live")
async def liveness() -> dict[str, str]:
    return {"status": "alive"}


async def check_database() -> None:
    async with engine.connect() as connection:
        await connection.execute(text("SELECT 1"))


async def check_cache(request: Request) -> None:
    redis_client = getattr(request.app.state, "redis", None)
    owns_client = redis_client is None
    if redis_client is None:
        redis_client = create_redis_client()
    try:
        await check_redis(redis_client)
    finally:
        if owns_client:
            await redis_client.aclose()


@router.get("/health/ready")
async def readiness(request: Request) -> dict[str, str]:
    try:
        await check_database()
        await check_cache(request)
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Dependencies unavailable") from exc
    return {"status": "ready"}
