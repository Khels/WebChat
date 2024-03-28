from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    DateTime,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base
from src.models import CreatedAtMixin, IdMixin

from .enums import TokenType

if TYPE_CHECKING:
    from src.chat.models import ChatParticipant


class User(IdMixin, CreatedAtMixin, Base):
    __tablename__ = "user"

    username: Mapped[str] = mapped_column(index=True, unique=True)
    first_name: Mapped[str] = mapped_column(default="")
    last_name: Mapped[str] = mapped_column(default="")
    password: Mapped[str] = mapped_column(String(256))
    last_online: Mapped[datetime | None] = mapped_column(default=None)
    is_active: Mapped[bool] = mapped_column(default=False)
    is_admin: Mapped[bool] = mapped_column(default=False)

    tokens: Mapped[list["Token"]] = relationship("Token", back_populates="user")
    chats: Mapped[list["ChatParticipant"]] = relationship(
        "ChatParticipant",
        back_populates="participant",
    )


class Token(IdMixin, CreatedAtMixin, Base):
    __tablename__ = "token"
    __table_args__ = (UniqueConstraint("type", "user_id", name="unique_token"),)

    token: Mapped[str] = mapped_column(String(128), index=True)
    type: Mapped[TokenType] = mapped_column(ENUM(TokenType, name="token_type"))
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
    )
    expires: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    scopes: Mapped[str] = mapped_column(Text)  # space-separated scopes

    user: Mapped["User"] = relationship("User", back_populates="tokens")

    def expired(self: "Token") -> bool:
        return self.expires <= datetime.now(UTC)
