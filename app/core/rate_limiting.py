"""Rate-limiting interfaces for a future Redis-backed implementation."""

from typing import Protocol


class RateLimiter(Protocol):
    """Contract implemented by a concrete rate limiter."""

    async def allow(
        self,
        key: str,
        limit: int,
        window_seconds: int,
    ) -> bool:
        """Return True when a request is permitted."""
        ...
