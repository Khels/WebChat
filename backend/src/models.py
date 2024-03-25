from datetime import datetime

from sqlalchemy.orm import Mapped, declarative_mixin, mapped_column
from sqlalchemy.sql import func


@declarative_mixin
class IdMixin:
    id: Mapped[int] = mapped_column(primary_key=True)


@declarative_mixin
class CreatedAtMixin:
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
