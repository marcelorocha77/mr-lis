"""Robô de integração — worker assíncrono que mantém conexões com todos os equipamentos
ativos, recebe mensagens, transforma em resultados e grava no banco.

Também expõe fila de saída (worklist / ordens) para os equipamentos que suportam.

Uso:
    docker compose exec backend python -m app.modules.mrinterface.robot

Em produção, roda como serviço separado (systemd / kubernetes deployment).
"""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.models.equipment import Equipment, InterfaceMessage
from app.models.exam import Exam
from app.models.request import Request, RequestItem
from app.models.result import Result
from app.modules.mrinterface.drivers import DRIVER_REGISTRY, get_driver
from app.modules.mrinterface.drivers.base import BaseDriver, DriverResult
from app.modules.mrinterface.protocols.file_watcher import watch_dir
from app.modules.mrinterface.protocols.hl7_mllp import mllp_server, parse_hl7

log = logging.getLogger("mr.robot")


class EquipmentWorker:
    """Um worker por equipamento ativo. Mantém o loop de conexão e trata retries."""

    def __init__(self, equipment: Equipment):
        self.equipment = equipment
        self.driver_cls = get_driver(equipment.driver)
        self.driver: BaseDriver | None = self.driver_cls(equipment.connection) if self.driver_cls else None
        self._task: asyncio.Task | None = None
        self._server = None
        self._stop = asyncio.Event()

    async def start(self):
        if not self.driver:
            log.error("driver %s not found for equipment %s", self.equipment.driver, self.equipment.code)
            return
        proto = self.equipment.protocol
        log.info("starting worker: %s (%s / %s)", self.equipment.code, self.equipment.driver, proto)
        self._task = asyncio.create_task(self._run(proto))

    async def _run(self, proto: str):
        backoff = 1
        while not self._stop.is_set():
            try:
                if proto == "hl7_mllp":
                    await self._run_mllp_server()
                elif proto == "astm_tcp":
                    await self._run_astm_client()
                elif proto == "file":
                    await self._run_file()
                else:
                    log.warning("protocol %s not implemented yet", proto)
                    await asyncio.sleep(30)
                backoff = 1
            except Exception as e:
                log.exception("worker %s error: %s", self.equipment.code, e)
                await self._touch_error(str(e))
                await asyncio.sleep(min(backoff, 60))
                backoff *= 2

    async def _run_mllp_server(self):
        """Servidor MLLP: escuta na porta configurada, atende conexões dos equipamentos."""
        conn = self.equipment.connection
        host = conn.get("bind", "0.0.0.0")
        port = int(conn.get("port", 5000))

        async def on_message(payload: str) -> str:
            await self._handle_inbound(payload, "hl7_mllp")
            ack = self.driver.build_ack(payload) if self.driver else None
            return ack or ""

        self._server = await mllp_server(host, port, on_message)
        log.info("MLLP listening on %s:%d for %s", host, port, self.equipment.code)
        async with self._server:
            await self._stop.wait()

    async def _run_astm_client(self):
        """Client ASTM TCP: conecta e fica lendo transmissões do equipamento."""
        from app.modules.mrinterface.protocols.astm import ASTMClient

        conn = self.equipment.connection
        host = conn.get("host", "127.0.0.1")
        port = int(conn.get("port", 4001))
        client = ASTMClient(host, port)
        await client.connect()
        try:
            while not self._stop.is_set():
                payload = await client.read_transmission()
                if payload:
                    await self._handle_inbound(payload, "astm_tcp")
        finally:
            await client.close()

    async def _run_file(self):
        """Watch dir mode — legado por arquivo."""
        conn = self.equipment.connection
        path = conn.get("watch_dir")
        if not path:
            log.error("equipment %s configured as file but no watch_dir", self.equipment.code)
            return

        async def on_file(fp, data: bytes):
            await self._handle_inbound(data.decode("latin1", errors="replace"), "file")

        await watch_dir(path, on_file, pattern=conn.get("pattern", "*.txt"),
                        poll_interval=float(conn.get("poll_interval", 2.0)),
                        move_after=conn.get("done_dir"))

    async def _handle_inbound(self, payload: str, protocol: str):
        if not self.driver:
            return
        try:
            results = self.driver.parse_message(payload)
        except Exception as e:
            await self._log_message(protocol, payload, direction="rx", status="parse_error", error=str(e))
            return

        async with AsyncSessionLocal() as db:
            await self._log_message(protocol, payload, direction="rx", status="ok", db=db)
            for r in results:
                await self._apply_result(db, r)
            await db.commit()

        # atualizar last_seen
        async with AsyncSessionLocal() as db:
            eq = await db.get(Equipment, self.equipment.id)
            if eq:
                eq.last_seen = datetime.now(timezone.utc)
                eq.last_error = None
                await db.commit()

    async def _apply_result(self, db: AsyncSession, r: DriverResult):
        """Grava resultado no banco associando ao RequestItem correto."""
        req_stmt = select(Request).where(
            Request.tenant_id == self.equipment.tenant_id,
            Request.number == r.request_number,
        )
        req = (await db.execute(req_stmt)).scalar_one_or_none()
        if not req:
            log.warning("request %s not found for tenant %s", r.request_number, self.equipment.tenant_id)
            return

        exam_stmt = select(Exam).where(
            Exam.tenant_id == self.equipment.tenant_id,
            Exam.code == r.exam_code,
        )
        exam = (await db.execute(exam_stmt)).scalar_one_or_none()
        if not exam:
            log.warning("exam %s not in catalog", r.exam_code)
            return

        ri_stmt = select(RequestItem).where(
            RequestItem.request_id == req.id, RequestItem.exam_id == exam.id
        )
        ri = (await db.execute(ri_stmt)).scalar_one_or_none()
        if not ri:
            return

        existing = (await db.execute(select(Result).where(Result.request_item_id == ri.id))).scalar_one_or_none()
        if existing:
            existing.numeric_value = r.numeric_value
            existing.text_value = r.text_value
            existing.unit = r.unit or existing.unit
            existing.flag = r.flag
            existing.equipment = self.equipment.name
            existing.entered_at = datetime.now(timezone.utc)
            existing.status = "revisar"
        else:
            db.add(Result(
                tenant_id=self.equipment.tenant_id,
                request_item_id=ri.id,
                numeric_value=r.numeric_value,
                text_value=r.text_value,
                unit=r.unit,
                flag=r.flag,
                equipment=self.equipment.name,
                entered_at=datetime.now(timezone.utc),
                status="revisar",
            ))
        ri.status = "resultado_pronto"

    async def _log_message(self, protocol: str, payload: str, direction: str,
                           status: str = "ok", error: str | None = None,
                           db: AsyncSession | None = None):
        msg_type = ""
        req_num = None
        if protocol.startswith("hl7"):
            segs = parse_hl7(payload)
            if segs:
                msh = segs[0]
                msg_type = msh.field(9) if msh.name == "MSH" else ""
            for s in segs:
                if s.name == "OBR":
                    req_num = s.field(3) or s.field(2)
                    break

        msg = InterfaceMessage(
            tenant_id=self.equipment.tenant_id,
            at=datetime.now(timezone.utc),
            equipment_id=self.equipment.id,
            direction=direction,
            protocol=protocol,
            message_type=msg_type,
            raw=payload,
            status=status,
            error=error,
            request_number=req_num,
        )
        if db is None:
            async with AsyncSessionLocal() as sess:
                sess.add(msg)
                await sess.commit()
        else:
            db.add(msg)

    async def _touch_error(self, err: str):
        async with AsyncSessionLocal() as db:
            eq = await db.get(Equipment, self.equipment.id)
            if eq:
                eq.last_error = err[:500]
                await db.commit()

    async def stop(self):
        self._stop.set()
        if self._server:
            self._server.close()
            try:
                await self._server.wait_closed()
            except Exception:
                pass
        if self._task:
            self._task.cancel()


