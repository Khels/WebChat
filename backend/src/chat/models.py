from sqlalchemy import Boolean, Column, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from src.database import Base
from src.models import CreatedAtMixin, IdMixin

from .enums import ChatType, MessageType
from .schemas import ParticipantCreate


class Chat(IdMixin, CreatedAtMixin, Base):
    __tablename__ = "chat"

    name = Column(String)
    type = Column(Enum(ChatType, name="chat_type"), nullable=False)
    image_url = Column(String)

    messages = relationship("Message", back_populates="chat")
    participants = relationship("ChatParticipant", back_populates="chat")

    def add_participants(self, participants: list[ParticipantCreate]):
        for participant in participants:
            self.participants.append(ChatParticipant(
                participant_id=participant.id,
                is_admin=participant.is_admin
            ))


class ChatParticipant(Base):
    __tablename__ = "chat_participant"

    chat_id = Column(
        Integer,
        ForeignKey("chat.id", ondelete="CASCADE"),
        primary_key=True
    )
    participant_id = Column(
        Integer,
        ForeignKey("user.id", ondelete="CASCADE"),
        primary_key=True
    )
    is_admin = Column(Boolean, default=False, nullable=False)

    chat = relationship("Chat", back_populates="participants")
    participant = relationship("User", back_populates="chats")


class Message(IdMixin, CreatedAtMixin, Base):
    __tablename__ = "message"

    author_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    sender_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    chat_id = Column(Integer, ForeignKey("chat.id"), nullable=False)
    type = Column(Enum(MessageType, name="message_type"), nullable=False)
    content = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False, nullable=False)
    is_edited = Column(Boolean, default=False, nullable=False)

    author = relationship("User", foreign_keys=[author_id])
    sender = relationship("User", foreign_keys=[sender_id])
    chat = relationship("Chat", back_populates="messages")
