from redis.asyncio import Redis

from app.core.config import settings


def create_redis_client() -> Redis:
    return Redis.from_url(
        settings.REDIS_URL.get_secret_value(),
        decode_responses=True,
        max_connections=settings.REDIS_MAX_CONNECTIONS,
        socket_connect_timeout=settings.REDIS_SOCKET_TIMEOUT,
        socket_timeout=settings.REDIS_SOCKET_TIMEOUT,
        health_check_interval=30,
    )


async def check_redis(client: Redis) -> bool:
    return bool(await client.ping())
