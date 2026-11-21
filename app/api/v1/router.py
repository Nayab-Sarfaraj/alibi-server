"""Version 1 API router composition."""

from typing import Any

from fastapi import APIRouter, Response

from app.api.dependencies import CurrentUser
from app.modules.cases.router import router as cases_router
from app.modules.users.router import auth_router, upgrade_router
from app.modules.users.router import router as users_router

router = APIRouter()
router.include_router(users_router, prefix="/users", tags=["users"])
router.include_router(upgrade_router, prefix="/user", tags=["users"])
router.include_router(auth_router, prefix="/auth", tags=["auth"])
router.include_router(cases_router, prefix="/cases", tags=["cases"])


@router.get("/auth/test", tags=["Auth"])
async def test_auth(user: CurrentUser, response: Response) -> dict[str, Any]:
    """Temporary test route to verify Supabase JWT authentication."""
    del user
    response.headers["Cache-Control"] = "no-store"
    return {"status": "authenticated"}


@router.get("/ping", tags=["System"])
async def ping() -> dict[str, str]:
    return {"message": "pong"}
