"""Authorization dependency primitives."""

from collections.abc import Callable
from typing import Annotated

from fastapi import Depends, HTTPException, status

from app.api.dependencies import AuthenticatedUser, get_current_user


def require_role(allowed_roles: set[str]) -> Callable[..., object]:
    """Create a dependency that permits only principals with an allowed role."""

    async def check_role(
        user: Annotated[
            AuthenticatedUser,
            Depends(get_current_user),
        ],
    ) -> AuthenticatedUser:
        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return user

    return check_role
