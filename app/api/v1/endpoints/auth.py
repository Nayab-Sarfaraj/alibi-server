from fastapi import APIRouter, Depends
from app.services.auth_service import get_current_user

router = APIRouter()

@router.get("/me")
def me(current_user=Depends(get_current_user)):
    return current_user.email