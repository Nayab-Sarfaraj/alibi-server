from fastapi import FastAPI

from app.api.router import router as api_router
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="FastAPI backend for Alibi.",
    version=settings.VERSION,
)

app.include_router(api_router)


@app.on_event("startup")
async def on_startup() -> None:
    settings.validate_required_settings()


@app.on_event("shutdown")
async def on_shutdown() -> None:
    # Clean up resources here.
    pass


@app.get("/")
def health_check() -> dict[str, str]:
    return {"status": "ok", "environment": settings.APP_ENV}
