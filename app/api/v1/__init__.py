from app.api.v1.router import router

# Backward-compatible alias used by existing imports.
api_router = router

__all__ = ["api_router", "router"]
