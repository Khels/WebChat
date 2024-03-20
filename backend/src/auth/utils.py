import secrets
import string
from datetime import UTC, datetime, timedelta

from fastapi import HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy import delete, select
from sqlalchemy.orm import joinedload

from src.config import ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS
from src.database import AsyncSession
from src.enums import WSError

from .enums import TokenType
from .exceptions import InvalidTokenHTTPException, TokenExpiredHTTPException
from .models import Token, User
from .service import pwd_context


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


async def get_user(session: AsyncSession, username: str) -> User:
    query = select(User).where(User.username.ilike(username))
    result = await session.execute(query)
    user = result.scalar()

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return user


async def authenticate_user(
    username: str,
    password: str,
    session: AsyncSession,
) -> User | bool:
    user = await get_user(session, username)
    if not user:
        return False
    if not verify_password(plain_password=password, hashed_password=user.password):
        return False
    return user


async def authenticate_user_token(
    token: str,
    session: AsyncSession,
    websocket: WebSocket | None = None,
) -> User | bool:
    access_token = await get_token(
        token=token,
        token_type=TokenType.ACCESS,
        session=session,
        websocket=websocket,
    )
    user = access_token.user

    if not user.is_active:
        if websocket:
            raise WebSocketDisconnect(
                code=WSError.INACTIVE_USER,
                reason=WSError.INACTIVE_USER.label,
            )
        raise HTTPException(status_code=400, detail="Inactive user")

    return user


def generate_token(length: int = 64) -> str:
    symbols = string.ascii_letters + string.digits
    return "".join(secrets.choice(symbols) for i in range(length))


async def create_token(
    session: AsyncSession,
    token_type: TokenType,
    user: User,
    expires: datetime | timedelta,
    scopes: str | None = None,
) -> Token:
    token = generate_token()
    if isinstance(expires, timedelta):
        expires = datetime.now(UTC) + expires
    scopes = scopes if scopes else ""

    new_token = Token(
        token=token,
        type=token_type,
        user_id=user.id,
        expires=expires,
        scopes=scopes,
    )

    session.add(new_token)
    await session.commit()
    await session.refresh(new_token)

    return new_token


async def create_access_token(
    session: AsyncSession,
    user: User,
    scopes: str | None = None,
) -> Token:
    return await create_token(
        session=session,
        token_type=TokenType.ACCESS,
        user=user,
        expires=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        scopes=scopes,
    )


async def create_refresh_token(
    session: AsyncSession,
    user: User,
    expires: datetime | None = None,
    scopes: str | None = None,
) -> Token:
    return await create_token(
        session=session,
        token_type=TokenType.REFRESH,
        user=user,
        expires=expires if expires else timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        scopes=scopes,
    )


async def get_token(
    token: str,
    token_type: TokenType,
    session: AsyncSession,
    websocket: WebSocket | None = None,
) -> Token:
    query = (
        select(Token)
        .where(
            Token.token == token,
            Token.type.in_([token_type]),
        )
        .options(
            joinedload(Token.user, innerjoin=True),
        )
    )
    result = await session.execute(query)
    access_token: Token = result.scalar()

    if access_token is None:
        if websocket:
            raise WebSocketDisconnect(
                code=WSError.INVALID_TOKEN,
                reason=WSError.INVALID_TOKEN.label,
            )
        raise InvalidTokenHTTPException

    if access_token.expired():
        if websocket:
            raise WebSocketDisconnect(
                code=WSError.TOKEN_EXPIRED,
                reason=WSError.TOKEN_EXPIRED.label,
            )
        raise TokenExpiredHTTPException

    return access_token


async def delete_user_tokens(session: AsyncSession, user: User) -> None:
    await session.execute(delete(Token).where(Token.user_id == user.id))
    await session.commit()
