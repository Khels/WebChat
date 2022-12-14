from fastapi import Depends, HTTPException
from src.database import AsyncSession, get_db_session

from .enums import TokenType
from .models import User
from .service import oauth2_scheme
from .utils import get_token


async def get_current_user(
    session: AsyncSession = Depends(get_db_session),
    token: str = Depends(oauth2_scheme)
):
    access_token = await get_token(
        token=token, token_type=TokenType.ACCESS, session=session)

    return access_token.user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
