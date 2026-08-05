from fastapi import APIRouter

router = APIRouter()

@router.get("/health", tags=["Health"])
def read_health() -> dict[str, str]:
    return {"status": "ok", "message": "Courtroom server is healthy."}
