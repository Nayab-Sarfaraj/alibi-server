"""User API routes belong here as the feature is expanded."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import CurrentUser
from app.db.session import get_db
from app.modules.users import service as user_service
from app.modules.users.schemas import (
    AuthSessionResponse,
    SetPasswordRequest,
    UserResponse,
    UserUpgradeRequest,
    UserUpgradeResponse,
    VerifyEmailRequest,
)

router = APIRouter()
upgrade_router = APIRouter()
auth_router = APIRouter()


@router.post("/me", response_model=UserResponse)
@router.get("/me", response_model=UserResponse)
async def get_or_create_user(
    user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserResponse:
    """Resolve or create application user from authenticated identity."""
    db_user = await user_service.get_or_create_user(user, db)
    return UserResponse.model_validate(db_user)


@upgrade_router.post("/upgrade", response_model=UserUpgradeResponse)
async def upgrade_user(
    payload: UserUpgradeRequest,
    user: CurrentUser,
) -> UserUpgradeResponse:
    """Request Supabase verification without changing the Alibi user row."""
    await user_service.upgrade_user_email(user, payload.email)
    return UserUpgradeResponse()


@auth_router.post("/verify-email", response_model=AuthSessionResponse)
async def verify_email(
    payload: VerifyEmailRequest,
    user: CurrentUser,
) -> AuthSessionResponse:
    """Verify a Supabase email-change OTP for the authenticated guest."""
    session = await user_service.verify_supabase_email_change(
        user, payload.email, payload.otp
    )
    return AuthSessionResponse.model_validate(session)


@auth_router.post("/set-password", status_code=204)
async def set_password(payload: SetPasswordRequest, user: CurrentUser) -> None:
    """Set a password after Supabase confirms the account email is verified."""
    await user_service.set_supabase_password(user, payload.password)


__all__ = ["auth_router", "router", "upgrade_router"]
