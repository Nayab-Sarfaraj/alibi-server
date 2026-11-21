"""Authorization dependency primitives."""

from collections.abc import Callable
from typing import Annotated

from fastapi import Depends, HTTPException, status

from app.api.dependencies import get_current_user


def require_role(allowed_roles: set[str]) -> Callable[..., object]:
    """Create a dependency that permits only principals with an allowed role."""

    async def check_role(
        user: Annotated[
            object,
            Depends(get_current_user),
        ],
    ) -> object:
        role = getattr(user, "role", None)
        if role is None and isinstance(user, dict):
            role = user.get("role")
        if role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return user

    return check_role
