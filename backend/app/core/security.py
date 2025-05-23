from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status
from typing import Any
import jwt
from passlib.context import CryptContext

from app.models import TokenPayload
from app import crud
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def get_token_from_login_password(login: str, password: str) -> str:
    user = await crud.get_user_by_login(login)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if not verify_password(password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")

    access_token = create_access_token(
        subject=user.id,
        expires_delta=timedelta(seconds=settings.SECURITY_ACCESS_TOKEN_EXPIRE_SECONDS)
    )
    return {"access_token": access_token, "token_type": "bearer"}

def create_access_token(subject: int, expires_delta: timedelta) -> str:
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = TokenPayload(exp=expire, sub=str(subject)).model_dump()
    encoded_jwt = jwt.encode(to_encode, settings.SECURITY_SECRET_KEY, algorithm=settings.SECURITY_ALGORITHM)
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)