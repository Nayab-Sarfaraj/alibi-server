"""Unit tests for user application services."""

from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest

from app.api.dependencies import AuthenticatedIdentity
from app.core.exceptions import AppException, ConflictError, NotFoundError
from app.modules.users import service
from app.modules.users.models import User


def test_users_service_module_imports() -> None:
    assert service is not None


@pytest.mark.asyncio
async def test_get_or_create_user_returns_existing() -> None:
    auth_identity = AuthenticatedIdentity(
        auth_subject=uuid4(),
        is_guest=False,
        email="detective@example.com",
    )
    mock_user = User(
        id=uuid4(),
        auth_subject=auth_identity.auth_subject,
        email=auth_identity.email,
        is_guest=False,
        display_name="DetectiveDodger",
    )
    mock_db = AsyncMock()

    with patch(
        "app.modules.users.repository.find_user_auth_subject",
        return_value=mock_user,
    ):
        result = await service.get_or_create_user(auth_identity, mock_db)
        assert result == mock_user


@pytest.mark.asyncio
async def test_get_or_create_user_synchronizes_upgraded_guest_identity() -> None:
    identity = AuthenticatedIdentity(
        auth_subject=uuid4(),
        is_guest=False,
        email="detective@example.com",
    )
    guest_user = User(
        id=uuid4(),
        auth_subject=identity.auth_subject,
        email=None,
        is_guest=True,
    )
    synchronized_user = User(
        id=guest_user.id,
        auth_subject=identity.auth_subject,
        email=identity.email,
        is_guest=False,
    )
    mock_db = AsyncMock()

    with (
        patch(
            "app.modules.users.repository.find_user_auth_subject",
            return_value=guest_user,
        ),
        patch(
            "app.modules.users.repository.synchronize_guest_identity",
            return_value=synchronized_user,
        ) as synchronize_identity,
    ):
        result = await service.get_or_create_user(identity, mock_db)

    assert result == synchronized_user
    synchronize_identity.assert_awaited_once_with(guest_user, identity, mock_db)


@pytest.mark.asyncio
async def test_get_or_create_user_creates_new_when_missing() -> None:
    auth_identity = AuthenticatedIdentity(
        auth_subject=uuid4(),
        is_guest=True,
        email=None,
    )
    created_user = User(
        id=uuid4(),
        auth_subject=auth_identity.auth_subject,
        email=None,
        is_guest=True,
        display_name="Detective",
    )
    mock_db = AsyncMock()

    with (
        patch(
            "app.modules.users.repository.find_user_auth_subject",
            return_value=None,
        ),
        patch(
            "app.modules.users.repository.create_user",
            return_value=created_user,
        ),
    ):
        result = await service.get_or_create_user(auth_identity, mock_db)
        assert result == created_user


@pytest.mark.asyncio
async def test_get_or_create_user_returns_concurrently_created_user() -> None:
    auth_identity = AuthenticatedIdentity(
        auth_subject=uuid4(),
        is_guest=False,
        email="detective@example.com",
    )
    concurrent_user = User(
        id=uuid4(),
        auth_subject=auth_identity.auth_subject,
        email=auth_identity.email,
        is_guest=False,
        display_name="DetectiveDodger",
    )
    mock_db = AsyncMock()

    with (
        patch(
            "app.modules.users.repository.find_user_auth_subject",
            side_effect=[None, concurrent_user],
        ),
        patch(
            "app.modules.users.repository.create_user",
            return_value=None,
        ),
    ):
        result = await service.get_or_create_user(auth_identity, mock_db)

    assert result == concurrent_user


@pytest.mark.asyncio
async def test_get_user_by_id_raises_not_found() -> None:
    mock_db = AsyncMock()
    missing_id = uuid4()

    with patch(
        "app.modules.users.repository.get_user_by_id",
        return_value=None,
    ):
        with pytest.raises(NotFoundError) as exc_info:
            await service.get_user_by_id(missing_id, mock_db)

        assert exc_info.value.status_code == 404
        assert exc_info.value.code == "USER_NOT_FOUND"


