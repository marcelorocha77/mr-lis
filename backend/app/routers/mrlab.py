"""MRLAB — módulo núcleo: pacientes, médicos, convênios, exames, requisições."""
from datetime import datetime
from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import func, or_, select
from sqlalchemy.orm import selectinload

from app.core.deps import CurrentUser, DbSession
from app.models.doctor import Doctor
from app.models.exam import Exam
from app.models.insurance import Insurance
from app.models.patient import Patient
from app.models.request import Request, RequestItem
from app.schemas.common import Page
from app.schemas.doctor import DoctorCreate, DoctorOut, DoctorUpdate
from app.schemas.exam import ExamCreate, ExamOut, ExamUpdate
from app.schemas.insurance import InsuranceCreate, InsuranceOut, InsuranceUpdate
from app.schemas.patient import PatientCreate, PatientOut, PatientUpdate
from app.schemas.request import RequestCreate, RequestOut

router = APIRouter(prefix="/mrlab", tags=["mrlab"])


# ---------- Pacientes ----------
@router.get("/pacientes", response_model=Page[PatientOut])
async def list_patients(
    user: CurrentUser,
    db: DbSession,
    q: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    stmt = select(Patient).where(Patient.tenant_id == user.tenant_id)
    if q:
        like = f"%{q}%"
        stmt = stmt.where(or_(Patient.full_name.ilike(like), Patient.cpf.ilike(like)))

    total = await db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    stmt = stmt.order_by(Patient.full_name).limit(page_size).offset((page - 1) * page_size)
    result = await db.execute(stmt)
    items = list(result.scalars().all())
    return Page[PatientOut](items=items, total=total, page=page, page_size=page_size)


@router.post("/pacientes", response_model=PatientOut, status_code=201)
async def create_patient(payload: PatientCreate, user: CurrentUser, db: DbSession):
    p = Patient(**payload.model_dump(), tenant_id=user.tenant_id)
    db.add(p)
    await db.flush()
    await db.refresh(p)
    return p


@router.get("/pacientes/{patient_id}", response_model=PatientOut)
async def get_patient(patient_id: int, user: CurrentUser, db: DbSession):
    p = await db.get(Patient, patient_id)
    if not p or p.tenant_id != user.tenant_id:
        raise HTTPException(404, "Patient not found")
    return p


@router.patch("/pacientes/{patient_id}", response_model=PatientOut)
async def update_patient(
    patient_id: int, payload: PatientUpdate, user: CurrentUser, db: DbSession
):
    p = await db.get(Patient, patient_id)
    if not p or p.tenant_id != user.tenant_id:
        raise HTTPException(404, "Patient not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(p, k, v)
    await db.flush()
    await db.refresh(p)
    return p


@router.delete("/pacientes/{patient_id}", status_code=204)
async def delete_patient(patient_id: int, user: CurrentUser, db: DbSession):
    p = await db.get(Patient, patient_id)
    if not p or p.tenant_id != user.tenant_id:
        raise HTTPException(404, "Patient not found")
    await db.delete(p)


# ---------- Médicos ----------
@router.get("/medicos", response_model=Page[DoctorOut])
async def list_doctors(
    user: CurrentUser,
    db: DbSession,
    q: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    stmt = select(Doctor).where(Doctor.tenant_id == user.tenant_id)
    if q:
        like = f"%{q}%"
        stmt = stmt.where(or_(Doctor.full_name.ilike(like), Doctor.crm.ilike(like)))
    total = await db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    stmt = stmt.order_by(Doctor.full_name).limit(page_size).offset((page - 1) * page_size)
    result = await db.execute(stmt)
    return Page[DoctorOut](
        items=list(result.scalars().all()), total=total, page=page, page_size=page_size
    )


@router.post("/medicos", response_model=DoctorOut, status_code=201)
async def create_doctor(payload: DoctorCreate, user: CurrentUser, db: DbSession):
    d = Doctor(**payload.model_dump(), tenant_id=user.tenant_id)
    db.add(d)
    await db.flush()
    await db.refresh(d)
    return d


@router.patch("/medicos/{doctor_id}", response_model=DoctorOut)
async def update_doctor(doctor_id: int, payload: DoctorUpdate, user: CurrentUser, db: DbSession):
    d = await db.get(Doctor, doctor_id)
    if not d or d.tenant_id != user.tenant_id:
        raise HTTPException(404, "Doctor not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(d, k, v)
    await db.flush()
    await db.refresh(d)
    return d


# ---------- Convênios ----------
@router.get("/convenios", response_model=Page[InsuranceOut])
async def list_insurances(
    user: CurrentUser,
    db: DbSession,
    q: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    stmt = select(Insurance).where(Insurance.tenant_id == user.tenant_id)
    if q:
        like = f"%{q}%"
        stmt = stmt.where(or_(Insurance.name.ilike(like), Insurance.code.ilike(like)))
    total = await db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    stmt = stmt.order_by(Insurance.name).limit(page_size).offset((page - 1) * page_size)
    result = await db.execute(stmt)
    return Page[InsuranceOut](
        items=list(result.scalars().all()), total=total, page=page, page_size=page_size
    )


@router.post("/convenios", response_model=InsuranceOut, status_code=201)
async def create_insurance(payload: InsuranceCreate, user: CurrentUser, db: DbSession):
    ins = Insurance(**payload.model_dump(), tenant_id=user.tenant_id)
    db.add(ins)
    await db.flush()
    await db.refresh(ins)
    return ins


# ---------- Exames (catálogo) ----------
@router.get("/exames", response_model=Page[ExamOut])
async def list_exams(
    user: CurrentUser,
    db: DbSession,
    q: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    stmt = select(Exam).where(Exam.tenant_id == user.tenant_id)
    if q:
        like = f"%{q}%"
        stmt = stmt.where(or_(Exam.name.ilike(like), Exam.code.ilike(like)))
    total = await db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    stmt = stmt.order_by(Exam.name).limit(page_size).offset((page - 1) * page_size)
    result = await db.execute(stmt)
    return Page[ExamOut](
        items=list(result.scalars().all()), total=total, page=page, page_size=page_size
    )


@router.post("/exames", response_model=ExamOut, status_code=201)
async def create_exam(payload: ExamCreate, user: CurrentUser, db: DbSession):
    e = Exam(**payload.model_dump(), tenant_id=user.tenant_id)
    db.add(e)
    await db.flush()
    await db.refresh(e)
    return e


@router.patch("/exames/{exam_id}", response_model=ExamOut)
async def update_exam(exam_id: int, payload: ExamUpdate, user: CurrentUser, db: DbSession):
    e = await db.get(Exam, exam_id)
    if not e or e.tenant_id != user.tenant_id:
        raise HTTPException(404, "Exam not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(e, k, v)
    await db.flush()
    await db.refresh(e)
    return e


# ---------- Requisições ----------
def _next_request_number() -> str:
    now = datetime.now()
    return f"R{now.strftime('%Y%m%d%H%M%S')}"


@router.get("/requisicoes", response_model=Page[RequestOut])
async def list_requests(
    user: CurrentUser,
    db: DbSession,
    status_filter: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    stmt = (
        select(Request)
        .where(Request.tenant_id == user.tenant_id)
        .options(selectinload(Request.items))
    )
    if status_filter:
        stmt = stmt.where(Request.status == status_filter)
    total = await db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    stmt = stmt.order_by(Request.received_datetime.desc()).limit(page_size).offset((page - 1) * page_size)
    result = await db.execute(stmt)
    return Page[RequestOut](
        items=list(result.scalars().all()), total=total, page=page, page_size=page_size
    )


@router.post("/requisicoes", response_model=RequestOut, status_code=201)
async def create_request(payload: RequestCreate, user: CurrentUser, db: DbSession):
    # validate patient
    patient = await db.get(Patient, payload.patient_id)
    if not patient or patient.tenant_id != user.tenant_id:
        raise HTTPException(400, "Patient not found in tenant")

    req = Request(
        tenant_id=user.tenant_id,
        number=_next_request_number(),
        patient_id=payload.patient_id,
        doctor_id=payload.doctor_id,
        insurance_id=payload.insurance_id,
        collection_datetime=payload.collection_datetime,
        clinical_info=payload.clinical_info,
    )
    db.add(req)
    await db.flush()

    for item in payload.items:
        exam = await db.get(Exam, item.exam_id)
        if not exam or exam.tenant_id != user.tenant_id:
            raise HTTPException(400, f"Exam {item.exam_id} not found")
        db.add(
            RequestItem(
                tenant_id=user.tenant_id,
                request_id=req.id,
                exam_id=exam.id,
                price=item.price if item.price is not None else exam.price,
            )
        )
    await db.flush()
    await db.refresh(req, attribute_names=["items"])
    return req


@router.get("/requisicoes/{request_id}", response_model=RequestOut)
async def get_request(request_id: int, user: CurrentUser, db: DbSession):
    stmt = (
        select(Request)
        .where(Request.id == request_id, Request.tenant_id == user.tenant_id)
        .options(selectinload(Request.items))
    )
    result = await db.execute(stmt)
    req = result.scalar_one_or_none()
    if not req:
        raise HTTPException(404, "Request not found")
    return req
