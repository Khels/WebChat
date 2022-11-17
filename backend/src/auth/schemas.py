from datetime import datetime

from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str


class UserBase(BaseModel):
    username: str
    first_name: str
    last_name: str


class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    id: int
    last_online: datetime | None
    is_active: bool
    is_admin: bool

    class Config:
        orm_mode = True


class UserUpdate(BaseModel):
    username: str | None
    first_name: str | None
    last_name: str | None
