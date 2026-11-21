from datetime import UTC, datetime
from uuid import uuid4

from app.modules.users.models import User
from app.modules.users.schemas import UserResponse


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
