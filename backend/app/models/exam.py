from decimal import Decimal
from sqlalchemy import Boolean, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models._mixins import TenantMixin, TimestampMixin


class Exam(Base, TenantMixin, TimestampMixin):
    """Cadastro de exames (catálogo)."""

    __tablename__ = "exams"
    __table_args__ = (
        UniqueConstraint("tenant_id", "code", name="uq_exams_tenant_code"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    section: Mapped[str | None] = mapped_column(String(60))  # setor: bioquimica, hematologia, imunologia...
    material: Mapped[str | None] = mapped_column(String(60))  # sangue, urina, fezes...
    method: Mapped[str | None] = mapped_column(String(120))  # método analítico
    unit: Mapped[str | None] = mapped_column(String(20))  # unidade de medida
    turnaround_hours: Mapped[int] = mapped_column(Integer, default=24, nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0.00"), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
