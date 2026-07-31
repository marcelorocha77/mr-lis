"""MRQuality — port das funcoes do TMQuality:

Cadastros:
- Fabricantes / Métodos / Lotes de controle / Regras Westgard
- QC-Analito (associação lote × exame × equipamento com média/SD/regras)
- Causas raiz

Operação:
- Lançar dosagem QC (QcRun) — aplica Westgard automaticamente
- Registrar ação corretiva
- Diário do equipamento (calibração, manutenção)

Análises:
- Levey-Jennings (série de pontos + linhas ±1/2/3 SD)
- Sigma-Westgard (métrica σ por analito)
- CV / média interna / média móvel / erro total
- Violações abertas
"""
from datetime import datetime, timezone
from decimal import Decimal
from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import select

from app.core.deps import CurrentUser, DbSession
from app.models.exam import Exam
from app.models.qc import (
    CorrectiveAction, EquipmentMaintenance, Manufacturer, Method,
    QcAnalyte, QcLot, QcRun, QcViolation, RootCause, WestgardRule,
)
from app.modules.mrquality.westgard import (
    ALL_RULES, evaluate, moving_average, sigma_metric, stats_summary, total_error,
)
from app.schemas.qc import (
    CorrectiveActionCreate, CorrectiveActionOut,
    LeveyJenningsPoint, LeveyJenningsResponse,
    MaintenanceCreate, MaintenanceOut,
    ManufacturerCreate, ManufacturerOut,
    MethodCreate, MethodOut,
    QcAnalyteCreate, QcAnalyteOut,
    QcLotCreate, QcLotOut,
    QcRunCreate, QcRunOut,
    QcViolationOut, RootCauseCreate, RootCauseOut,
    SigmaMetric,
)

router = APIRouter(prefix="/mrquality", tags=["mrquality"])


# ==================== CADASTROS ====================
@router.get("/fabricantes", response_model=list[ManufacturerOut])
async def list_manufacturers(user: CurrentUser, db: DbSession):
    stmt = select(Manufacturer).where(Manufacturer.tenant_id == user.tenant_id).order_by(Manufacturer.name)
    return list((await db.execute(stmt)).scalars().all())


@router.post("/fabricantes", response_model=ManufacturerOut, status_code=201)
async def create_manufacturer(payload: ManufacturerCreate, user: CurrentUser, db: DbSession):
    m = Manufacturer(**payload.model_dump(), tenant_id=user.tenant_id)
    db.add(m); await db.flush(); await db.refresh(m)
    return m


@router.get("/metodos", response_model=list[MethodOut])
async def list_methods(user: CurrentUser, db: DbSession):
    stmt = select(Method).where(Method.tenant_id == user.tenant_id).order_by(Method.name)
    return list((await db.execute(stmt)).scalars().all())


@router.post("/metodos", response_model=MethodOut, status_code=201)
async def create_method(payload: MethodCreate, user: CurrentUser, db: DbSession):
    m = Method(**payload.model_dump(), tenant_id=user.tenant_id)
    db.add(m); await db.flush(); await db.refresh(m)
    return m


@router.get("/lotes", response_model=list[QcLotOut])
async def list_lots(user: CurrentUser, db: DbSession):
    stmt = select(QcLot).where(QcLot.tenant_id == user.tenant_id).order_by(QcLot.product_name)
    return list((await db.execute(stmt)).scalars().all())


@router.post("/lotes", response_model=QcLotOut, status_code=201)
async def create_lot(payload: QcLotCreate, user: CurrentUser, db: DbSession):
    lot = QcLot(**payload.model_dump(), tenant_id=user.tenant_id)
    db.add(lot); await db.flush(); await db.refresh(lot)
    return lot


@router.get("/analitos", response_model=list[QcAnalyteOut])
async def list_analytes(user: CurrentUser, db: DbSession):
    stmt = select(QcAnalyte).where(QcAnalyte.tenant_id == user.tenant_id).order_by(QcAnalyte.id.desc())
    return list((await db.execute(stmt)).scalars().all())


@router.post("/analitos", response_model=QcAnalyteOut, status_code=201)
async def create_analyte(payload: QcAnalyteCreate, user: CurrentUser, db: DbSession):
    a = QcAnalyte(**payload.model_dump(), tenant_id=user.tenant_id)
    db.add(a); await db.flush(); await db.refresh(a)
    return a


