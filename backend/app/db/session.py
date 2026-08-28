from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

engine = create_async_engine(settings.SQLALCHEMY_DATABASE_URI, echo=False)
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Alias so other modules can import either name
async_session_maker = async_session

Base = declarative_base()

async def get_db():
    async with async_session() as session:
        yield session
