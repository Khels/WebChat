from datetime import datetime

from pydantic import BaseModel


class UserBase(BaseModel):
    username: str
    first_name: str | None
    last_name: str | None
    last_online: datetime | None
    is_active: bool
    is_admin: bool


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int

    class Config:
        orm_mode = True
