"""Router principal de la API v1."""
from fastapi import APIRouter

from app.api.v1 import (
    auth,
    campanas,
    comunicaciones,
    dashboard,
    empresas,
    inventario,
    leads,
    notificaciones,
    plantillas,
    public,
    reservas,
    users,
    webhooks,
)

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(dashboard.router)
api_router.include_router(notificaciones.router)
api_router.include_router(webhooks.router)
api_router.include_router(plantillas.router)
api_router.include_router(comunicaciones.router)
api_router.include_router(campanas.router)
api_router.include_router(users.router)
api_router.include_router(empresas.router)
api_router.include_router(leads.router)
api_router.include_router(inventario.router)
api_router.include_router(reservas.router)
api_router.include_router(public.router)
