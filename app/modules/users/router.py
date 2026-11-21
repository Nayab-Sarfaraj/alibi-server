"""User API routes belong here as the feature is expanded."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import CurrentUser
from app.db.session import get_db
from app.modules.users import service as user_service
from app.modules.users.schemas import UserResponse

router = APIRouter()


@router.post("/me", response_model=UserResponse)
@router.get("/me", response_model=UserResponse)
async def get_or_create_user(
    user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserResponse:
    """Resolve or create application user from authenticated identity."""
    db_user = await user_service.get_or_create_user(user, db)
    return UserResponse.model_validate(db_user)


__all__ = ["router"]
