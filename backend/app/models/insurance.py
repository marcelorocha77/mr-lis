from sqlalchemy import Boolean, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models._mixins import TenantMixin, TimestampMixin


class Insurance(Base, TenantMixin, TimestampMixin):
    """Convênios / operadoras."""

    __tablename__ = "insurances"
    __table_args__ = (
        UniqueConstraint("tenant_id", "code", name="uq_insurances_tenant_code"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    ans_code: Mapped[str | None] = mapped_column(String(20))  # código ANS (TISS)
    price_table: Mapped[str | None] = mapped_column(String(30))  # AMB, TUSS etc.
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
