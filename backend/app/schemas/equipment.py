from datetime import datetime
from pydantic import BaseModel, ConfigDict


class EquipmentBase(BaseModel):
    code: str
    name: str
    driver: str
    protocol: str = "hl7_mllp"
    connection: dict = {}
    section: str | None = None
    direction: str = "bidirectional"
    is_enabled: bool = True


class EquipmentCreate(EquipmentBase):
    pass


class EquipmentUpdate(BaseModel):
    name: str | None = None
    driver: str | None = None
    protocol: str | None = None
    connection: dict | None = None
    section: str | None = None
    direction: str | None = None
    is_enabled: bool | None = None


class EquipmentOut(EquipmentBase):
    id: int
    last_seen: datetime | None = None
    last_error: str | None = None
    pending_count: int = 0
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class DriverInfo(BaseModel):
    code: str
    vendor: str
    model: str
    protocol: str
    section: str


class InterfaceMessageOut(BaseModel):
    id: int
    at: datetime
    equipment_id: int | None
    direction: str
    protocol: str
    message_type: str | None
    status: str
    request_number: str | None
    error: str | None
    raw: str | None = None
    model_config = ConfigDict(from_attributes=True)
