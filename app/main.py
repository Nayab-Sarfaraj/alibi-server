from fastapi import FastAPI

from app.api.v1 import api_router
from app.core.config import settings
from app.db.session import engine

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="FastAPI backend for courtroom services.",
    version=settings.VERSION,
)

app.include_router(api_router, prefix="/api/v1")

@app.on_event("startup")
async def on_startup() -> None:
    # Initialize or check services here, e.g. database connection pooling or cache warming.
    pass

@app.on_event("shutdown")
async def on_shutdown() -> None:
    # Clean up resources here.
    pass

@app.get("/")
def health_check() -> dict[str, str]:
    return {"status": "ok", "environment": settings.APP_ENV}
