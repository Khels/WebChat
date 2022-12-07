from sqlalchemy import Column, DateTime, Integer
from sqlalchemy.orm import declarative_mixin
from sqlalchemy.sql import func


@declarative_mixin
class IdMixin:
    id = Column(Integer, primary_key=True)


@declarative_mixin
class CreatedAtMixin:
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
