"""MRGuardian — monitoramento em tempo real (equipamentos, prazos, alarmes)."""
from fastapi import APIRouter
from pydantic import BaseModel

from app.core.deps import CurrentUser

router = APIRouter(prefix="/mrguardian", tags=["mrguardian"])


class EquipmentStatus(BaseModel):
    name: str
    status: str  # online / offline / warning
    last_seen: str | None = None
    pending_results: int = 0


class Alarm(BaseModel):
    level: str  # info / warning / critical
    message: str
    at: str


@router.get("/equipamentos", response_model=list[EquipmentStatus])
async def equipamentos(user: CurrentUser):
    """Stub — status dos equipamentos conectados via HL7/ASTM."""
    return [
        EquipmentStatus(name="Cobas 6000", status="online", pending_results=3),
        EquipmentStatus(name="Sysmex XN-1000", status="online", pending_results=0),
        EquipmentStatus(name="Architect i2000", status="warning", pending_results=12),
    ]


@router.get("/alarmes", response_model=list[Alarm])
async def alarmes(user: CurrentUser):
    return []
