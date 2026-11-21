"""User request and response schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


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


__all__ = ["UserResponse"]
