"""Punto de entrada de la API EMC Producciones."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.db.seed import seed_initial_admin
from app.services.agentes import seed_config_agentes


@asynccontextmanager
async def lifespan(app: FastAPI):
    seed_initial_admin()
    seed_config_agentes()
    yield


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
)

# El frontend Astro consume la API en desarrollo local y desde el dominio
# configurado. Los orígenes permitidos se configuran con CORS_ORIGINS (comma).
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",") if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.get("/health", tags=["health"])
def health() -> dict:
    return {"status": "ok"}
