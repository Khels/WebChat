from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from .config import DATABASE_URL, DEBUG

engine = create_async_engine(DATABASE_URL, future=True, echo=DEBUG)

Base = declarative_base()

_AsyncSession = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


# Dependency
async def get_db_session() -> AsyncGenerator[AsyncSession]:
    async with _AsyncSession() as session:
        yield session
