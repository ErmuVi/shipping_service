from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from src.config import settings


class Base(DeclarativeBase):
    pass


engine = create_async_engine(settings.database_url)
session_maker = async_sessionmaker(bind=engine, expire_on_commit=False)


async def get_async_session():
    async with session_maker() as session:
        yield session
