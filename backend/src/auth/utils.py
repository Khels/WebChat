from datetime import datetime, timedelta

from fastapi import HTTPException
from jose import jwt
from sqlalchemy import select
from src.config import ALGORITHM, SECRET_KEY
from src.database import AsyncSession

from .models import User
from .service import pwd_context


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
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


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# TODO
def create_refresh_token():
    pass
