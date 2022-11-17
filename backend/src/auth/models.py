from sqlalchemy import Boolean, Column, DateTime, Integer, String
from src.database import Base


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    username = Column(String, index=True, nullable=False, unique=True)
    first_name = Column(String, default="", nullable=False)
    last_name = Column(String, default="", nullable=False)
    password = Column(String, nullable=False)
    last_online = Column(DateTime, default=None)
    is_active = Column(Boolean, default=True, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
