from datetime import datetime
from sqlalchemy import Boolean, DateTime, Integer, String, UniqueConstraint, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models._mixins import TenantMixin, TimestampMixin


class Equipment(Base, TenantMixin, TimestampMixin):
    """Equipamento clínico conectado ao LIS (analisador, coagulômetro, etc.)."""

    __tablename__ = "equipments"
    __table_args__ = (
        UniqueConstraint("tenant_id", "code", name="uq_equipments_tenant_code"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    driver: Mapped[str] = mapped_column(String(60), nullable=False)
    # ex: roche_cobas6000, sysmex_xn, abbott_architect, siemens_advia2120, generic_hl7 ...

    protocol: Mapped[str] = mapped_column(String(20), nullable=False, default="hl7_mllp")
    # hl7_mllp / astm_tcp / astm_serial / file / rest

    connection: Mapped[dict] = mapped_column(JSON, default=dict)
    # dict com host, port, serial_port, baud, watch_dir, extras específicos do driver

    section: Mapped[str | None] = mapped_column(String(60))
    # bioquimica / hematologia / imunologia / hormonios / coagulacao / urinalise / microbiologia

    direction: Mapped[str] = mapped_column(String(20), default="bidirectional")
    # inbound / outbound / bidirectional

    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_seen: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_error: Mapped[str | None] = mapped_column(String(500))
    pending_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)


class InterfaceMessage(Base, TenantMixin):
    """Log de mensagens trocadas com equipamentos (HL7/ASTM)."""

    __tablename__ = "interface_messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    equipment_id: Mapped[int | None] = mapped_column(Integer, index=True)
    direction: Mapped[str] = mapped_column(String(10), nullable=False)  # rx / tx
    protocol: Mapped[str] = mapped_column(String(20), nullable=False)
    message_type: Mapped[str | None] = mapped_column(String(20))  # ORU^R01, ORM^O01, ...
    raw: Mapped[str] = mapped_column(String, nullable=False)  # payload cru
    parsed: Mapped[dict | None] = mapped_column(JSON)  # extração
    status: Mapped[str] = mapped_column(String(20), default="ok", nullable=False)
    # ok / parse_error / ack_error / duplicated
    request_number: Mapped[str | None] = mapped_column(String(20), index=True)
    error: Mapped[str | None] = mapped_column(String(500))
