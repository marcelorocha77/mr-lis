from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict


class ExamBase(BaseModel):
    code: str
    name: str
    section: str | None = None
    material: str | None = None
    method: str | None = None
    unit: str | None = None
    turnaround_hours: int = 24
    price: Decimal = Decimal("0.00")
    is_active: bool = True


class ExamCreate(ExamBase):
    pass


class ExamUpdate(ExamBase):
    code: str | None = None
    name: str | None = None


class ExamOut(ExamBase):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
