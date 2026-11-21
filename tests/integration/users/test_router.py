"""Integration checks for the users router."""


def test_users_router_is_registered() -> None:
    from app.api.v1.router import router as v1_router
    from app.modules.users.router import router as users_router

    assert any(
        getattr(route, "original_router", None) is users_router
        for route in v1_router.routes
    )
