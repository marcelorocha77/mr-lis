from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.core.deps import CurrentUser, DbSession
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password,
)
from app.models.tenant import Tenant
from app.models.user import User
from app.schemas.auth import LoginIn, MeOut, RefreshIn, TokenOut

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenOut)
async def login(payload: LoginIn, db: DbSession):
    result = await db.execute(
        select(Tenant).where(Tenant.slug == payload.tenant_slug, Tenant.is_active.is_(True))
    )
    tenant = result.scalar_one_or_none()
    if not tenant:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    result = await db.execute(
        select(User).where(
            User.tenant_id == tenant.id,
            User.email == payload.email,
            User.is_active.is_(True),
        )
    )
    user = result.scalar_one_or_none()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return TokenOut(
        access_token=create_access_token(user.id, tenant.id, {"role": user.role}),
        refresh_token=create_refresh_token(user.id, tenant.id),
    )


@router.post("/refresh", response_model=TokenOut)
async def refresh(payload: RefreshIn, db: DbSession):
    try:
        data = decode_token(payload.refresh_token)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    if data.get("typ") != "refresh":
        raise HTTPException(status_code=401, detail="Wrong token type")

    user_id = int(data["sub"])
    tenant_id = int(data["tid"])
    result = await db.execute(select(User).where(User.id == user_id, User.is_active.is_(True)))
    user = result.scalar_one_or_none()
    if not user or user.tenant_id != tenant_id:
        raise HTTPException(status_code=401, detail="User not found")

    return TokenOut(
        access_token=create_access_token(user.id, tenant_id, {"role": user.role}),
        refresh_token=create_refresh_token(user.id, tenant_id),
    )


@router.get("/me", response_model=MeOut)
async def me(user: CurrentUser, db: DbSession):
    tenant = await db.get(Tenant, user.tenant_id)
    return MeOut(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        tenant_id=user.tenant_id,
        tenant_name=tenant.name if tenant else "",
    )
