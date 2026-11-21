"""Logging configuration entry point."""

import json
import logging
import re
import sys
from contextvars import ContextVar
from datetime import UTC, datetime

request_id_ctx: ContextVar[str | None] = ContextVar("request_id", default=None)

correlation_id_ctx: ContextVar[str | None] = ContextVar("correlation_id", default=None)


class JSONFormatter(logging.Formatter):
    """Render log records as JSON without serializing exception details."""

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": request_id_ctx.get(),
            "correlation_id": correlation_id_ctx.get(),
        }

        if record.exc_info:
            payload["exception_type"] = (
                record.exc_info[0].__name__ if record.exc_info[0] else "Unknown"
            )

        for field in ("status_code", "duration_ms"):
            value = getattr(record, field, None)
            if value is not None:
                payload[field] = value

        return json.dumps(payload, default=str)


class SensitiveDataFilter(logging.Filter):
    """Prevent common secret formats from appearing in application logs."""

    _database_password = re.compile(r"(://[^:\s]+:)[^@\s]+(@)")
    _secret_assignment = re.compile(
        r"(?i)(secret(?:_key)?|password|token)\s*[=:]\s*[^\s,]+"
    )

    def filter(self, record: logging.LogRecord) -> bool:
        message = record.getMessage()
        message = self._database_password.sub(r"\1***\2", message)
        record.msg = self._secret_assignment.sub(r"\1=***", message)
        record.args = ()
        return True


def configure_logging(level: str = "INFO") -> None:
    """Configure the application's base logger once at process startup."""
    handler = logging.StreamHandler(sys.stdout)
    handler._alibi_logging_handler = True  # type: ignore[attr-defined]
    handler.addFilter(SensitiveDataFilter())
    handler.setFormatter(JSONFormatter())

    root = logging.getLogger()
    root.handlers[:] = [
        existing_handler
        for existing_handler in root.handlers
        if not getattr(existing_handler, "_alibi_logging_handler", False)
    ]
    root.addHandler(handler)
    root.setLevel(level.upper())

    # Never emit SQL text or bound parameters through application logs.
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
