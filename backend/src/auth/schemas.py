from datetime import datetime

from pydantic import BaseModel


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str


class TokenData(BaseModel):
    username: str


class UserBase(BaseModel):
    username: str
    first_name: str | None
    last_name: str | None


class UserCreate(BaseModel):
    username: str
    password: str
    password_confirm: str


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
