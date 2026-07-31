"""Modelos do MRQuality — port das entidades do TMQuality:
Manufacturer, Method, QcLot, QcAnalyte, QcRun, WestgardRule,
QcViolation, CorrectiveAction, EquipmentMaintenance.
"""
from datetime import date, datetime
from decimal import Decimal
from sqlalchemy import (
    Boolean, Date, DateTime, ForeignKey, Integer, JSON, Numeric, String, UniqueConstraint, func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models._mixins import TenantMixin, TimestampMixin


# ---------- Cadastros auxiliares ----------
class Manufacturer(Base, TenantMixin, TimestampMixin):
    """Fabricante de material de controle / kit (Bio-Rad, Randox, Roche, etc.)."""
    __tablename__ = "manufacturers"
    __table_args__ = (UniqueConstraint("tenant_id", "name", name="uq_manufacturers_tenant_name"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    country: Mapped[str | None] = mapped_column(String(60))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class Method(Base, TenantMixin, TimestampMixin):
    """Método analítico padronizado (Enzimático hexoquinase, IFCC UV, Quimiluminescência…)."""
    __tablename__ = "methods"
    __table_args__ = (UniqueConstraint("tenant_id", "name", name="uq_methods_tenant_name"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    principle: Mapped[str | None] = mapped_column(String(200))  # princípio analítico
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


# ---------- Lote de controle ----------
class QcLot(Base, TenantMixin, TimestampMixin):
    """Lote de material de controle interno (ex.: Bio-Rad Multiqual lote #12345)."""
    __tablename__ = "qc_lots"
    __table_args__ = (UniqueConstraint("tenant_id", "lot_number", name="uq_qc_lots_tenant_lot"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    manufacturer_id: Mapped[int | None] = mapped_column(ForeignKey("manufacturers.id"))
    product_name: Mapped[str] = mapped_column(String(200), nullable=False)
    lot_number: Mapped[str] = mapped_column(String(60), nullable=False, index=True)
    level: Mapped[str] = mapped_column(String(20), nullable=False)  # QC1, QC2, QC3 (nível)
    expiry_date: Mapped[date | None] = mapped_column(Date)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


# ---------- Controle-Exame (setup Levey-Jennings por analito) ----------
class QcAnalyte(Base, TenantMixin, TimestampMixin):
    """Configuração de QC por analito × lote × equipamento.
    Traz a média, desvio-padrão (SD) e coeficiente de variação (CV) alvo,
    além das regras Westgard ativas.
    """
    __tablename__ = "qc_analytes"
    __table_args__ = (
        UniqueConstraint(
            "tenant_id", "qc_lot_id", "exam_id", "equipment_id",
            name="uq_qc_analytes_lot_exam_eq",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    qc_lot_id: Mapped[int] = mapped_column(ForeignKey("qc_lots.id"), nullable=False, index=True)
    exam_id: Mapped[int] = mapped_column(ForeignKey("exams.id"), nullable=False, index=True)
    equipment_id: Mapped[int | None] = mapped_column(ForeignKey("equipments.id"), index=True)
    method_id: Mapped[int | None] = mapped_column(ForeignKey("methods.id"))

    # valores de bula (do fabricante) — usados como fallback quando não há histórico
    package_insert_mean: Mapped[Decimal | None] = mapped_column(Numeric(18, 6))
    package_insert_sd: Mapped[Decimal | None] = mapped_column(Numeric(18, 6))

    # valores internos (calculados do histórico após ≥20 corridas)
    internal_mean: Mapped[Decimal | None] = mapped_column(Numeric(18, 6))
    internal_sd: Mapped[Decimal | None] = mapped_column(Numeric(18, 6))
    internal_cv: Mapped[Decimal | None] = mapped_column(Numeric(8, 4))  # %

    # meta (limite de qualidade — TEa: erro total permitido) para cálculo Sigma
    tea_percent: Mapped[Decimal | None] = mapped_column(Numeric(8, 4))

    # regras Westgard ativas (lista de códigos: 1_3s, 2_2s, R_4s, 4_1s, 10x…)
    active_rules: Mapped[dict] = mapped_column(JSON, default=dict)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


# ---------- Dosagem do controle (cada leitura) ----------
class QcRun(Base, TenantMixin, TimestampMixin):
    """Cada leitura de material de controle. É este o ponto no gráfico Levey-Jennings."""
    __tablename__ = "qc_runs"

    id: Mapped[int] = mapped_column(primary_key=True)
    qc_analyte_id: Mapped[int] = mapped_column(ForeignKey("qc_analytes.id"), nullable=False, index=True)
    run_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True,
                                              server_default=func.now())
    value: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False)
    z_score: Mapped[Decimal | None] = mapped_column(Numeric(8, 4))     # calculado no lançamento
    equipment_batch: Mapped[str | None] = mapped_column(String(60))    # lote reagente
    operator_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    is_valid: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    # motivo de invalidação (se aplicável) — usuário pode marcar como "outlier justificado"
    invalid_reason: Mapped[str | None] = mapped_column(String(200))
    notes: Mapped[str | None] = mapped_column(String(500))


# ---------- Regras Westgard aplicadas ----------
class WestgardRule(Base):
    """Enum estático de regras Westgard suportadas. Populada por seed."""
    __tablename__ = "westgard_rules"

    code: Mapped[str] = mapped_column(String(10), primary_key=True)  # 1_2s, 1_3s, 2_2s, R_4s, 4_1s, 10x, 8x, 12x
    description: Mapped[str] = mapped_column(String(200), nullable=False)
    kind: Mapped[str] = mapped_column(String(15), nullable=False)     # warning | rejection


# ---------- Violação detectada ----------
class QcViolation(Base, TenantMixin, TimestampMixin):
    """Violação de regra Westgard detectada em um QcRun."""
    __tablename__ = "qc_violations"

    id: Mapped[int] = mapped_column(primary_key=True)
    qc_run_id: Mapped[int] = mapped_column(ForeignKey("qc_runs.id"), nullable=False, index=True)
    rule_code: Mapped[str] = mapped_column(ForeignKey("westgard_rules.code"), nullable=False)
    severity: Mapped[str] = mapped_column(String(15), nullable=False)  # warning | rejection
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    resolved_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    corrective_action_id: Mapped[int | None] = mapped_column(ForeignKey("corrective_actions.id"))
    notes: Mapped[str | None] = mapped_column(String(500))


# ---------- Ação corretiva ----------
class RootCause(Base, TenantMixin, TimestampMixin):
    """Causa raiz catalogada (reagente vencido, calibração fora, contaminação…)."""
    __tablename__ = "root_causes"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    category: Mapped[str | None] = mapped_column(String(60))  # reagente / equipamento / operador / amostra


class CorrectiveAction(Base, TenantMixin, TimestampMixin):
    """Ação corretiva executada em resposta a uma violação de QC."""
    __tablename__ = "corrective_actions"

    id: Mapped[int] = mapped_column(primary_key=True)
    root_cause_id: Mapped[int | None] = mapped_column(ForeignKey("root_causes.id"))
    action: Mapped[str] = mapped_column(String(500), nullable=False)
    executed_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    executed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    effectiveness: Mapped[str | None] = mapped_column(String(15))  # eficaz / não-eficaz / parcial


# ---------- Diário de equipamento (calibração, manutenção) ----------
class EquipmentMaintenance(Base, TenantMixin, TimestampMixin):
    """Diário do equipamento — TMQuality → TFMDIARIOEQUIPAMENTOS."""
    __tablename__ = "equipment_maintenance"

    id: Mapped[int] = mapped_column(primary_key=True)
    equipment_id: Mapped[int] = mapped_column(ForeignKey("equipments.id"), nullable=False, index=True)
    kind: Mapped[str] = mapped_column(String(30), nullable=False)  # calibracao / preventiva / corretiva / limpeza
    performed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    performed_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    description: Mapped[str | None] = mapped_column(String(2000))
    next_due: Mapped[date | None] = mapped_column(Date)
