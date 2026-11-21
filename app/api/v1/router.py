"""Version 1 API router composition."""

from typing import Any

from fastapi import APIRouter

from app.api.dependencies import CurrentUser
from app.modules.cases.router import router as cases_router
from app.modules.users.router import router as users_router

router = APIRouter()
router.include_router(users_router, prefix="/users", tags=["users"])
router.include_router(cases_router, prefix="/cases", tags=["cases"])


@router.get("/auth/test", tags=["Auth"])
async def test_auth(user: CurrentUser) -> dict[str, Any]:
    """Temporary test route to verify Supabase JWT authentication."""
    return {
        "status": "authenticated",
        "user": user,
    }


@router.get("/ping", tags=["System"])
async def ping() -> dict[str, str]:
    return {"message": "pong"}
