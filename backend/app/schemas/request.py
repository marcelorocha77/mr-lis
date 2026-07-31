from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict


class RequestItemIn(BaseModel):
    exam_id: int
    price: Decimal | None = None


class RequestItemOut(BaseModel):
    id: int
    exam_id: int
    price: Decimal
    status: str
    model_config = ConfigDict(from_attributes=True)


class RequestCreate(BaseModel):
    patient_id: int
    doctor_id: int | None = None
    insurance_id: int | None = None
    collection_datetime: datetime | None = None
    clinical_info: str | None = None
    items: list[RequestItemIn]


class RequestOut(BaseModel):
    id: int
    number: str
    patient_id: int
    doctor_id: int | None
    insurance_id: int | None
    collection_datetime: datetime | None
    received_datetime: datetime
    status: str
    clinical_info: str | None
    items: list[RequestItemOut]
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
