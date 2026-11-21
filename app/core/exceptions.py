import logging
from collections.abc import Mapping
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.logging import correlation_id_ctx, request_id_ctx

logger = logging.getLogger(__name__)


class AppException(StarletteHTTPException):
    """Base application exception with structured error code and details."""

    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        details: Any = None,
        headers: Mapping[str, str] | None = None,
    ) -> None:
        super().__init__(status_code=status_code, detail=message, headers=headers)
        self.code = code
        self.details = details


class NotFoundError(AppException):
    def __init__(
        self,
        message: str = "Resource not found",
        code: str = "NOT_FOUND",
        details: Any = None,
        headers: Mapping[str, str] | None = None,
    ) -> None:
        super().__init__(
            status_code=404,
            code=code,
            message=message,
            details=details,
            headers=headers,
        )


class ConflictError(AppException):
    def __init__(
        self,
        message: str = "Resource conflict",
        code: str = "CONFLICT",
        details: Any = None,
        headers: Mapping[str, str] | None = None,
    ) -> None:
        super().__init__(
            status_code=409,
            code=code,
            message=message,
            details=details,
            headers=headers,
        )


class BadRequestError(AppException):
    def __init__(
        self,
        message: str = "Bad request",
        code: str = "BAD_REQUEST",
        details: Any = None,
        headers: Mapping[str, str] | None = None,
    ) -> None:
        super().__init__(
            status_code=400,
            code=code,
            message=message,
            details=details,
            headers=headers,
        )


class DatabaseError(AppException):
    def __init__(
        self,
        message: str = "Database operation failed",
        code: str = "DATABASE_ERROR",
        details: Any = None,
        headers: Mapping[str, str] | None = None,
    ) -> None:
        super().__init__(
            status_code=500,
            code=code,
            message=message,
            details=details,
            headers=headers,
        )


class ExternalServiceError(AppException):
    def __init__(
        self,
        message: str = "An external service request failed",
        code: str = "EXTERNAL_SERVICE_ERROR",
    ) -> None:
        super().__init__(status_code=503, code=code, message=message)


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
        code = getattr(exc, "code", "HTTP_ERROR")
        details = getattr(exc, "details", None)
        return error_response(
            exc.status_code,
            code,
            str(exc.detail),
            details=details,
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
