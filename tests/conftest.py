"""Shared test fixtures for the backend test suite."""

from collections.abc import AsyncIterator

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient


@pytest.fixture
def app_module() -> FastAPI:
    """Provide the ASGI application for integration tests."""
    from app.main import app

    return app


@pytest.fixture
async def api_client() -> AsyncIterator[AsyncClient]:
    """Provide an HTTPX client backed directly by the ASGI application."""
    from app.main import create_app

    async with AsyncClient(
        transport=ASGITransport(app=create_app()),
        base_url="http://testserver",
    ) as client:
        yield client
