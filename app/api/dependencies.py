"""Dependencies shared across API versions and feature routers."""

from fastapi import Request


def get_request_id(request: Request) -> str | None:
    """Return a caller-provided request identifier when one is available."""
    return request.headers.get("X-Request-ID")
