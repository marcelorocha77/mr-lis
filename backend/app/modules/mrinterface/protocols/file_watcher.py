"""Integração por arquivos — comum em equipamentos antigos e integrações batch.
O equipamento grava um arquivo (CSV, TXT, HL7 em arquivo) numa pasta compartilhada.
"""
from __future__ import annotations

import asyncio
from pathlib import Path


async def watch_dir(
    path: str,
    on_file,          # async (path: Path, content: bytes) -> None
    pattern: str = "*",
    poll_interval: float = 2.0,
    move_after: str | None = None,  # pasta para mover após processar (evita reprocessamento)
):
    """Polling simples de diretório. Simples de portar para inotify/ReadDirectoryChanges depois."""
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    done_dir = Path(move_after) if move_after else None
    if done_dir:
        done_dir.mkdir(parents=True, exist_ok=True)

    seen: set[str] = set()
    while True:
        try:
            for f in sorted(p.glob(pattern)):
                if not f.is_file():
                    continue
                key = f"{f.name}:{f.stat().st_size}:{int(f.stat().st_mtime)}"
                if key in seen:
                    continue
                seen.add(key)
                try:
                    data = f.read_bytes()
                except OSError:
                    continue
                await on_file(f, data)
                if done_dir:
                    try:
                        f.rename(done_dir / f.name)
                    except OSError:
                        pass
        except Exception:
            pass
        await asyncio.sleep(poll_interval)
