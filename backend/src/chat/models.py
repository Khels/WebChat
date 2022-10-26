from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String
from src.database import Base


class Chat(Base):
    __tablename__ = "chat"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    logo = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.timestamp)
