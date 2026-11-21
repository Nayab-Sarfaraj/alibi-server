"""Integration checks for user provisioning through the public API."""

from unittest.mock import Mock
from uuid import uuid4

import pytest
from httpx import AsyncClient
from jwt import PyJWKClientError
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import dependencies
from app.api.dependencies import AuthenticatedIdentity, get_current_user
from app.main import app
from app.modules.users.models import User


def test_users_router_is_registered() -> None:
    from app.api.v1.router import router as v1_router
    from app.modules.users.router import router as users_router

    assert any(
        getattr(route, "original_router", None) is users_router
        for route in v1_router.routes
    )


async def test_users_me_requires_authentication(client: AsyncClient) -> None:
    response = await client.get("/api/v1/users/me")
    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "Bearer"

    post_response = await client.post("/api/v1/users/me")
    assert post_response.status_code == 401
    assert post_response.headers["WWW-Authenticate"] == "Bearer"


async def test_first_and_repeat_request_provision_one_user(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    identity = AuthenticatedIdentity(
        auth_subject=uuid4(),
        is_guest=False,
        email="detective@example.com",
    )
    app.dependency_overrides[get_current_user] = lambda: identity

    try:
        first_response = await client.get("/api/v1/users/me")
        second_response = await client.get("/api/v1/users/me")
    finally:
        app.dependency_overrides.pop(get_current_user, None)

    assert first_response.status_code == 200
    assert second_response.status_code == 200
    assert first_response.json()["id"] == second_response.json()["id"]
    assert "auth_subject" not in first_response.json()

    count = await db_session.scalar(
        select(func.count())
        .select_from(User)
        .where(User.auth_subject == identity.auth_subject)
    )
    assert count == 1


async def test_guest_identity_provisions_guest_user(
    client: AsyncClient,
) -> None:
    identity = AuthenticatedIdentity(auth_subject=uuid4(), is_guest=True)
    app.dependency_overrides[get_current_user] = lambda: identity

    try:
        response = await client.get("/api/v1/users/me")
    finally:
        app.dependency_overrides.pop(get_current_user, None)

    assert response.status_code == 200
    assert response.json()["is_guest"] is True


async def test_different_identities_receive_different_users(
    client: AsyncClient,
) -> None:
    first_identity = AuthenticatedIdentity(auth_subject=uuid4(), is_guest=False)
    second_identity = AuthenticatedIdentity(auth_subject=uuid4(), is_guest=False)

    app.dependency_overrides[get_current_user] = lambda: first_identity
    try:
        first_response = await client.get("/api/v1/users/me")
        app.dependency_overrides[get_current_user] = lambda: second_identity
        second_response = await client.get("/api/v1/users/me")
    finally:
        app.dependency_overrides.pop(get_current_user, None)

    assert first_response.status_code == 200
    assert second_response.status_code == 200
    assert first_response.json()["id"] != second_response.json()["id"]


async def test_invalid_jwt_does_not_create_user(
    client: AsyncClient,
    db_session: AsyncSession,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    jwk_client = Mock()
    jwk_client.get_signing_key_from_jwt.side_effect = PyJWKClientError("invalid")
    monkeypatch.setattr(dependencies, "get_jwk_client", lambda: jwk_client)
    before_count = await db_session.scalar(select(func.count()).select_from(User))

    response = await client.get(
        "/api/v1/users/me",
        headers={"Authorization": "Bearer invalid.jwt.token"},
    )

    after_count = await db_session.scalar(select(func.count()).select_from(User))
    assert response.status_code == 401
    assert after_count == before_count
