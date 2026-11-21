from httpx import AsyncClient


async def test_versioned_route(client: AsyncClient) -> None:
    response = await client.get("/api/v1/ping")

    assert response.status_code == 200
    assert response.json() == {"message": "pong"}
