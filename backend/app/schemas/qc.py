from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict


# ---------- Cadastros ----------
class ManufacturerBase(BaseModel):
    name: str
    country: str | None = None
    is_active: bool = True


class ManufacturerCreate(ManufacturerBase): pass
class ManufacturerOut(ManufacturerBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class MethodBase(BaseModel):
    name: str
    principle: str | None = None
    is_active: bool = True


class MethodCreate(MethodBase): pass
class MethodOut(MethodBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


# ---------- Lote QC ----------
class QcLotBase(BaseModel):
    manufacturer_id: int | None = None
    product_name: str
    lot_number: str
    level: str
    expiry_date: date | None = None
    is_active: bool = True


class QcLotCreate(QcLotBase): pass


class QcLotOut(QcLotBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


# ---------- QC Analyte ----------
class QcAnalyteBase(BaseModel):
    qc_lot_id: int
    exam_id: int
    equipment_id: int | None = None
    method_id: int | None = None
    package_insert_mean: Decimal | None = None
    package_insert_sd: Decimal | None = None
    internal_mean: Decimal | None = None
    internal_sd: Decimal | None = None
    internal_cv: Decimal | None = None
    tea_percent: Decimal | None = None
    active_rules: dict = {}
    is_active: bool = True


class QcAnalyteCreate(QcAnalyteBase): pass


class QcAnalyteOut(QcAnalyteBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


# ---------- QC Run ----------
class QcRunCreate(BaseModel):
    qc_analyte_id: int
    value: Decimal
    equipment_batch: str | None = None
    notes: str | None = None


class QcRunOut(BaseModel):
    id: int
    qc_analyte_id: int
    run_at: datetime
    value: Decimal
    z_score: Decimal | None
    equipment_batch: str | None
    operator_id: int | None
    is_valid: bool
    notes: str | None
    model_config = ConfigDict(from_attributes=True)


class QcViolationOut(BaseModel):
    id: int
    qc_run_id: int
    rule_code: str
    severity: str
    resolved_at: datetime | None
    corrective_action_id: int | None
    notes: str | None
    model_config = ConfigDict(from_attributes=True)


# ---------- Análises ----------
class LeveyJenningsPoint(BaseModel):
    run_id: int
    at: datetime
    value: Decimal
    z_score: Decimal | None
    violations: list[str] = []


class LeveyJenningsResponse(BaseModel):
    analyte_id: int
    exam_code: str
    lot_number: str
    level: str
    mean: Decimal | None
    sd: Decimal | None
    upper_1s: Decimal | None
    lower_1s: Decimal | None
    upper_2s: Decimal | None
    lower_2s: Decimal | None
    upper_3s: Decimal | None
    lower_3s: Decimal | None
    points: list[LeveyJenningsPoint]
    stats: dict


class SigmaMetric(BaseModel):
    analyte_id: int
    exam_code: str
    exam_name: str
    lot_number: str
    level: str
    mean: Decimal | None
    sd: Decimal | None
    cv_percent: Decimal | None
    bias_percent: Decimal | None
    tea_percent: Decimal | None
    sigma: Decimal | None
    classification: str  # world-class / aceitavel / ruim / na


# ---------- Ação corretiva ----------
class CorrectiveActionCreate(BaseModel):
    root_cause_id: int | None = None
    action: str
    effectiveness: str | None = None


class CorrectiveActionOut(CorrectiveActionCreate):
    id: int
    executed_at: datetime
    executed_by_id: int | None
    model_config = ConfigDict(from_attributes=True)


class RootCauseCreate(BaseModel):
    name: str
    category: str | None = None


class RootCauseOut(RootCauseCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)


# ---------- Manutenção equipamento ----------
class MaintenanceCreate(BaseModel):
    equipment_id: int
    kind: str
    description: str | None = None
    next_due: date | None = None


class MaintenanceOut(MaintenanceCreate):
    id: int
    performed_at: datetime
    performed_by_id: int | None
    model_config = ConfigDict(from_attributes=True)
