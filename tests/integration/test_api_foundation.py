from httpx import AsyncClient


async def test_liveness(api_client: AsyncClient) -> None:
    response = await api_client.get("/health/live")

    assert response.status_code == 200
    assert response.json() == {"status": "alive"}


async def test_readiness(api_client: AsyncClient) -> None:
    response = await api_client.get("/health/ready")

    assert response.status_code == 200


async def test_versioned_route(api_client: AsyncClient) -> None:
    response = await api_client.get("/api/v1/ping")

    assert response.status_code == 200
    assert response.json() == {"message": "pong"}


async def test_not_found(api_client: AsyncClient) -> None:
    response = await api_client.get("/invalid-route")

    assert response.status_code == 404
    assert "error" in response.json()
