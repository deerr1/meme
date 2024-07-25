from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession

from core.settings import settings

session_factory: AsyncSession = async_sessionmaker(
            create_async_engine(
                settings.SQLALCHEMY_DATABASE_URI
            )
        )

@asynccontextmanager
async def get_session() -> AsyncSession:
    try:
        session = session_factory()
        yield session
    finally:
        await session.close()