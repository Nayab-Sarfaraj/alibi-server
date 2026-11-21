from typing import cast

import pytest
from redis.asyncio import Redis

from app.infrastructure.cache.redis_client import (
    create_redis_client,
)
from app.infrastructure.cache.service import CacheService


@pytest.mark.asyncio
async def test_redis_connection() -> None:
    client = create_redis_client()

    try:
        assert await client.ping()
    finally:
        await client.aclose()


@pytest.mark.asyncio
async def test_cache_set_get_delete() -> None:
    client = create_redis_client()

    try:
        cache = CacheService(client, "testing")

        await cache.set(
            "test",
            "example",
            {"message": "hello"},
            ttl=60,
        )

        result = await cache.get("test", "example")
        assert result == {"message": "hello"}

        await cache.delete("test", "example")

        result = await cache.get("test", "example")
        assert result is None

    finally:
        await client.aclose()


def test_cache_key_components_cannot_collide() -> None:
    cache = CacheService(cast(Redis, None), "testing")

    assert cache.key("user:profile", "42") != cache.key("user", "profile:42")
