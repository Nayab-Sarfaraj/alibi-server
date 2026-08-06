from datetime import datetime
from typing import Any

from fastapi import Depends, HTTPException, status
from jose import JWTError

from app.dependencies.auth import oauth2_scheme
from app.utils.jwt import create_access_token, create_refresh_token, decode_token
from app.utils.security import hash_password, verify_password


def register(email: str, password: str) -> dict[str, str]:
    user = User.get_user_by_email(email)
    if user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    hashed_password = hash_password(password)
    new_user = User.create({"email": email, "hashed_password": hashed_password})

    access_token = create_access_token({"sub": str(new_user.id)})
    refresh_token, refresh_payload = create_refresh_token({"sub": str(new_user.id)})

    Token.create(
        {
            "user_id": new_user.id,
            "jti": refresh_payload["jti"],
            "expires_at": refresh_payload["exp"],
            "revoked_at": None,
        }
    )

    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

def login(email: str, password: str) -> dict[str, str]:
    user = User.get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    if not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    access_token = create_access_token({"sub": str(user.id)})
    refresh_token, refresh_payload = create_refresh_token({"sub": str(user.id)})

    Token.create(
        {
            "user_id": user.id,
            "jti": refresh_payload["jti"],
            "expires_at": refresh_payload["exp"],
            "revoked_at": None,
        }
    )

    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


def get_current_user(token: str = Depends(oauth2_scheme)) -> Any:
    try:
        payload = decode_token(token)
    except JWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user = User.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    return user


def refresh_access_token(refresh_token: str) -> dict[str, str]:
    try:
        payload = decode_token(refresh_token)
    except JWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc

    token_type = payload.get("token_type")
    jti = payload.get("jti")
    if token_type != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")

    db_token = Token.get_token_by_jti(jti)
    if db_token is None or db_token.revoked_at is not None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is revoked")

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user = User.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    new_access_token = create_access_token({"sub": str(user.id)})
    new_refresh_token, new_refresh_payload = create_refresh_token({"sub": str(user.id)})

    Token.create(
        {
            "user_id": user.id,
            "jti": new_refresh_payload["jti"],
            "expires_at": new_refresh_payload["exp"],
            "revoked_at": None,
        }
    )

    db_token.revoked_at = datetime.now()
    db_token.save()

    return {"access_token": new_access_token, "refresh_token": new_refresh_token, "token_type": "bearer"}


def logout(refresh_token: str) -> dict[str, str]:
    try:
        payload = decode_token(refresh_token)
    except JWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc

    if payload.get("token_type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")

    jti = payload.get("jti")
    db_token = Token.get_token_by_jti(jti)
    if db_token is None or db_token.revoked_at is not None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is revoked or invalid")
    db_token.revoked_at = datetime.now()
    db_token.save() 
    return {"message": "Logged out successfully"}