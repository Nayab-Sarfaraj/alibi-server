"""Version 1 API router composition."""

from fastapi import APIRouter

from app.modules.cases.router import router as cases_router
from app.modules.users.router import router as users_router

router = APIRouter()
router.include_router(users_router, prefix="/users", tags=["users"])
router.include_router(cases_router, prefix="/cases", tags=["cases"])


@router.get("/ping", tags=["System"])
async def ping() -> dict[str, str]:
    return {"message": "pong"}
