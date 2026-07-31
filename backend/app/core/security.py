from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
from jose import JWTError, jwt

from app.core.config import settings

ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    # bcrypt aceita no máximo 72 bytes; trunca defensivamente
    pwd = password.encode("utf-8")[:72]
    return bcrypt.hashpw(pwd, bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    pwd = plain.encode("utf-8")[:72]
    try:
        return bcrypt.checkpw(pwd, hashed.encode("utf-8"))
    except (ValueError, TypeError):
        return False


def create_access_token(subject: str | int, tenant_id: int, extra: dict | None = None) -> str:
    now = datetime.now(timezone.utc)
    payload: dict[str, Any] = {
        "sub": str(subject),
        "tid": tenant_id,
        "iat": now,
        "exp": now + timedelta(minutes=settings.access_token_expire_minutes),
        "typ": "access",
    }
    if extra:
        payload.update(extra)
    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)


def create_refresh_token(subject: str | int, tenant_id: int) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(subject),
        "tid": tenant_id,
        "iat": now,
        "exp": now + timedelta(days=settings.refresh_token_expire_days),
        "typ": "refresh",
    }
    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
    except JWTError as e:
        raise ValueError(f"invalid token: {e}") from e
