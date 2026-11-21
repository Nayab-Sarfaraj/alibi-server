from datetime import UTC, datetime
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.modules.users.models import User
from app.modules.users.schemas import UserProfileUpdate, UserResponse


def test_user_response_does_not_expose_auth_subject() -> None:
    user = User(
        id=uuid4(),
        auth_subject=uuid4(),
        email="detective@example.com",
        display_name="DetectiveDodger",
        is_guest=False,
        total_xp=0,
        credit_balance=0,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    profile = UserResponse.model_validate(user)

    assert "auth_subject" not in profile.model_dump()


def test_profile_update_allows_only_explicit_profile_fields() -> None:
    update = UserProfileUpdate(
        display_name="  Detective Dodger  ",
        avatar_url="https://cdn.example.com/avatar.png",
    )

    assert update.changes() == {
        "display_name": "Detective Dodger",
        "avatar_url": "https://cdn.example.com/avatar.png",
    }


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"display_name": ""},
        {"display_name": "x" * 101},
        {"avatar_url": "ftp://cdn.example.com/avatar.png"},
        {"avatar_url": "https://example.com/" + "x" * 500},
        {"email": "not-allowed@example.com"},
        {"auth_subject": str(uuid4())},
        {"total_xp": 9999},
        {"credit_balance": 9999},
        {"is_guest": False},
        {"user_id": str(uuid4())},
    ],
)
def test_profile_update_rejects_empty_invalid_and_protected_fields(
    payload: dict[str, object],
) -> None:
    with pytest.raises(ValidationError):
        UserProfileUpdate.model_validate(payload)
