"""MRInterface — integração com equipamentos (HL7/ASTM/File) e sistemas externos (TISS)."""
from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import select

from app.core.deps import CurrentUser, DbSession
from app.models.equipment import Equipment, InterfaceMessage
from app.modules.mrinterface.drivers import DRIVER_REGISTRY, list_drivers
from app.schemas.equipment import (
    DriverInfo, EquipmentCreate, EquipmentOut, EquipmentUpdate, InterfaceMessageOut,
)

router = APIRouter(prefix="/mrinterface", tags=["mrinterface"])


# ---------- Drivers disponíveis ----------
@router.get("/drivers", response_model=list[DriverInfo])
async def drivers_list(user: CurrentUser):
    return list_drivers()


# ---------- Equipamentos ----------
@router.get("/equipamentos", response_model=list[EquipmentOut])
async def list_equipments(user: CurrentUser, db: DbSession):
    stmt = select(Equipment).where(Equipment.tenant_id == user.tenant_id).order_by(Equipment.name)
    result = await db.execute(stmt)
    return list(result.scalars().all())


@router.post("/equipamentos", response_model=EquipmentOut, status_code=201)
async def create_equipment(payload: EquipmentCreate, user: CurrentUser, db: DbSession):
    if payload.driver not in DRIVER_REGISTRY:
        raise HTTPException(400, f"Driver desconhecido: {payload.driver}")
    eq = Equipment(**payload.model_dump(), tenant_id=user.tenant_id)
    db.add(eq)
    await db.flush()
    await db.refresh(eq)
    return eq


@router.patch("/equipamentos/{eq_id}", response_model=EquipmentOut)
async def update_equipment(eq_id: int, payload: EquipmentUpdate, user: CurrentUser, db: DbSession):
    eq = await db.get(Equipment, eq_id)
    if not eq or eq.tenant_id != user.tenant_id:
        raise HTTPException(404, "Equipamento não encontrado")
    if payload.driver and payload.driver not in DRIVER_REGISTRY:
        raise HTTPException(400, f"Driver desconhecido: {payload.driver}")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(eq, k, v)
    await db.flush()
    await db.refresh(eq)
    return eq


@router.delete("/equipamentos/{eq_id}", status_code=204)
async def delete_equipment(eq_id: int, user: CurrentUser, db: DbSession):
    eq = await db.get(Equipment, eq_id)
    if not eq or eq.tenant_id != user.tenant_id:
        raise HTTPException(404, "Equipamento não encontrado")
    await db.delete(eq)


# ---------- Endpoints legados (compatibilidade) ----------
@router.get("/endpoints", response_model=list[EquipmentOut])
async def endpoints(user: CurrentUser, db: DbSession):
    """Alias de /equipamentos para o dashboard antigo."""
    return await list_equipments(user, db)


# ---------- Log de mensagens ----------
@router.get("/mensagens", response_model=list[InterfaceMessageOut])
async def messages_list(
    user: CurrentUser,
    db: DbSession,
    equipment_id: int | None = None,
    direction: str | None = None,
    status: str | None = None,
    limit: int = Query(100, ge=1, le=500),
):
    stmt = select(InterfaceMessage).where(InterfaceMessage.tenant_id == user.tenant_id)
    if equipment_id is not None:
        stmt = stmt.where(InterfaceMessage.equipment_id == equipment_id)
    if direction:
        stmt = stmt.where(InterfaceMessage.direction == direction)
    if status:
        stmt = stmt.where(InterfaceMessage.status == status)
    stmt = stmt.order_by(InterfaceMessage.at.desc()).limit(limit)
    result = await db.execute(stmt)
    items = list(result.scalars().all())
    # não devolver o raw completo na listagem
    return [
        InterfaceMessageOut(
            id=m.id, at=m.at, equipment_id=m.equipment_id, direction=m.direction,
            protocol=m.protocol, message_type=m.message_type, status=m.status,
            request_number=m.request_number, error=m.error,
        )
        for m in items
    ]


@router.get("/mensagens/{msg_id}", response_model=InterfaceMessageOut)
async def message_detail(msg_id: int, user: CurrentUser, db: DbSession):
    m = await db.get(InterfaceMessage, msg_id)
    if not m or m.tenant_id != user.tenant_id:
        raise HTTPException(404, "Mensagem não encontrada")
    return m


# ---------- Status do robô ----------
@router.get("/robot/status")
async def robot_status(user: CurrentUser, db: DbSession):
    stmt = select(Equipment).where(
        Equipment.tenant_id == user.tenant_id,
        Equipment.is_enabled.is_(True),
    )
    active = list((await db.execute(stmt)).scalars().all())
    return {
        "drivers_registered": len(DRIVER_REGISTRY),
        "equipments_active": len(active),
        "equipments": [{"code": e.code, "name": e.name, "last_seen": e.last_seen, "last_error": e.last_error} for e in active],
    }
