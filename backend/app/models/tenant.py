from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models._mixins import TimestampMixin


class Tenant(Base, TimestampMixin):
    """A single laboratory customer (SaaS tenant)."""

    __tablename__ = "tenants"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(60), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    cnpj: Mapped[str | None] = mapped_column(String(20))
    plan: Mapped[str] = mapped_column(String(20), default="starter", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
