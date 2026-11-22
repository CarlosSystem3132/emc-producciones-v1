"""Router principal de la API v1."""
from fastapi import APIRouter

from app.api.v1 import (
    auth,
    campanas,
    chat,
    comunicaciones,
    config_agentes,
    dashboard,
    empresas,
    facturas,
    firmas,
    ia,
    inventario,
    leads,
    notificaciones,
    pagos,
    patrocinadores,
    plantillas,
    public,
    reportes,
    reservas,
    secuencias,
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
api_router.include_router(chat.router)
api_router.include_router(secuencias.router)
api_router.include_router(ia.router)
api_router.include_router(pagos.router)
api_router.include_router(facturas.router)
api_router.include_router(firmas.router)
api_router.include_router(patrocinadores.router)
api_router.include_router(reportes.router)
api_router.include_router(config_agentes.router)
