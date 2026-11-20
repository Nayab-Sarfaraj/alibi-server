from fastapi import APIRouter

router = APIRouter(tags=["Health"])


@router.get("/health/live")
async def liveness() -> dict[str, str]:
    return {"status": "alive"}


@router.get("/health/ready")
async def readiness() -> dict[str, str]:
    return {"status": "ready"}
