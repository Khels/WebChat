from datetime import datetime

from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    __tablename__ = "user"

    id: int = Field(primary_key=True)
    username: str = Field(unique=True)
    first_name: str = Field(default="")
    last_name: str = Field(default="")
    password: str
    last_online: datetime = Field()
    is_active: bool = Field(default=True)
    is_admin: bool = Field(default=False)
