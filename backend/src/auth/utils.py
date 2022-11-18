import secrets
import string
from datetime import datetime, timedelta

from fastapi import HTTPException
from sqlalchemy import select
from src.config import ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS
from src.database import AsyncSession

from .models import AccessToken, RefreshToken, User
from .service import pwd_context


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


async def get_user(session: AsyncSession, username: str) -> User:
    result = await session.execute(
        select(User).where(User.username.ilike(username)))
    user = result.scalar()

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return user


async def authenticate_user(
    session: AsyncSession, username: str, password: str
) -> User | bool:
    user = await get_user(session, username)
    if not user:
        return False
    if not verify_password(plain_password=password,
                           hashed_password=user.password):
        return False
    return user


def generate_token(length: int = 128) -> str:
    symbols = string.ascii_letters + string.digits + "#$%&()+-/:;<=>?@[]_{|}~"
    token = ''.join(secrets.choice(symbols) for i in range(length))
    return token


async def create_token(
    session: AsyncSession,
    token_model: type[AccessToken] | type[RefreshToken],
    user: User,
    expires: timedelta,
    scopes: str | None = None
) -> AccessToken | RefreshToken:
    token = generate_token()
    expires = datetime.utcnow() + expires
    scopes = scopes if scopes else ""

    new_token = token_model(
        token=token,
        user=user,
        expires=expires,
        scopes=scopes
    )

    session.add(new_token)

    await session.commit()
    await session.refresh(new_token)

    return new_token


async def create_access_token(
    session: AsyncSession,
    user: User,
    scopes: str | None = None
) -> AccessToken:
    return await create_token(
        session=session,
        token_model=AccessToken,
        user=user,
        expires=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        scopes=scopes
    )


async def create_refresh_token(
    session: AsyncSession,
    user: User,
    scopes: str | None = None
) -> RefreshToken:
    return await create_token(
        session=session,
        token_model=RefreshToken,
        user=user,
        expires=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        scopes=scopes
    )
