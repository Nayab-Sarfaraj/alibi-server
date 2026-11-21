import json
from typing import Any

from redis.asyncio import Redis


class CacheService:
    def __init__(self, client: Redis, environment: str) -> None:
        self.client = client
        self.environment = environment

    def key(self, namespace: str, identifier: str) -> str:
        return f"alibi:{self.environment}:{namespace}:{identifier}"

    async def get(self, namespace: str, identifier: str) -> Any | None:
        value = await self.client.get(
            self.key(namespace=namespace, identifier=identifier)
        )
        return json.loads(value) if value is not None else None

    async def set(
        self,
        namespace: str,
        identifier: str,
        value: Any,
        ttl: int = 300,
    ) -> None:
        if ttl <= 0:
            raise ValueError("Cache TTL must be positive")

        await self.client.set(
            self.key(namespace, identifier),
            json.dumps(value),
            ex=ttl,
        )

    async def delete(
        self,
        namespace: str,
        identifier: str,
    ) -> None:
        await self.client.delete(self.key(namespace, identifier))
