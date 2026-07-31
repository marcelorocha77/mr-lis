from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr


class DoctorBase(BaseModel):
    full_name: str
    crm: str
    crm_uf: str
    specialty: str | None = None
    phone: str | None = None
    email: EmailStr | None = None


class DoctorCreate(DoctorBase):
    pass


class DoctorUpdate(DoctorBase):
    full_name: str | None = None
    crm: str | None = None
    crm_uf: str | None = None


class DoctorOut(DoctorBase):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
