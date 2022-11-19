from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from src.database import AsyncSession, get_db_session

from .exceptions import InvalidTokenHTTPException, TokenExpiredHTTPException
from .models import AccessToken, User
from .service import oauth2_scheme


async def get_current_user(
    session: AsyncSession = Depends(get_db_session),
    token: str = Depends(oauth2_scheme)
):
    query = select(AccessToken).where(AccessToken.token == token).options(
        joinedload(AccessToken.user, innerjoin=True)
    )
    result = await session.execute(query)
    access_token: AccessToken = result.scalar()

    if access_token is None:
        raise InvalidTokenHTTPException()

    if access_token.expired():
        raise TokenExpiredHTTPException()

    return access_token.user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
