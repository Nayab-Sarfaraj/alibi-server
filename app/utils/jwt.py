from jose import jwt
from app.core.config import Settings
from datetime import datetime,timedelta
import uuid


Token_Types:dict={"ACCESS_TOKEN": "access", "REFRESH_TOKEN": "refresh"}

def create_access_token(data:dict)->str:
    return _create_token(data, timedelta(minutes=15), Token_Types["ACCESS_TOKEN"])


def create_refresh_token(data:dict)->str:
    return _create_token(data, timedelta(days=7), Token_Types["REFRESH_TOKEN"] )

def _create_token(data:dict,expires_delta:timedelta,token_type:str    )->str:
    to_encode = data.copy()
    expire = datetime.now() + expires_delta
    jti = str(uuid.uuid4())
    to_encode["exp"] = expire
    to_encode["token_type"] = token_type
    to_encode["jti"] = jti
    return jwt.encode(to_encode,Settings.SECRET_KEY,algorithm="HS256")

def decode_token(token:str)->dict:
    return jwt.decode(token,Settings.SECRET_KEY,algorithms=["HS256"])   

