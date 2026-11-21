from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.api.health import router as health_router
from app.api.metrics import router as metrics_router
from app.api.router import router as api_router
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import configure_logging
from app.core.middleware import register_security_middleware
from app.core.request_context import RequestContextMiddleware
from app.db.session import close_db, engine
from app.infrastructure.cache.redis_client import check_redis, create_redis_client


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Manage shared application resources across the ASGI lifecycle."""
    settings.validate_required_settings()
    redis_client = create_redis_client()
    app.state.redis = redis_client
    try:
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))

        await check_redis(redis_client)
        yield
    finally:
        await redis_client.aclose()
        await close_db()


def create_app() -> FastAPI:
    """Build the Alibi ASGI application with environment-specific settings."""
    configure_logging(settings.LOG_LEVEL)
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description="Alibi Backend API",
        version=settings.VERSION,
        debug=settings.APP_DEBUG,
        lifespan=lifespan,
        docs_url="/docs" if settings.APP_ENV != "production" else None,
        redoc_url=None,
        openapi_url="/openapi.json" if settings.APP_ENV != "production" else None,
    )
    register_security_middleware(
        app,
        trusted_hosts=settings.TRUSTED_HOSTS,
        max_body_bytes=settings.MAX_REQUEST_BODY_BYTES,
    )
    app.add_middleware(RequestContextMiddleware)
    register_exception_handlers(app)
    app.include_router(health_router)
    app.include_router(metrics_router)
    app.include_router(api_router)
    # Keep CORS outside ServerErrorMiddleware so browser clients can read 500s.
    app.middleware_stack = CORSMiddleware(
        app=app.build_middleware_stack(),
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=False,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
        allow_headers=["Authorization", "Content-Type"],
    )
    return app


app = create_app()
