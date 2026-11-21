"""Dependencies shared across API versions and feature routers."""

from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer


@dataclass(frozen=True)
class AuthenticatedUser:
    """Authenticated principal shape for future protected endpoints."""

    id: str
    role: str


bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(bearer_scheme),
    ],
) -> AuthenticatedUser:
    """Fail closed until token verification is implemented in Phase 4."""
    del credentials
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication is not yet available",
        headers={"WWW-Authenticate": "Bearer"},
    )


CurrentUser = Annotated[AuthenticatedUser, Depends(get_current_user)]


def get_request_id(request: Request) -> str | None:
    """Return a caller-provided request identifier when one is available."""
    return request.headers.get("X-Request-ID")
