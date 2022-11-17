from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from src.config import ACCESS_TOKEN_EXPIRE_MINUTES
from src.database import AsyncSession, get_session

from .dependencies import get_current_active_user
from .models import User
from .schemas import Token, UserCreate, UserRead
from .utils import authenticate_user, create_access_token, get_password_hash

router = APIRouter(prefix="/api/v1", tags=['auth'])


@router.post("/token", response_model=Token)
async def get_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session)
):
    user = await authenticate_user(
        session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/users", response_model=UserRead)
async def create_user(
    user: UserCreate,
    session: AsyncSession = Depends(get_session)
):
    data = user.dict()
    hashed_password = get_password_hash(data["password"])
    data["password"] = hashed_password
    user = User(**data)

    session.add(user)

    await session.commit()
    await session.refresh(user)

    return user


@router.get("/users/me", response_model=UserRead)
async def me(current_user: User = Depends(get_current_active_user)):
    return current_user


@router.get("/users", response_model=list[UserRead])
async def get_users(
    session: AsyncSession = Depends(get_session)
):
    results = await session.execute(select(User))
    return results.scalars().all()


@router.get("/users/{user_id}", response_model=UserRead)
async def get_user(
    user_id: int,
    session: AsyncSession = Depends(get_session)
):
    user = await session.get(User, user_id)

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return user