class IntegrationRobot:
    """Orquestra todos os workers de todos os tenants."""

    def __init__(self):
        self.workers: dict[int, EquipmentWorker] = {}
        self._reconcile_task: asyncio.Task | None = None
        self._stop = asyncio.Event()

    async def run(self):
        log.info("MR Integration Robot starting — %d drivers registered", len(DRIVER_REGISTRY))
        self._reconcile_task = asyncio.create_task(self._reconcile_loop())
        await self._stop.wait()
        log.info("stopping robot...")
        for w in list(self.workers.values()):
            await w.stop()

    async def _reconcile_loop(self):
        """A cada 30s, verifica o banco de equipamentos e sincroniza os workers."""
        while not self._stop.is_set():
            try:
                await self._reconcile()
            except Exception:
                log.exception("reconcile error")
            try:
                await asyncio.wait_for(self._stop.wait(), timeout=30)
            except asyncio.TimeoutError:
                pass

    async def _reconcile(self):
        async with AsyncSessionLocal() as db:
            active = (await db.execute(
                select(Equipment).where(Equipment.is_enabled.is_(True))
            )).scalars().all()

        active_ids = {e.id for e in active}
        # parar workers de equipamentos desativados
        for eid in list(self.workers.keys()):
            if eid not in active_ids:
                await self.workers[eid].stop()
                del self.workers[eid]

        # iniciar workers novos
        for eq in active:
            if eq.id not in self.workers:
                w = EquipmentWorker(eq)
                await w.start()
                self.workers[eq.id] = w

    def shutdown(self):
        self._stop.set()


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)-5s [%(name)s] %(message)s",
    )
    robot = IntegrationRobot()
    try:
        await robot.run()
    except (KeyboardInterrupt, asyncio.CancelledError):
        pass


if __name__ == "__main__":
    asyncio.run(main())
