"""ASTM E1381 / E1394 — protocolo clássico para analisadores mais antigos
(Cobas Integra, Architect, Advia, Dimension, Immulite, Vitros, Alifax).

Estrutura mínima:
- Frames delimitados por STX (0x02) e ETX/ETB (0x03/0x17), com checksum.
- Registros H (header), P (patient), O (order), R (result), C (comment), L (terminator).
"""
from __future__ import annotations

import asyncio
from dataclasses import dataclass, field

STX = b"\x02"
ETX = b"\x03"
ETB = b"\x17"
EOT = b"\x04"
ENQ = b"\x05"
ACK = b"\x06"
NAK = b"\x15"
CR = b"\x0d"
LF = b"\x0a"


def checksum(data: bytes) -> str:
    """Checksum ASTM: soma dos bytes mod 256 → hex de 2 dígitos maiúsculo."""
    return f"{sum(data) & 0xFF:02X}"


def frame(seq: int, records: list[str], last: bool = True) -> bytes:
    body = "\r".join(records) + "\r"
    end = ETX if last else ETB
    inner = f"{seq % 8}{body}".encode("latin1") + end
    return STX + inner + checksum(inner).encode("ascii") + CR + LF


@dataclass
class ASTMRecord:
    type: str  # H, P, O, R, C, L, Q, M
    fields: list[str] = field(default_factory=list)

    def field_at(self, idx: int) -> str:
        return self.fields[idx] if idx < len(self.fields) else ""


def parse_records(payload: str) -> list[ASTMRecord]:
    """Extrai registros ASTM de um payload textual."""
    records: list[ASTMRecord] = []
    for line in payload.replace("\r\n", "\r").split("\r"):
        line = line.strip()
        if not line or len(line) < 2:
            continue
        # remover números sequenciais no início se houver
        while line and line[0].isdigit():
            line = line[1:]
        rtype = line[0]
        rest = line[1:].split("|") if len(line) > 1 else []
        records.append(ASTMRecord(type=rtype, fields=rest))
    return records


class ASTMClient:
    """Cliente ASTM sobre TCP com handshake ENQ/ACK simplificado."""

    def __init__(self, host: str, port: int, timeout: float = 30.0):
        self.host = host
        self.port = port
        self.timeout = timeout
        self._reader: asyncio.StreamReader | None = None
        self._writer: asyncio.StreamWriter | None = None
        self._seq = 1

    async def connect(self):
        self._reader, self._writer = await asyncio.wait_for(
            asyncio.open_connection(self.host, self.port), self.timeout
        )

    async def _read_byte(self) -> bytes:
        assert self._reader
        b = await asyncio.wait_for(self._reader.read(1), self.timeout)
        return b

    async def send_records(self, records: list[str]) -> bool:
        """Envia records via handshake ASTM. Retorna True se ACK recebido."""
        assert self._writer
        self._writer.write(ENQ)
        await self._writer.drain()
        resp = await self._read_byte()
        if resp != ACK:
            return False
        self._writer.write(frame(self._seq, records, last=True))
        await self._writer.drain()
        self._seq += 1
        resp = await self._read_byte()
        self._writer.write(EOT)
        await self._writer.drain()
        return resp == ACK

    async def read_transmission(self) -> str:
        """Lê uma transmissão completa (ENQ → frames → EOT) e retorna o payload."""
        assert self._reader and self._writer
        buf = b""
        collected = ""
        while True:
            chunk = await asyncio.wait_for(self._reader.read(4096), self.timeout)
            if not chunk:
                break
            buf += chunk
            while buf:
                if buf[:1] == ENQ:
                    self._writer.write(ACK)
                    await self._writer.drain()
                    buf = buf[1:]
                    continue
                if buf[:1] == EOT:
                    buf = buf[1:]
                    return collected
                stx = buf.find(STX)
                if stx < 0:
                    buf = b""
                    break
                end = buf.find(CR, stx)
                if end < 0:
                    break
                frame_body = buf[stx + 1 : end - 3]  # remove trailing ETX/ETB + checksum
                # remove seq number (first byte)
                collected += frame_body[1:].decode("latin1", errors="replace") + "\r"
                self._writer.write(ACK)
                await self._writer.drain()
                buf = buf[end + 2 :]
        return collected

    async def close(self):
        if self._writer:
            self._writer.close()
            try:
                await self._writer.wait_closed()
            except Exception:
                pass
