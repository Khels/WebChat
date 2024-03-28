from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base
from src.models import CreatedAtMixin, IdMixin

from .enums import ChatType, MessageType
from .schemas import ParticipantCreate

if TYPE_CHECKING:
    from src.auth.models import User


class Chat(IdMixin, CreatedAtMixin, Base):
    __tablename__ = "chat"

    name: Mapped[str] = mapped_column(String(128))
    type: Mapped[ChatType] = mapped_column(ENUM(ChatType, name="chat_type"))
    image_url: Mapped[str]

    messages: Mapped[list["Message"]] = relationship("Message", back_populates="chat")
    participants: Mapped[list["ChatParticipant"]] = relationship(
        "ChatParticipant",
        back_populates="chat",
    )

    def add_participants(self: "Chat", participants: list[ParticipantCreate]) -> None:
        for participant in participants:
            self.participants.append(
                ChatParticipant(
                    participant_id=participant.id,
                    is_admin=participant.is_admin,
                ),
            )


class ChatParticipant(CreatedAtMixin, Base):
    __tablename__ = "chat_participant"

    chat_id: Mapped[int] = mapped_column(
        ForeignKey("chat.id", ondelete="CASCADE"),
        primary_key=True,
    )
    participant_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"),
        primary_key=True,
    )
    is_admin: Mapped[bool] = mapped_column(default=False)

    chat: Mapped["Chat"] = relationship("Chat", back_populates="participants")
    participant: Mapped["User"] = relationship("User", back_populates="chats")


class Message(IdMixin, CreatedAtMixin, Base):
    __tablename__ = "message"

    author_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    sender_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    chat_id: Mapped[int] = mapped_column(ForeignKey("chat.id"))
    type: Mapped[MessageType] = mapped_column(ENUM(MessageType, name="message_type"))
    content: Mapped[str] = mapped_column(Text)
    is_read: Mapped[bool] = mapped_column(default=False)
    is_edited: Mapped[bool] = mapped_column(default=False)

    author: Mapped["User"] = relationship("User", foreign_keys=[author_id])
    sender: Mapped["User"] = relationship("User", foreign_keys=[sender_id])
    chat: Mapped["Chat"] = relationship("Chat", back_populates="messages")
