import logging
from collections.abc import Mapping
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.logging import correlation_id_ctx, request_id_ctx

logger = logging.getLogger(__name__)


def error_response(
    status_code: int,
    code: str,
    message: str,
    details: Any = None,
    headers: Mapping[str, str] | None = None,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": code,
                "message": message,
                "details": details,
            }
        },
        headers=headers,
    )


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        return error_response(
            exc.status_code,
            "HTTP_ERROR",
            str(exc.detail),
            headers=exc.headers,
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        return error_response(
            422,
            "VALIDATION_ERROR",
            "Invalid request data",
            [
                {
                    "loc": list(error["loc"]),
                    "type": error["type"],
                }
                for error in exc.errors()
            ],
        )

    @app.exception_handler(Exception)
    async def internal_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        request_id = getattr(request.state, "request_id", None)
        request_token = request_id_ctx.set(request_id)
        correlation_token = correlation_id_ctx.set(request_id)
        try:
            logger.exception("Unhandled API exception")
        finally:
            correlation_id_ctx.reset(correlation_token)
            request_id_ctx.reset(request_token)
        return error_response(
            500,
            "INTERNAL_SERVER_ERROR",
            "An unexpected error occurred",
            headers={"X-Request-ID": request_id} if request_id else None,
        )
