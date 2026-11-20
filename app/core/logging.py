"""Logging configuration entry point."""

import logging


def configure_logging(level: str = "INFO") -> None:
    """Configure the application's base logger once at process startup."""
    logging.basicConfig(level=level.upper())
