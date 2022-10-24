from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from .config import DATABASE_URL

engine = create_async_engine(DATABASE_URL)


async def get_session() -> AsyncSession:
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session
