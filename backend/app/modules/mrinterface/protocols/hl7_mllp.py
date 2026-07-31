"""HL7 v2 sobre MLLP (Minimal Lower-Layer Protocol) — protocolo mais comum
para integração com analisadores clínicos modernos (Cobas, Sysmex, Architect, etc.).

MLLP framing:
    <VT> ... payload HL7 ... <FS><CR>
    VT = 0x0B, FS = 0x1C, CR = 0x0D
"""
from __future__ import annotations

import asyncio
from dataclasses import dataclass

VT = b"\x0b"
FS = b"\x1c"
CR = b"\x0d"


def frame(payload: str) -> bytes:
    return VT + payload.encode("utf-8") + FS + CR


def unframe(buf: bytes) -> tuple[list[str], bytes]:
    """Extrai mensagens completas do buffer e retorna o restante."""
    messages: list[str] = []
    while True:
        start = buf.find(VT)
        if start < 0:
            return messages, b""
        end = buf.find(FS + CR, start + 1)
        if end < 0:
            return messages, buf[start:]
        messages.append(buf[start + 1 : end].decode("utf-8", errors="replace"))
        buf = buf[end + 2 :]


@dataclass
class HL7Segment:
    name: str
    fields: list[str]

    def field(self, idx: int) -> str:
        return self.fields[idx] if idx < len(self.fields) else ""

    def __repr__(self):
        return f"{self.name}|{'|'.join(self.fields[1:])}"


def parse_hl7(payload: str) -> list[HL7Segment]:
    """Parser HL7 v2 mínimo (nível de segmentos e campos, delimitador padrão | ^ ~ \\ &)."""
    segments: list[HL7Segment] = []
    for line in payload.replace("\r\n", "\r").replace("\n", "\r").split("\r"):
        if not line:
            continue
        parts = line.split("|")
        segments.append(HL7Segment(name=parts[0], fields=parts))
    return segments


def build_ack(msh: HL7Segment, code: str = "AA", text: str = "") -> str:
    """Constrói ACK simples (MSH+MSA)."""
    control_id = msh.field(9)
    sending_app = msh.field(2)
    sending_facility = msh.field(3)
    receiving_app = msh.field(4)
    receiving_facility = msh.field(5)
    msh_out = (
        f"MSH|^~\\&|{receiving_app}|{receiving_facility}|{sending_app}|{sending_facility}"
        f"|{msh.field(6)}||ACK|{control_id}|P|2.5"
    )
    msa = f"MSA|{code}|{control_id}|{text}"
    return msh_out + "\r" + msa


class MLLPClient:
    """Cliente MLLP para envio de mensagens HL7 e leitura de respostas/ACK."""

    def __init__(self, host: str, port: int, timeout: float = 30.0):
        self.host = host
        self.port = port
        self.timeout = timeout
        self._reader: asyncio.StreamReader | None = None
        self._writer: asyncio.StreamWriter | None = None

    async def connect(self):
        self._reader, self._writer = await asyncio.wait_for(
            asyncio.open_connection(self.host, self.port), self.timeout
        )

    async def send(self, payload: str) -> str:
        assert self._writer and self._reader
        self._writer.write(frame(payload))
        await self._writer.drain()
        buf = b""
        while True:
            chunk = await asyncio.wait_for(self._reader.read(4096), self.timeout)
            if not chunk:
                break
            buf += chunk
            msgs, buf = unframe(buf)
            if msgs:
                return msgs[0]
        return ""

    async def close(self):
        if self._writer:
            self._writer.close()
            try:
                await self._writer.wait_closed()
            except Exception:
                pass


async def mllp_server(
    host: str,
    port: int,
    on_message,  # async (payload: str) -> str  (returns ACK payload)
):
    """Inicia servidor MLLP; chama on_message para cada mensagem recebida."""

    async def _handle(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        buf = b""
        try:
            while True:
                chunk = await reader.read(4096)
                if not chunk:
                    return
                buf += chunk
                msgs, buf = unframe(buf)
                for m in msgs:
                    ack = await on_message(m)
                    if ack:
                        writer.write(frame(ack))
                        await writer.drain()
        except Exception:
            pass
        finally:
            writer.close()

    server = await asyncio.start_server(_handle, host, port)
    return server
