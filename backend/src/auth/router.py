from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select

from src.database import AsyncSession, get_db_session
from src.schemas import ClientErrorResponse

from .dependencies import get_current_active_user
from .enums import TokenType
from .models import Token, User
from .schemas import TokenResponse, UserCreate, UserRead
from .service import oauth2_scheme
from .utils import (
    authenticate_user,
    create_access_token,
    create_refresh_token,
    delete_user_tokens,
    get_password_hash,
    get_token,
    get_user,
)

router = APIRouter(prefix="/api/v1", tags=["auth"])


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=UserRead,
    responses={
        400: {
            "description": "Passwords did not match",
            "model": ClientErrorResponse,
        },
        409: {
            "description": "Username is already taken",
            "model": ClientErrorResponse,
        },
    },
)
async def register(  # noqa: ANN201
    user: UserCreate,
    session: AsyncSession = Depends(get_db_session),
):
    # check if user already exist
    try:
        await get_user(session, user.username)
    except HTTPException:
        pass
    else:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This username is already taken",
        )

    # compare passwords
    if user.password != user.password_confirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match",
        )

    # hash the password
    user.password = get_password_hash(user.password)
    del user.password_confirm

    # non-schema fields
    user_dict = user.model_dump()
    user_dict["is_active"] = True

    new_user = User(**user_dict)

    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)

    return new_user


@router.post(
    "/token",
    response_model=TokenResponse,
    responses={
        400: {
            "description": "Incorrect username or password",
            "model": ClientErrorResponse,
        },
    },
)
async def token(  # noqa: ANN201
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_db_session),
):
    user = await authenticate_user(form_data.username, form_data.password, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # remove old access and refresh tokens
    await delete_user_tokens(session=session, user=user)

    access_token = await create_access_token(
        session=session,
        user=user,
        scopes=form_data.scopes,
    )
    refresh_token = await create_refresh_token(
        session=session,
        user=user,
        scopes=form_data.scopes,
    )

    return {
        "access_token": access_token.token,
        "refresh_token": refresh_token.token,
    }


@router.get("/tokens")
async def get_tokens(session: AsyncSession = Depends(get_db_session)):  # noqa: ANN201
    result = await session.execute(
        select(Token).where(Token.type.in_([TokenType.ACCESS])),
    )
    access_tokens = len(list(result.scalars()))
    result = await session.execute(
        select(Token).where(
            Token.type.in_([TokenType.REFRESH]),
        ),
    )
    refresh_tokens = len(list(result.scalars()))
    return {
        "access_tokens": access_tokens,
        "refresh_tokens": refresh_tokens,
    }


@router.post(
    "/token/refresh",
    response_model=TokenResponse,
    responses={
        401: {
            "description": "Refresh token either expired or doesn't exist",
            "model": ClientErrorResponse,
        },
    },
)
async def refresh_token(  # noqa: ANN201
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_db_session),
):
    refresh_token = await get_token(
        token=token,
        token_type=TokenType.REFRESH,
        session=session,
    )

    user = refresh_token.user
    expires = refresh_token.expires
    scopes = refresh_token.scopes

    # remove old access and refresh tokens
    await delete_user_tokens(session=session, user=user)

    new_access_token = await create_access_token(
        session=session,
        user=user,
        scopes=scopes,
    )
    # create a new refresh token with the same expiration date
    new_refresh_token = await create_refresh_token(
        session=session,
        user=user,
        expires=expires,
        scopes=scopes,
    )

    return {
        "access_token": new_access_token.token,
        "refresh_token": new_refresh_token.token,
    }


@router.post(
    "/token/revoke",
    responses={
        401: {
            "description": "Access token either expired or doesn't exist",
            "model": ClientErrorResponse,
        },
    },
)
async def revoke_token(  # noqa: ANN201
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    await delete_user_tokens(session=session, user=current_user)
    return Response()


@router.get("/users/me", response_model=UserRead)
async def me(current_user: User = Depends(get_current_active_user)):  # noqa: ANN201
    return current_user


@router.get("/users", response_model=list[UserRead])
async def users(  # noqa: ANN201
    session: AsyncSession = Depends(get_db_session),
):
    result = await session.execute(select(User))
    return result.scalars().all()


@router.get("/users/{user_id}", response_model=UserRead)
async def user(  # noqa: ANN201
    user_id: int,
    session: AsyncSession = Depends(get_db_session),
):
    user = await session.get(User, user_id)

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return user
