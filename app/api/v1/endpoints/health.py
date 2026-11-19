from fastapi import APIRouter

router = APIRouter()

@router.get("/health", tags=["Health"])
def read_health() -> dict[str, str]:
    return {"status": "ok", "message": "Alibi server is healthy."}
