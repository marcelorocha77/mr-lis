"""MRLABLaudo — emissão e liberação de laudos."""
from datetime import datetime
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.deps import CurrentUser, DbSession
from app.models.request import Request

router = APIRouter(prefix="/mrlablaudo", tags=["mrlablaudo"])


class LaudoSummary(BaseModel):
    request_id: int
    number: str
    patient_id: int
    status: str
    received_datetime: datetime
    ready_count: int
    total_count: int
    model_config = ConfigDict(from_attributes=True)


@router.get("/pendentes", response_model=list[LaudoSummary])
async def laudos_pendentes(user: CurrentUser, db: DbSession):
    """Requisições prontas para liberação."""
    stmt = (
        select(Request)
        .where(
            Request.tenant_id == user.tenant_id,
            Request.status.in_(["em_processo", "liberada"]),
        )
        .options(selectinload(Request.items))
        .order_by(Request.received_datetime.desc())
        .limit(200)
    )
    result = await db.execute(stmt)
    reqs = list(result.scalars().all())
    return [
        LaudoSummary(
            request_id=r.id,
            number=r.number,
            patient_id=r.patient_id,
            status=r.status,
            received_datetime=r.received_datetime,
            ready_count=sum(1 for i in r.items if i.status == "resultado_pronto"),
            total_count=len(r.items),
        )
        for r in reqs
    ]


@router.post("/liberar/{request_id}", status_code=204)
async def liberar_laudo(request_id: int, user: CurrentUser, db: DbSession):
    req = await db.get(Request, request_id)
    if not req or req.tenant_id != user.tenant_id:
        raise HTTPException(404, "Request not found")
    req.status = "liberada"
    await db.flush()
