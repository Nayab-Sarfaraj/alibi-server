import pytest
from fastapi import HTTPException
from httpx import AsyncClient

from app.api.dependencies import AuthenticatedUser, get_current_user
from app.core.authorization import require_role


async def test_invalid_host_rejected(client: AsyncClient) -> None:
    response = await client.get(
        "/health/live",
        headers={"Host": "malicious.example"},
    )

    assert response.status_code == 400


async def test_request_body_limit_rejected(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/ping",
        content=b"x" * 1_048_577,
    )

    assert response.status_code == 413


async def test_authentication_fails_closed() -> None:
    with pytest.raises(HTTPException) as exception_info:
        await get_current_user(None)

    assert exception_info.value.status_code == 401
    assert exception_info.value.headers == {"WWW-Authenticate": "Bearer"}


async def test_authorization_rejects_disallowed_role() -> None:
    check_role = require_role({"admin"})

    with pytest.raises(HTTPException) as exception_info:
        await check_role(AuthenticatedUser(id="1", role="player"))

    assert exception_info.value.status_code == 403


async def test_auth_test_route_requires_token(client: AsyncClient) -> None:
    response = await client.get("/api/v1/auth/test")
    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "Bearer"

    root_response = await client.get("/auth/test")
    assert root_response.status_code == 401
    assert root_response.headers["WWW-Authenticate"] == "Bearer"


async def test_auth_test_route_rejects_invalid_token(client: AsyncClient) -> None:
    response = await client.get(
        "/api/v1/auth/test",
        headers={"Authorization": "Bearer invalid.token.value"},
    )
    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "Bearer"


async def test_auth_test_route_returns_503_when_jwks_unavailable(
    client: AsyncClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    from jwt import PyJWKClientConnectionError

    from app.api import dependencies

    class FailingJWKClient:
        def get_signing_key_from_jwt(self, token: str) -> None:
            raise PyJWKClientConnectionError("Connection timed out")

    monkeypatch.setattr(dependencies, "get_jwk_client", lambda: FailingJWKClient())

    response = await client.get(
        "/api/v1/auth/test",
        headers={
            "Authorization": (
                "Bearer eyJhbGciOiJFUzI1NiIsImtpZCI6InRlc3QifQ."
                "eyJzdWIiOiJ0ZXN0In0.c2lnbmF0dXJl"
            )
        },
    )
    assert response.status_code == 503
    assert (
        response.json()["error"]["message"]
        == "Authentication service temporarily unavailable"
    )
