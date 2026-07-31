from pydantic import BaseModel, EmailStr


class LoginIn(BaseModel):
    email: EmailStr
    password: str
    tenant_slug: str


class TokenOut(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshIn(BaseModel):
    refresh_token: str


class MeOut(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    role: str
    tenant_id: int
    tenant_name: str
