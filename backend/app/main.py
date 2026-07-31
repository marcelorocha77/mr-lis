from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers import (
    auth,
    mrlab,
    mrlablaudo,
    mrquality,
    mrguardian,
    mrpooling,
    mrinterface,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title="MR LIS — API",
    description="Sistema de gestão de laboratório clínico (multi-tenant)",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["meta"])
async def health():
    return {"status": "ok", "env": settings.environment}


app.include_router(auth.router)
app.include_router(mrlab.router)
app.include_router(mrlablaudo.router)
app.include_router(mrquality.router)
app.include_router(mrguardian.router)
app.include_router(mrpooling.router)
app.include_router(mrinterface.router)
