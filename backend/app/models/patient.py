from datetime import date
from sqlalchemy import Date, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models._mixins import TenantMixin, TimestampMixin


class Patient(Base, TenantMixin, TimestampMixin):
    __tablename__ = "patients"
    __table_args__ = (
        UniqueConstraint("tenant_id", "cpf", name="uq_patients_tenant_cpf"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    cpf: Mapped[str | None] = mapped_column(String(14), index=True)
    full_name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    social_name: Mapped[str | None] = mapped_column(String(200))
    birth_date: Mapped[date | None] = mapped_column(Date)
    sex: Mapped[str | None] = mapped_column(String(1))  # M / F / I
    phone: Mapped[str | None] = mapped_column(String(20))
    email: Mapped[str | None] = mapped_column(String(200))
    mother_name: Mapped[str | None] = mapped_column(String(200))

    address_street: Mapped[str | None] = mapped_column(String(200))
    address_number: Mapped[str | None] = mapped_column(String(20))
    address_complement: Mapped[str | None] = mapped_column(String(100))
    address_district: Mapped[str | None] = mapped_column(String(100))
    address_city: Mapped[str | None] = mapped_column(String(100))
    address_state: Mapped[str | None] = mapped_column(String(2))
    address_zip: Mapped[str | None] = mapped_column(String(10))
