"""Unit tests for user application services."""

from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest

from app.api.dependencies import AuthenticatedIdentity
from app.core.exceptions import ConflictError, NotFoundError
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
