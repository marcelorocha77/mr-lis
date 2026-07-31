from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models._mixins import TenantMixin, TimestampMixin


class Sample(Base, TenantMixin, TimestampMixin):
    """Amostra biológica coletada."""

    __tablename__ = "samples"

    id: Mapped[int] = mapped_column(primary_key=True)
    barcode: Mapped[str] = mapped_column(String(40), nullable=False, index=True, unique=True)
    request_id: Mapped[int] = mapped_column(ForeignKey("requests.id"), nullable=False, index=True)
    material: Mapped[str] = mapped_column(String(60), nullable=False)
    tube_type: Mapped[str | None] = mapped_column(String(40))
    collected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    received_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(20), default="pendente", nullable=False)
    # pendente, coletada, recebida, processando, descartada
    notes: Mapped[str | None] = mapped_column(String(500))
