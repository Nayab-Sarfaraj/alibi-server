"""User request and response schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, field_validator


class UserUpgradeRequest(BaseModel):
    """Email requested when an anonymous account is upgraded."""

    email: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        email = value.strip().lower()
        if len(email) > 255 or email.count("@") != 1:
            raise ValueError("A valid email address is required")
        local_part, domain = email.rsplit("@", maxsplit=1)
        if not local_part or "." not in domain or domain.startswith("."):
            raise ValueError("A valid email address is required")
        return email


class UserUpgradeResponse(BaseModel):
    """Acknowledgement that Supabase accepted the email-change request."""

    status: str = "verification_requested"


class VerifyEmailRequest(UserUpgradeRequest):
    """Supabase email-change OTP supplied after the user receives the email."""

    otp: str

    @field_validator("otp")
    @classmethod
    def validate_otp(cls, value: str) -> str:
        otp = value.strip()
        if not otp:
            raise ValueError("An OTP is required")
        return otp


class AuthSessionResponse(BaseModel):
    """Session credentials issued by Supabase after OTP verification."""

    access_token: str | None = None
    refresh_token: str | None = None
    token_type: str | None = None
    expires_in: int | None = None
    expires_at: int | None = None


class SetPasswordRequest(BaseModel):
    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if len(value) < 12:
            raise ValueError("Password must contain at least 12 characters")
        return value


class UserResponse(BaseModel):
    """Public user identity and profile schema."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str | None = None
    display_name: str
    avatar_url: str | None = None
    is_guest: bool
    total_xp: int
    credit_balance: int
    current_rank_id: UUID | None = None
    created_at: datetime
    updated_at: datetime


__all__ = [
    "AuthSessionResponse",
    "SetPasswordRequest",
    "UserResponse",
    "UserUpgradeRequest",
    "UserUpgradeResponse",
    "VerifyEmailRequest",
]
