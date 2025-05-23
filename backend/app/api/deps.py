from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
from typing import Annotated

from app.core.db import get_session
from app.crud import get_public_user
from app.core.config import settings
from app.models import UserPublic, TokenPayload

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"/api/auth/signin-openapi",
    scheme_name="JWT"
)

TokenDep = Annotated[str, Depends(reusable_oauth2)]

async def get_current_user(token: TokenDep) -> UserPublic:
    print(token)
    try:
        payload = jwt.decode(
            token, settings.SECURITY_SECRET_KEY, algorithms=[settings.SECURITY_ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (InvalidTokenError, ValidationError) as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    async with get_session() as session:
        user = await get_public_user(int(token_data.sub))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user


CurrentUser = Annotated[UserPublic, Depends(get_current_user)]