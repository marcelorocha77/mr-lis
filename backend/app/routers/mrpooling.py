"""MRPooling — worklist / mapa de trabalho por posto/setor."""
from fastapi import APIRouter, Query
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.deps import CurrentUser, DbSession
from app.models.exam import Exam
from app.models.request import Request, RequestItem

router = APIRouter(prefix="/mrpooling", tags=["mrpooling"])


class WorklistItem(BaseModel):
    request_item_id: int
    request_number: str
    patient_id: int
    exam_code: str
    exam_name: str
    section: str | None
    status: str
    model_config = ConfigDict(from_attributes=True)


@router.get("/worklist", response_model=list[WorklistItem])
async def worklist(
    user: CurrentUser,
    db: DbSession,
    section: str | None = Query(None, description="Filtra pelo setor"),
):
    """Lista de trabalho por setor (bioquimica, hematologia, imunologia...)."""
    stmt = (
        select(RequestItem, Request, Exam)
        .join(Request, RequestItem.request_id == Request.id)
        .join(Exam, RequestItem.exam_id == Exam.id)
        .where(
            RequestItem.tenant_id == user.tenant_id,
            RequestItem.status.in_(["pendente", "coletado", "em_analise"]),
        )
    )
    if section:
        stmt = stmt.where(Exam.section == section)
    stmt = stmt.order_by(Request.received_datetime).limit(500)

    rows = (await db.execute(stmt)).all()
    return [
        WorklistItem(
            request_item_id=ri.id,
            request_number=req.number,
            patient_id=req.patient_id,
            exam_code=ex.code,
            exam_name=ex.name,
            section=ex.section,
            status=ri.status,
        )
        for ri, req, ex in rows
    ]
