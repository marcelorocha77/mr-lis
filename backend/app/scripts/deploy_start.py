"""Entrypoint de produção — roda migrations + seed (idempotente) + uvicorn.

Usado no deploy do Fly.io. Localmente, você continua usando `uvicorn app.main:app`
direto no `docker-compose.yml` ou no dev sem Docker.
"""
import asyncio
import logging
import os
import sys

from app.core.database import Base, engine
from app.models import *  # noqa: F401,F403  register all mapped classes
from app.scripts.seed import main as run_seed

log = logging.getLogger("mr.deploy")


async def ensure_schema_and_seed():
    log.info("Creating schema (create_all)...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    log.info("Running seed (idempotent)...")
    try:
        await run_seed()
    except Exception as e:
        log.warning("seed skipped: %s", e)


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)-5s [%(name)s] %(message)s",
    )
    asyncio.run(ensure_schema_and_seed())

    # substitui o processo pelo uvicorn (evita processo Python idle)
    port = os.environ.get("PORT", "8000")
    args = ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", port]
    os.execvp(args[0], args)


if __name__ == "__main__":
    main()