@router.get("/regras")
async def list_westgard_rules():
    """Enum das regras disponíveis."""
    return [{"code": c, "description": d, "kind": k} for c, d, k in ALL_RULES]


@router.get("/causas-raiz", response_model=list[RootCauseOut])
async def list_root_causes(user: CurrentUser, db: DbSession):
    stmt = select(RootCause).where(RootCause.tenant_id == user.tenant_id).order_by(RootCause.name)
    return list((await db.execute(stmt)).scalars().all())


@router.post("/causas-raiz", response_model=RootCauseOut, status_code=201)
async def create_root_cause(payload: RootCauseCreate, user: CurrentUser, db: DbSession):
    r = RootCause(**payload.model_dump(), tenant_id=user.tenant_id)
    db.add(r); await db.flush(); await db.refresh(r)
    return r


# ==================== OPERAÇÃO ====================
async def _load_runs(db, analyte_id: int, limit: int = 40) -> list[QcRun]:
    stmt = (
        select(QcRun)
        .where(QcRun.qc_analyte_id == analyte_id, QcRun.is_valid.is_(True))
        .order_by(QcRun.run_at.desc())
        .limit(limit)
    )
    rows = list((await db.execute(stmt)).scalars().all())
    rows.reverse()
    return rows


@router.post("/dosagens", response_model=QcRunOut, status_code=201)
async def create_run(payload: QcRunCreate, user: CurrentUser, db: DbSession):
    """Lança dosagem de material de controle. Calcula Z-score e aplica Westgard."""
    analyte = await db.get(QcAnalyte, payload.qc_analyte_id)
    if not analyte or analyte.tenant_id != user.tenant_id:
        raise HTTPException(404, "QC-analito não encontrado")

    mean_v = float(analyte.internal_mean or analyte.package_insert_mean or 0)
    sd = float(analyte.internal_sd or analyte.package_insert_sd or 0)
    z = ((float(payload.value) - mean_v) / sd) if sd > 0 else None

    run = QcRun(
        tenant_id=user.tenant_id,
        qc_analyte_id=payload.qc_analyte_id,
        value=payload.value,
        z_score=Decimal(str(round(z, 4))) if z is not None else None,
        equipment_batch=payload.equipment_batch,
        operator_id=user.id,
        notes=payload.notes,
    )
    db.add(run); await db.flush()

    # Avalia regras Westgard usando os últimos N (incluindo essa)
    prev = await _load_runs(db, payload.qc_analyte_id, limit=20)
    series = [float(r.value) for r in prev] + [float(payload.value)]
    active_rules = list(analyte.active_rules.get("rules", [r[0] for r in ALL_RULES])) if analyte.active_rules else None
    if mean_v and sd:
        violations = evaluate(series, mean_v, sd, active_rules)
        for v in violations:
            db.add(QcViolation(
                tenant_id=user.tenant_id,
                qc_run_id=run.id,
                rule_code=v.rule_code,
                severity=v.severity,
            ))
    await db.flush()
    await db.refresh(run)
    return run


@router.get("/dosagens/{analyte_id}", response_model=list[QcRunOut])
async def list_runs(analyte_id: int, user: CurrentUser, db: DbSession,
                    limit: int = Query(200, ge=1, le=1000)):
    analyte = await db.get(QcAnalyte, analyte_id)
    if not analyte or analyte.tenant_id != user.tenant_id:
        raise HTTPException(404, "QC-analito não encontrado")
    stmt = (select(QcRun)
            .where(QcRun.qc_analyte_id == analyte_id)
            .order_by(QcRun.run_at.desc()).limit(limit))
    return list((await db.execute(stmt)).scalars().all())


@router.get("/violacoes", response_model=list[QcViolationOut])
async def list_violations(user: CurrentUser, db: DbSession,
                          only_open: bool = True):
    stmt = select(QcViolation).where(QcViolation.tenant_id == user.tenant_id)
    if only_open:
        stmt = stmt.where(QcViolation.resolved_at.is_(None))
    stmt = stmt.order_by(QcViolation.id.desc()).limit(500)
    return list((await db.execute(stmt)).scalars().all())


@router.post("/acoes-corretivas", response_model=CorrectiveActionOut, status_code=201)
async def create_corrective_action(payload: CorrectiveActionCreate, user: CurrentUser, db: DbSession):
    ca = CorrectiveAction(**payload.model_dump(), tenant_id=user.tenant_id, executed_by_id=user.id)
    db.add(ca); await db.flush(); await db.refresh(ca)
    return ca


