"""Logging configuration entry point."""

import logging
import re


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


def configure_logging(level: str = "INFO", *, development: bool = False) -> None:
    """Configure the application's base logger once at process startup."""
    handler = logging.StreamHandler()
    handler.addFilter(SensitiveDataFilter())
    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s %(levelname)s %(name)s %(message)s"
            if development
            else "%(asctime)s %(levelname)s %(name)s %(message)s"
        )
    )
    logging.basicConfig(level=level.upper(), handlers=[handler], force=True)
