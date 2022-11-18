from datetime import datetime

from pydantic import BaseModel


class TokenBase(BaseModel):
    token: str
    expires: datetime
    scopes: str

    class Config:
        orm_mode = True


class AccessToken(TokenBase):
    pass


class RefreshToken(TokenBase):
    pass


class LoginResponse(BaseModel):
    access_token: AccessToken
    refresh_token: RefreshToken


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str


class UserBase(BaseModel):
    username: str
    first_name: str | None
    last_name: str | None


class UserCreate(UserBase):
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