@router.patch("/violacoes/{violation_id}/resolver", response_model=QcViolationOut)
async def resolve_violation(violation_id: int, corrective_action_id: int,
                            user: CurrentUser, db: DbSession):
    v = await db.get(QcViolation, violation_id)
    if not v or v.tenant_id != user.tenant_id:
        raise HTTPException(404, "Violação não encontrada")
    v.corrective_action_id = corrective_action_id
    v.resolved_at = datetime.now(timezone.utc)
    v.resolved_by_id = user.id
    await db.flush(); await db.refresh(v)
    return v


# ==================== DIÁRIO DE EQUIPAMENTO ====================
@router.post("/manutencao", response_model=MaintenanceOut, status_code=201)
async def add_maintenance(payload: MaintenanceCreate, user: CurrentUser, db: DbSession):
    m = EquipmentMaintenance(**payload.model_dump(), tenant_id=user.tenant_id, performed_by_id=user.id)
    db.add(m); await db.flush(); await db.refresh(m)
    return m


@router.get("/manutencao", response_model=list[MaintenanceOut])
async def list_maintenance(user: CurrentUser, db: DbSession, equipment_id: int | None = None):
    stmt = select(EquipmentMaintenance).where(EquipmentMaintenance.tenant_id == user.tenant_id)
    if equipment_id:
        stmt = stmt.where(EquipmentMaintenance.equipment_id == equipment_id)
    stmt = stmt.order_by(EquipmentMaintenance.performed_at.desc()).limit(200)
    return list((await db.execute(stmt)).scalars().all())


# ==================== ANÁLISES ====================
@router.get("/levey-jennings/{analyte_id}", response_model=LeveyJenningsResponse)
async def levey_jennings(analyte_id: int, user: CurrentUser, db: DbSession,
                          limit: int = Query(60, ge=5, le=500)):
    analyte = await db.get(QcAnalyte, analyte_id)
    if not analyte or analyte.tenant_id != user.tenant_id:
        raise HTTPException(404, "QC-analito não encontrado")

    exam = await db.get(Exam, analyte.exam_id)
    lot = await db.get(QcLot, analyte.qc_lot_id)

    runs = await _load_runs(db, analyte_id, limit=limit)
    # violações por run
    v_stmt = select(QcViolation).where(
        QcViolation.tenant_id == user.tenant_id,
        QcViolation.qc_run_id.in_([r.id for r in runs] or [-1]),
    )
    viols = list((await db.execute(v_stmt)).scalars().all())
    v_by_run: dict[int, list[str]] = {}
    for v in viols:
        v_by_run.setdefault(v.qc_run_id, []).append(v.rule_code)

    mean_v = analyte.internal_mean or analyte.package_insert_mean
    sd = analyte.internal_sd or analyte.package_insert_sd
    lines = {"upper_1s": None, "lower_1s": None, "upper_2s": None, "lower_2s": None, "upper_3s": None, "lower_3s": None}
    if mean_v is not None and sd is not None:
        m = float(mean_v); s = float(sd)
        lines = {
            "upper_1s": Decimal(str(round(m + s, 4))),
            "lower_1s": Decimal(str(round(m - s, 4))),
            "upper_2s": Decimal(str(round(m + 2*s, 4))),
            "lower_2s": Decimal(str(round(m - 2*s, 4))),
            "upper_3s": Decimal(str(round(m + 3*s, 4))),
            "lower_3s": Decimal(str(round(m - 3*s, 4))),
        }
    return LeveyJenningsResponse(
        analyte_id=analyte.id,
        exam_code=exam.code if exam else "",
        lot_number=lot.lot_number if lot else "",
        level=lot.level if lot else "",
        mean=mean_v, sd=sd, **lines,
        points=[LeveyJenningsPoint(
            run_id=r.id, at=r.run_at, value=r.value, z_score=r.z_score,
            violations=v_by_run.get(r.id, []),
        ) for r in runs],
        stats=stats_summary([float(r.value) for r in runs]),
    )


@router.get("/cv/{analyte_id}")
async def cv_analysis(analyte_id: int, user: CurrentUser, db: DbSession,
                      last_n: int = 30):
    analyte = await db.get(QcAnalyte, analyte_id)
    if not analyte or analyte.tenant_id != user.tenant_id:
        raise HTTPException(404, "QC-analito não encontrado")
    runs = await _load_runs(db, analyte_id, limit=last_n)
    values = [float(r.value) for r in runs]
    return stats_summary(values)


