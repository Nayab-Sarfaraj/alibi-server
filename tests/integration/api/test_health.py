from unittest.mock import AsyncMock

import pytest
from httpx import AsyncClient

from app.api import health


async def test_liveness(client: AsyncClient) -> None:
    response = await client.get("/health/live")

    assert response.status_code == 200
    assert response.json() == {"status": "alive"}


async def test_readiness(monkeypatch: pytest.MonkeyPatch, client: AsyncClient) -> None:
    monkeypatch.setattr(health, "check_database", AsyncMock())
    monkeypatch.setattr(health, "check_cache", AsyncMock())

    response = await client.get("/health/ready")

    assert response.status_code == 200


async def test_readiness_returns_service_unavailable_when_dependency_fails(
    monkeypatch: pytest.MonkeyPatch,
    client: AsyncClient,
) -> None:
    async def unavailable() -> None:
        raise ConnectionError("database unavailable")

    monkeypatch.setattr(health, "check_database", unavailable)

    response = await client.get("/health/ready")

    assert response.status_code == 503
    assert response.json()["error"]["code"] == "HTTP_ERROR"
