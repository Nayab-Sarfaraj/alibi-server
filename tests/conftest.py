"""Shared test fixtures for the backend test suite."""

import pytest


@pytest.fixture
def app_module():
    """Provide the ASGI application for integration tests."""
    from app.main import app

    return app
