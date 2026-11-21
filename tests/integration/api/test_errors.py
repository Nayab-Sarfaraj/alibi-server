from httpx import AsyncClient


async def test_not_found(client: AsyncClient) -> None:
    response = await client.get("/invalid-route")

    assert response.status_code == 404
    assert "error" in response.json()
