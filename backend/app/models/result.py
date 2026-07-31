from datetime import datetime
from decimal import Decimal
from sqlalchemy import DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models._mixins import TenantMixin, TimestampMixin


class Result(Base, TenantMixin, TimestampMixin):
    """Resultado de um exame (RequestItem)."""

    __tablename__ = "results"

    id: Mapped[int] = mapped_column(primary_key=True)
    request_item_id: Mapped[int] = mapped_column(
        ForeignKey("request_items.id"), nullable=False, index=True, unique=True
    )
    numeric_value: Mapped[Decimal | None] = mapped_column(Numeric(18, 6))
    text_value: Mapped[str | None] = mapped_column(String(2000))
    unit: Mapped[str | None] = mapped_column(String(20))
    reference_range: Mapped[str | None] = mapped_column(String(120))
    flag: Mapped[str | None] = mapped_column(String(10))  # N, H, L, HH, LL, A
    method: Mapped[str | None] = mapped_column(String(120))
    equipment: Mapped[str | None] = mapped_column(String(60))

    entered_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    entered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    released_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    released_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(20), default="rascunho", nullable=False)
    # rascunho, revisar, liberado, retificado
