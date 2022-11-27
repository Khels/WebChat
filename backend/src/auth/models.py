from datetime import datetime

from sqlalchemy import (Boolean, Column, DateTime, Enum, ForeignKey, Integer,
                        String, Text, UniqueConstraint)
from sqlalchemy.orm import relationship
from src.database import Base

from .service import TokenType


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

    tokens = relationship("Token", back_populates="user")


class Token(Base):
    __tablename__ = "token"
    __table_args__ = (
        UniqueConstraint("type", "user_id", name="unique_token"),
    )

    id = Column(Integer, primary_key=True)
    token = Column(String(length=128), index=True, nullable=False)
    type = Column(Enum(TokenType, name="token_type"), nullable=False)
    user_id = Column(
        Integer,
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False
    )
    expires = Column(DateTime, nullable=False)
    scopes = Column(Text, nullable=False)  # space-separated scopes

    user = relationship("User", back_populates="tokens")

    def expired(self) -> bool:
        return self.expires <= datetime.utcnow()