@pytest.mark.asyncio
async def test_upgrade_user_email_updates_profile_and_requests_verification() -> None:
    identity = AuthenticatedIdentity(
        auth_subject=uuid4(),
        is_guest=True,
        access_token="verified-jwt",
    )
    with patch(
        "app.modules.users.service.request_supabase_email_change",
        new_callable=AsyncMock,
    ) as request_change:
        await service.upgrade_user_email(identity, "detective@example.com")

    request_change.assert_awaited_once_with("verified-jwt", "detective@example.com")


@pytest.mark.asyncio
async def test_upgrade_user_email_rejects_non_guest_identity() -> None:
    identity = AuthenticatedIdentity(auth_subject=uuid4(), is_guest=False)

    with patch(
        "app.modules.users.service.request_supabase_email_change",
        new_callable=AsyncMock,
    ) as request_change:
        with pytest.raises(AppException) as exc_info:
            await service.upgrade_user_email(identity, "detective@example.com")

    assert exc_info.value.status_code == 403
    assert exc_info.value.code == "GUEST_IDENTITY_REQUIRED"
    request_change.assert_not_awaited()


@pytest.mark.asyncio
async def test_supabase_email_change_uses_authenticated_rest_request(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class Response:
        is_success = True

        def json(self) -> dict[str, str]:
            return {}

    class Client:
        captured_request: dict[str, object] = {}

        async def __aenter__(self) -> "Client":
            return self

        async def __aexit__(self, *args: object) -> None:
            return None

        async def request(self, method: str, url: str, **kwargs: object) -> Response:
            self.captured_request = {"method": method, "url": url, **kwargs}
            return Response()

    client = Client()
    monkeypatch.setattr(service.settings, "SUPABASE_URL", "https://project.supabase.co")
    monkeypatch.setattr(service.settings, "SUPABASE_PUBLISHABLE_KEY", "publishable-key")
    monkeypatch.setattr(service.httpx, "AsyncClient", lambda **_: client)

    await service.request_supabase_email_change("verified-jwt", "detective@example.com")

    assert client.captured_request == {
        "method": "PUT",
        "url": "https://project.supabase.co/auth/v1/user",
        "headers": {
            "apikey": "publishable-key",
            "Authorization": "Bearer verified-jwt",
        },
        "json": {"email": "detective@example.com"},
    }


@pytest.mark.asyncio
async def test_supabase_email_change_maps_conflict_response(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class Response:
        is_success = False
        status_code = 409

        def json(self) -> dict[str, str]:
            return {"code": "email_exists"}

    class Client:
        async def __aenter__(self) -> "Client":
            return self

        async def __aexit__(self, *args: object) -> None:
            return None

        async def request(self, *args: object, **kwargs: object) -> Response:
            return Response()

    monkeypatch.setattr(service.settings, "SUPABASE_URL", "https://project.supabase.co")
    monkeypatch.setattr(service.settings, "SUPABASE_PUBLISHABLE_KEY", "publishable-key")
    monkeypatch.setattr(service.httpx, "AsyncClient", lambda **_: Client())

    with pytest.raises(ConflictError) as exc_info:
        await service.request_supabase_email_change("verified-jwt", "taken@example.com")

    assert exc_info.value.status_code == 409
    assert exc_info.value.code == "SUPABASE_EMAIL_CONFLICT"


@pytest.mark.asyncio
async def test_verify_email_returns_supabase_session_for_same_identity() -> None:
    identity = AuthenticatedIdentity(
        auth_subject=uuid4(),
        is_guest=True,
        access_token="guest-access-token",
    )
    session = {
        "access_token": "new-access-token",
        "refresh_token": "new-refresh-token",
        "user": {"id": str(identity.auth_subject)},
    }

    with patch(
        "app.modules.users.service._supabase_request",
        new_callable=AsyncMock,
        return_value=session,
    ) as request:
        result = await service.verify_supabase_email_change(
            identity, "detective@example.com", "123456"
        )

    assert result is session
    request.assert_awaited_once_with(
        "POST",
        "/auth/v1/verify",
        "guest-access-token",
        {"email": "detective@example.com", "token": "123456", "type": "email_change"},
    )


@pytest.mark.asyncio
async def test_verify_email_rejects_a_session_for_another_subject() -> None:
    identity = AuthenticatedIdentity(
        auth_subject=uuid4(), is_guest=True, access_token="guest-access-token"
    )

    with patch(
        "app.modules.users.service._supabase_request",
        new_callable=AsyncMock,
        return_value={"user": {"id": str(uuid4())}},
    ):
        with pytest.raises(AppException) as exc_info:
            await service.verify_supabase_email_change(
                identity, "detective@example.com", "123456"
            )

    assert exc_info.value.status_code == 403
    assert exc_info.value.code == "SUPABASE_IDENTITY_MISMATCH"


@pytest.mark.asyncio
async def test_verify_email_maps_rejected_or_expired_otp_to_bad_request() -> None:
    identity = AuthenticatedIdentity(
        auth_subject=uuid4(), is_guest=True, access_token="guest-access-token"
    )

    with patch(
        "app.modules.users.service._supabase_request",
        new_callable=AsyncMock,
        side_effect=AppException(
            status_code=400,
            code="SUPABASE_INVALID_REQUEST",
            message="Supabase rejected the request",
        ),
    ):
        with pytest.raises(AppException) as exc_info:
            await service.verify_supabase_email_change(
                identity, "detective@example.com", "expired-otp"
            )

    assert exc_info.value.status_code == 400
    assert exc_info.value.code == "SUPABASE_INVALID_REQUEST"


@pytest.mark.asyncio
async def test_set_password_only_after_supabase_confirms_email() -> None:
    identity = AuthenticatedIdentity(
        auth_subject=uuid4(), is_guest=False, access_token="access-token"
    )

    with patch(
        "app.modules.users.service._supabase_request",
        new_callable=AsyncMock,
        side_effect=[{"email_confirmed_at": "2026-01-01T00:00:00Z"}, {}],
    ) as request:
        await service.set_supabase_password(identity, "a-secure-password")

    assert request.await_args_list[0].args == ("GET", "/auth/v1/user", "access-token")
    assert request.await_args_list[1].args == (
        "PUT",
        "/auth/v1/user",
        "access-token",
        {"password": "a-secure-password"},
    )


@pytest.mark.asyncio
async def test_set_password_rejects_unverified_email() -> None:
    identity = AuthenticatedIdentity(
        auth_subject=uuid4(), is_guest=False, access_token="access-token"
    )

    with patch(
        "app.modules.users.service._supabase_request",
        new_callable=AsyncMock,
        return_value={"email_confirmed_at": None},
    ) as request:
        with pytest.raises(AppException) as exc_info:
            await service.set_supabase_password(identity, "a-secure-password")

    assert exc_info.value.status_code == 403
    assert exc_info.value.code == "EMAIL_NOT_VERIFIED"
    request.assert_awaited_once_with("GET", "/auth/v1/user", "access-token")


@pytest.mark.asyncio
async def test_create_new_user_raises_conflict_if_exists() -> None:
    auth_identity = AuthenticatedIdentity(
        auth_subject=uuid4(),
        is_guest=False,
        email="existing@example.com",
    )
    existing_user = User(
        id=uuid4(),
        auth_subject=auth_identity.auth_subject,
    )
    mock_db = AsyncMock()

    with patch(
        "app.modules.users.repository.find_user_auth_subject",
        return_value=existing_user,
    ):
        with pytest.raises(ConflictError) as exc_info:
            await service.create_new_user(auth_identity, mock_db)

        assert exc_info.value.status_code == 409
        assert exc_info.value.code == "USER_ALREADY_EXISTS"
