"""User request and response schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, field_validator, model_validator


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


class UserProfileUpdate(BaseModel):
    """The only profile fields an authenticated user may edit."""

    model_config = ConfigDict(extra="forbid")

    display_name: str | None = None
    avatar_url: str | None = None

    @model_validator(mode="after")
    def require_update(self) -> "UserProfileUpdate":
        if not self.model_fields_set:
            raise ValueError("Provide at least one profile field")
        if "display_name" in self.model_fields_set and self.display_name is None:
            raise ValueError("Display name cannot be null")
        return self

    @field_validator("display_name")
    @classmethod
    def validate_display_name(cls, value: str | None) -> str | None:
        if value is None:
            return value
        display_name = value.strip()
        if not display_name or len(display_name) > 100:
            raise ValueError("Display name must be between 1 and 100 characters")
        return display_name

    @field_validator("avatar_url")
    @classmethod
    def validate_avatar_url(cls, value: str | None) -> str | None:
        if value is None:
            return value
        avatar_url = value.strip()
        if len(avatar_url) > 500 or not avatar_url.startswith(("https://", "http://")):
            raise ValueError("Avatar URL must be an HTTP(S) URL up to 500 characters")
        return avatar_url

    def changes(self) -> dict[str, str | None]:
        """Return only fields explicitly supplied by the authenticated caller."""
        return {field: getattr(self, field) for field in self.model_fields_set}


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
    "UserProfileUpdate",
    "UserResponse",
    "UserUpgradeRequest",
    "UserUpgradeResponse",
    "VerifyEmailRequest",
]
