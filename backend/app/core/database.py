from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


_db_url = settings.normalized_database_url
_is_sqlite = _db_url.startswith("sqlite")

engine = create_async_engine(
    _db_url,
    echo=False,
    pool_pre_ping=not _is_sqlite,
    connect_args={"check_same_thread": False} if _is_sqlite else {},
)

AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
