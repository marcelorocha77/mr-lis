"""Bootstrap para dev local sem Docker.
Cria as tabelas via create_all() (contornando Alembic) e roda o seed.

Uso:
    cd D:/projeto\ lis/backend
    python -m app.scripts.bootstrap_sqlite
"""
import asyncio

from app.core.database import Base, engine
from app.models import *  # noqa: F401,F403  register all mapped classes
from app.scripts.seed import main as run_seed


async def create_schema():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def main():
    print("Creating schema (SQLite)...")
    await create_schema()
    print("Running seed...")
    await run_seed()
    print("Done.")


if __name__ == "__main__":
    asyncio.run(main())