@router.get("/media-movel/{analyte_id}")
async def moving_average_ep(analyte_id: int, user: CurrentUser, db: DbSession,
                             window: int = 5, last_n: int = 60):
    analyte = await db.get(QcAnalyte, analyte_id)
    if not analyte or analyte.tenant_id != user.tenant_id:
        raise HTTPException(404, "QC-analito não encontrado")
    runs = await _load_runs(db, analyte_id, limit=last_n)
    values = [float(r.value) for r in runs]
    ma = moving_average(values, window=window)
    return {
        "window": window,
        "series": [
            {"at": r.run_at, "value": v, "ma": m}
            for r, v, m in zip(runs, values, ma)
        ]
    }


@router.get("/sigma-westgard", response_model=list[SigmaMetric])
async def sigma_westgard(user: CurrentUser, db: DbSession):
    """Sigma metrics para todos os QC-analitos ativos do tenant."""
    stmt = select(QcAnalyte).where(
        QcAnalyte.tenant_id == user.tenant_id,
        QcAnalyte.is_active.is_(True),
    )
    analytes = list((await db.execute(stmt)).scalars().all())
    out: list[SigmaMetric] = []
    for a in analytes:
        exam = await db.get(Exam, a.exam_id)
        lot = await db.get(QcLot, a.qc_lot_id)
        mean_v = a.internal_mean or a.package_insert_mean
        sd = a.internal_sd or a.package_insert_sd
        cv = a.internal_cv
        tea = a.tea_percent
        bias = Decimal("0")
        if a.internal_mean and a.package_insert_mean:
            bias = ((a.internal_mean - a.package_insert_mean) / a.package_insert_mean * 100).quantize(Decimal("0.0001"))

        sigma = None; cls = "na"
        if cv and tea and cv > 0:
            sigma_val = sigma_metric(float(cv), float(bias), float(tea))
            sigma = Decimal(str(round(sigma_val, 2)))
            cls = ("world-class" if sigma_val >= 6 else "aceitavel" if sigma_val >= 4 else "ruim")
        out.append(SigmaMetric(
            analyte_id=a.id,
            exam_code=exam.code if exam else "",
            exam_name=exam.name if exam else "",
            lot_number=lot.lot_number if lot else "",
            level=lot.level if lot else "",
            mean=mean_v, sd=sd, cv_percent=cv, bias_percent=bias, tea_percent=tea,
            sigma=sigma, classification=cls,
        ))
    return out


@router.get("/erro-total/{analyte_id}")
async def total_error_ep(analyte_id: int, user: CurrentUser, db: DbSession):
    analyte = await db.get(QcAnalyte, analyte_id)
    if not analyte or analyte.tenant_id != user.tenant_id:
        raise HTTPException(404, "QC-analito não encontrado")
    cv = float(analyte.internal_cv or 0)
    mean_v = float(analyte.internal_mean or 0)
    pi_mean = float(analyte.package_insert_mean or mean_v)
    bias = ((mean_v - pi_mean) / pi_mean * 100) if pi_mean else 0.0
    te = total_error(bias, cv)
    return {"cv_percent": cv, "bias_percent": bias, "total_error_percent": te,
            "tea_percent": float(analyte.tea_percent) if analyte.tea_percent else None}


# ==================== PAINEL ====================
@router.get("/painel")
async def qc_dashboard(user: CurrentUser, db: DbSession):
    """Resumo executivo do QC — TFMPAINEL do TMQuality."""
    analytes = list((await db.execute(
        select(QcAnalyte).where(QcAnalyte.tenant_id == user.tenant_id, QcAnalyte.is_active.is_(True))
    )).scalars().all())
    lots = list((await db.execute(
        select(QcLot).where(QcLot.tenant_id == user.tenant_id, QcLot.is_active.is_(True))
    )).scalars().all())
    open_violations = list((await db.execute(
        select(QcViolation).where(
            QcViolation.tenant_id == user.tenant_id,
            QcViolation.resolved_at.is_(None),
        )
    )).scalars().all())
    open_rej = sum(1 for v in open_violations if v.severity == "rejection")
    open_warn = sum(1 for v in open_violations if v.severity == "warning")
    return {
        "active_analytes": len(analytes),
        "active_lots": len(lots),
        "open_rejections": open_rej,
        "open_warnings": open_warn,
    }
