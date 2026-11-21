"""ASGI request context, HTTP logging, and metrics middleware."""

import logging
import time
from uuid import uuid4

from starlette.datastructures import MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.core.logging import correlation_id_ctx, request_id_ctx
from app.core.metrics import HTTP_DURATION, HTTP_REQUESTS

logger = logging.getLogger("alibi.api")


class RequestContextMiddleware:
    """Attach trusted IDs, metrics, and response timing to each HTTP request."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request_id = str(uuid4())
        request_token = request_id_ctx.set(request_id)
        correlation_token = correlation_id_ctx.set(request_id)
        started = time.perf_counter()
        status_code = 500

        async def send_wrapper(message: Message) -> None:
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
                headers = MutableHeaders(scope=message)
                headers["X-Request-ID"] = request_id
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        except Exception:
            logger.exception("Unhandled request failure")
            raise
        finally:
            duration_ms = (time.perf_counter() - started) * 1000
            route = scope.get("route")
            route_path = getattr(route, "path", "unmatched")
            method = scope.get("method", "UNKNOWN")
            HTTP_REQUESTS.labels(
                method=method,
                route=route_path,
                status_code=str(status_code),
            ).inc()
            HTTP_DURATION.labels(method=method, route=route_path).observe(
                duration_ms / 1000
            )
            logger.info(
                "HTTP request completed",
                extra={"status_code": status_code, "duration_ms": duration_ms},
            )
            correlation_id_ctx.reset(correlation_token)
            request_id_ctx.reset(request_token)
