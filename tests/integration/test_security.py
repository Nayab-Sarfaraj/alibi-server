import pytest
from fastapi import HTTPException
from httpx import AsyncClient

from app.api.dependencies import AuthenticatedUser, get_current_user
from app.core.authorization import require_role


async def test_invalid_host_rejected(api_client: AsyncClient) -> None:
    response = await api_client.get(
        "/health/live",
        headers={"Host": "malicious.example"},
    )

    assert response.status_code == 400


async def test_request_body_limit_rejected(api_client: AsyncClient) -> None:
    response = await api_client.post(
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
