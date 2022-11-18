from sqlalchemy import (Boolean, Column, DateTime, ForeignKey, Integer, String,
                        Text)
from sqlalchemy.orm import declarative_mixin, declared_attr, relationship
from src.database import Base


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    username = Column(String, index=True, nullable=False, unique=True)
    first_name = Column(String, default="", nullable=False)
    last_name = Column(String, default="", nullable=False)
    password = Column(String, nullable=False)
    last_online = Column(DateTime, default=None)
    is_active = Column(Boolean, default=False, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)

    access_token = relationship(
        "AccessToken",
        back_populates="user",
        uselist=False,
        cascade="all, delete",
        passive_deletes=True
    )
    refresh_token = relationship(
        "RefreshToken",
        back_populates="user",
        uselist=False,
        cascade="all, delete",
        passive_deletes=True
    )


@declarative_mixin
class TokenMixin:
    id = Column(Integer, primary_key=True)
    token = Column(String(length=256), index=True, nullable=False)
    expires = Column(DateTime, nullable=False)
    scopes = Column(Text, nullable=False)  # space-separated scopes

    @declared_attr
    def user_id(cls):
        return Column(
            Integer,
            ForeignKey("user.id", ondelete="CASCADE"),
            nullable=False
        )


class AccessToken(TokenMixin, Base):
    __tablename__ = "access_token"

    user = relationship("User", back_populates="access_token")


class RefreshToken(TokenMixin, Base):
    __tablename__ = "refresh_token"

    user = relationship("User", back_populates="refresh_token")
