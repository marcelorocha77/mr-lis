from sqlalchemy import String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models._mixins import TenantMixin, TimestampMixin


class Doctor(Base, TenantMixin, TimestampMixin):
    """Solicitantes (médicos que pedem exames)."""

    __tablename__ = "doctors"
    __table_args__ = (
        UniqueConstraint("tenant_id", "crm", "crm_uf", name="uq_doctors_tenant_crm"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    crm: Mapped[str] = mapped_column(String(15), nullable=False, index=True)
    crm_uf: Mapped[str] = mapped_column(String(2), nullable=False)
    specialty: Mapped[str | None] = mapped_column(String(100))
    phone: Mapped[str | None] = mapped_column(String(20))
    email: Mapped[str | None] = mapped_column(String(200))
