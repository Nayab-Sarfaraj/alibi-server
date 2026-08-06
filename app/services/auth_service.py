from datetime import datetime

from app.utils.security import verify_password
from app.utils.jwt import create_access_token, create_refresh_token,decode_access_token, decode_token
from fastapi import Depends, HTTPException,status
from app.dependencies.auth import oauth2_scheme    

def login(email:str,password:str):
    user = User.get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    if not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    
    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})

    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


def get_current_user(token:str=Depends(oauth2_scheme)):
    payload = decode_token(token)
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user = User.get_user_by_id(user_id)

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    return user


def refresh_access_token(refresh_token:str):
    payload = decode_token(refresh_token)
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
    new_refresh_token = create_refresh_token({"sub": str(user.id)})
    db_token.revoked_at = datetime.now()
    db_token.save()

    return {"access_token": new_access_token, "refresh_token": new_refresh_token, "token_type": "bearer"}   
