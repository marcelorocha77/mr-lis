from datetime import datetime
from decimal import Decimal
from sqlalchemy import DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models._mixins import TenantMixin, TimestampMixin


class Request(Base, TenantMixin, TimestampMixin):
    """Requisição / pedido de exames (a "ficha")."""

    __tablename__ = "requests"

    id: Mapped[int] = mapped_column(primary_key=True)
    number: Mapped[str] = mapped_column(String(20), nullable=False, index=True)

    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"), nullable=False, index=True)
    doctor_id: Mapped[int | None] = mapped_column(ForeignKey("doctors.id"))
    insurance_id: Mapped[int | None] = mapped_column(ForeignKey("insurances.id"))

    collection_datetime: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    received_datetime: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    status: Mapped[str] = mapped_column(String(20), default="aberta", nullable=False)
    # aberta, coletada, em_processo, liberada, cancelada, entregue
    clinical_info: Mapped[str | None] = mapped_column(String(2000))

    items: Mapped[list["RequestItem"]] = relationship(
        "RequestItem", back_populates="request", cascade="all, delete-orphan"
    )


class RequestItem(Base, TenantMixin, TimestampMixin):
    """Cada exame pedido dentro de uma requisição."""

    __tablename__ = "request_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    request_id: Mapped[int] = mapped_column(ForeignKey("requests.id"), nullable=False, index=True)
    exam_id: Mapped[int] = mapped_column(ForeignKey("exams.id"), nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0.00"), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="pendente", nullable=False)
    # pendente, coletado, em_analise, resultado_pronto, liberado, cancelado

    request: Mapped["Request"] = relationship("Request", back_populates="items")
