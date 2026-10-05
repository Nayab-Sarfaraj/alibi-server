from fastapi import APIRouter, Depends, HTTPException, status

from app.services.auth_service import (
    get_current_user,
    login,
    logout,
    refresh_access_token,
    register,
)

router = APIRouter()


@router.post("/register")
def register_endpoint(payload: dict[str, str]) -> dict[str, str]:
    email = payload.get("email")
    password = payload.get("password")
    if not email or not password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email and password are required")
    return register(email, password)


@router.post("/login")
def login_endpoint(payload: dict[str, str]) -> dict[str, str]:
    email = payload.get("email")
    password = payload.get("password")
    if not email or not password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email and password are required")
    return login(email, password)


@router.post("/refresh")
def refresh_endpoint(payload: dict[str, str]) -> dict[str, str]:
    refresh_token = payload.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Refresh token is required")
    return refresh_access_token(refresh_token)


@router.post("/logout")
def logout_endpoint(payload: dict[str, str]) -> dict[str, str]:
    refresh_token = payload.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Refresh token is required")
    return logout(refresh_token)


@router.get("/me")
def me(current_user=Depends(get_current_user)) -> dict[str, str]:
    return {"email": current_user.email}