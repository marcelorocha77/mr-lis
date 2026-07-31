from datetime import date, datetime
from pydantic import BaseModel, ConfigDict, EmailStr


class PatientBase(BaseModel):
    cpf: str | None = None
    full_name: str
    social_name: str | None = None
    birth_date: date | None = None
    sex: str | None = None
    phone: str | None = None
    email: EmailStr | None = None
    mother_name: str | None = None
    address_street: str | None = None
    address_number: str | None = None
    address_complement: str | None = None
    address_district: str | None = None
    address_city: str | None = None
    address_state: str | None = None
    address_zip: str | None = None


class PatientCreate(PatientBase):
    pass


class PatientUpdate(PatientBase):
    full_name: str | None = None


class PatientOut(PatientBase):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
