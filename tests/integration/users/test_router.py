"""Integration checks for user provisioning through the public API."""

from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest
from httpx import AsyncClient
from jwt import PyJWKClientError
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import dependencies
from app.api.dependencies import AuthenticatedIdentity, get_current_user
from app.main import app
from app.modules.users import service as user_service
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


async def test_upgrade_route_requires_authentication(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/user/upgrade",
        json={"email": "detective@example.com"},
    )

    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "Bearer"


async def test_upgrade_route_requests_supabase_verification(
    client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    identity = AuthenticatedIdentity(
        auth_subject=uuid4(),
        is_guest=True,
        access_token="verified-jwt",
    )
    request_change = AsyncMock()
    app.dependency_overrides[get_current_user] = lambda: identity
    monkeypatch.setattr(user_service, "upgrade_user_email", request_change)

    try:
        response = await client.post(
            "/api/v1/user/upgrade",
            json={"email": "detective@example.com"},
        )
    finally:
        app.dependency_overrides.pop(get_current_user, None)

    assert response.status_code == 200
    assert response.json() == {"status": "verification_requested"}
    request_change.assert_awaited_once_with(identity, "detective@example.com")


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


async def test_me_synchronizes_an_upgraded_guest_identity(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    auth_subject = uuid4()
    guest_user = User(
        auth_subject=auth_subject,
        email=None,
        is_guest=True,
        display_name="DetectiveDodger",
        total_xp=0,
        credit_balance=0,
    )
    db_session.add(guest_user)
    await db_session.flush()
    identity = AuthenticatedIdentity(
        auth_subject=auth_subject,
        is_guest=False,
        email="detective@example.com",
    )
    app.dependency_overrides[get_current_user] = lambda: identity

    try:
        response = await client.get("/api/v1/users/me")
    finally:
        app.dependency_overrides.pop(get_current_user, None)

    await db_session.refresh(guest_user)
    assert response.status_code == 200
    assert response.json()["id"] == str(guest_user.id)
    assert guest_user.email == "detective@example.com"
    assert guest_user.is_guest is False


async def test_me_upgrade_preserves_existing_user_and_progression(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    auth_subject = uuid4()
    guest_user = User(
        auth_subject=auth_subject,
        email=None,
        is_guest=True,
        display_name="PersistentDetective",
        total_xp=1250,
        credit_balance=75,
    )
    db_session.add(guest_user)
    await db_session.flush()
    user_id = guest_user.id
    identity = AuthenticatedIdentity(
        auth_subject=auth_subject,
        is_guest=False,
        email="detective@example.com",
    )
    app.dependency_overrides[get_current_user] = lambda: identity

    try:
        first_response = await client.get("/api/v1/users/me")
        second_response = await client.get("/api/v1/users/me")
    finally:
        app.dependency_overrides.pop(get_current_user, None)

    await db_session.refresh(guest_user)
    assert first_response.status_code == 200
    assert second_response.status_code == 200
    assert first_response.json()["id"] == str(user_id)
    assert second_response.json()["id"] == str(user_id)
    assert guest_user.auth_subject == auth_subject
    assert guest_user.display_name == "PersistentDetective"
    assert guest_user.total_xp == 1250
    assert guest_user.credit_balance == 75


async def test_me_upgrade_does_not_overwrite_another_users_email(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    email = "taken@example.com"
    email_owner = User(auth_subject=uuid4(), email=email, is_guest=False)
    guest_user = User(auth_subject=uuid4(), email=None, is_guest=True)
    db_session.add_all([email_owner, guest_user])
    await db_session.flush()
    email_owner_id = email_owner.id
    guest_user_id = guest_user.id
    await db_session.commit()
    identity = AuthenticatedIdentity(
        auth_subject=guest_user.auth_subject,
        is_guest=False,
        email=email,
    )
    app.dependency_overrides[get_current_user] = lambda: identity

    try:
        response = await client.get("/api/v1/users/me")
    finally:
        app.dependency_overrides.pop(get_current_user, None)

    persisted_owner = await db_session.get(User, email_owner_id)
    persisted_guest = await db_session.get(User, guest_user_id)
    assert response.status_code == 409
    assert persisted_owner is not None
    assert persisted_guest is not None
    assert persisted_owner.email == email
    assert persisted_guest.email is None
    assert persisted_guest.is_guest is True


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
