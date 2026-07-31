from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


_db_url = settings.normalized_database_url
_is_sqlite = _db_url.startswith("sqlite")

if _is_sqlite:
    _connect_args = {"check_same_thread": False}
else:
    # asyncpg quer `ssl='require'` (não sslmode) quando o servidor exige SSL (Neon/Supabase/etc).
    # statement_cache_size=0 é obrigatório quando conectando via pooler (Neon -pooler /
    # Supabase Supavisor / PgBouncer em transaction mode).
    _connect_args = {"statement_cache_size": 0}
    if settings.requires_ssl:
        _connect_args["ssl"] = "require"

engine = create_async_engine(
    _db_url,
    echo=False,
    pool_pre_ping=not _is_sqlite,
    connect_args=_connect_args,
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
