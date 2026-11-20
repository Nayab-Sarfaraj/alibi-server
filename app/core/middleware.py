"""Security middleware registration."""

from fastapi import FastAPI
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.body_limit import RequestBodyLimitMiddleware


def register_security_middleware(
    app: FastAPI,
    trusted_hosts: list[str],
    max_body_bytes: int,
) -> None:
    """Install host-header validation and streaming request-size limits."""
    app.add_middleware(
        RequestBodyLimitMiddleware,
        max_body_size=max_body_bytes,
    )
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=trusted_hosts,
        www_redirect=False,
    )
