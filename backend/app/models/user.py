from sqlalchemy import Boolean, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models._mixins import TenantMixin, TimestampMixin


class User(Base, TenantMixin, TimestampMixin):
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("tenant_id", "email", name="uq_users_tenant_email"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(30), default="tecnico", nullable=False)
    # roles: admin, tecnico, bioquimico, medico, recepcao, faturamento
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
