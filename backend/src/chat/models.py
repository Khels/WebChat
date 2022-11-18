from datetime import datetime

from sqlalchemy import (Boolean, Column, DateTime, ForeignKey, Integer, String,
                        Text)
from sqlalchemy.orm import relationship
from src.database import Base


class Chat(Base):
    __tablename__ = "chat"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    image_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.timestamp)

    participants = relationship(
        "User",
        secondary="chat_participant",
        backref="chats"
    )


class ChatParticipant(Base):
    __tablename__ = "chat_participant"

    chat_id = Column(Integer, ForeignKey("chat.id"), primary_key=True)
    participant_id = Column(Integer, ForeignKey("user.id"), primary_key=True)
    is_admin = Column(Boolean, default=False, nullable=False)


class Message(Base):
    __tablename__ = "message"

    id = Column(Integer, primary_key=True)
    sender_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    chat_id = Column(Integer, ForeignKey("chat.id"), nullable=False)
    content = Column(Text)
    is_edited = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.timestamp)

    chat = relationship("Chat", backref="messages")
