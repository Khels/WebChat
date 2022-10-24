from fastapi import APIRouter, Depends
from sqlmodel import select
from src.database import AsyncSession, get_session

from .models import User
from .schemas import User as UserSchema
from .schemas import UserCreate

router = APIRouter(tags=['auth'])


@router.post("/users", response_model=UserSchema)
async def create_user(
    user: UserCreate, session: AsyncSession = Depends(get_session)
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


@router.get("/users/{user_id}")
async def get_user(
    user_id: int, session: AsyncSession = Depends(get_session)
):
    query = select(User).where(User.id == user_id)
    user = await session.execute(query)
    print(user)
    return user
