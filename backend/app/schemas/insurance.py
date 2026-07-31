from datetime import datetime
from pydantic import BaseModel, ConfigDict


class InsuranceBase(BaseModel):
    code: str
    name: str
    ans_code: str | None = None
    price_table: str | None = None
    is_active: bool = True


class InsuranceCreate(InsuranceBase):
    pass


class InsuranceUpdate(InsuranceBase):
    code: str | None = None
    name: str | None = None


class InsuranceOut(InsuranceBase):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
