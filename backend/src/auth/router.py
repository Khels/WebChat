from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from src.database import AsyncSession, get_session

from .models import User
from .schemas import UserCreate, UserRead

router = APIRouter(prefix="/api/v1", tags=['auth'])


@router.post("/users", response_model=UserRead)
async def create_user(
    user: UserCreate,
    session: AsyncSession = Depends(get_session)
):
    user = User(**user.dict())

    session.add(user)

    await session.commit()
    await session.refresh(user)

    return user


# @router.get("/users/me")
# async def me():
#     query = User.select().where(User.id == )
#     user = await db.
#     return {"username": "fakecurrentuser"}


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
