"""Webhooks para orquestación con n8n (Fase 2).

- POST /webhooks/estado-comunicacion: n8n confirma el resultado del envío
  (entregado / leído / error) y actualiza la comunicación.
- Autenticación por secreto compartido en el header X-Webhook-Secret.
"""
import uuid

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models.common import EstadoComunicacion
from app.models.comunicaciones import Comunicacion

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


class EstadoComunicacionIn(BaseModel):
    comunicacion_id: uuid.UUID
    estado: EstadoComunicacion
    detalle: str | None = None


def verificar_secreto(x_webhook_secret: str | None = Header(default=None)) -> None:
    if not settings.webhook_secret:
        raise HTTPException(status_code=503, detail="Webhook no configurado (WEBHOOK_SECRET vacío)")
    if x_webhook_secret != settings.webhook_secret:
        raise HTTPException(status_code=401, detail="Secreto de webhook inválido")


@router.post("/estado-comunicacion", dependencies=[Depends(verificar_secreto)])
def estado_comunicacion(
    payload: EstadoComunicacionIn,
    db: Session = Depends(get_db),
) -> dict:
    """Actualiza el estado de una comunicación según lo reportado por n8n
    (Gmail API / WhatsApp Cloud API)."""
    comunicacion = db.get(Comunicacion, payload.comunicacion_id)
    if comunicacion is None:
        raise HTTPException(status_code=404, detail="Comunicación no encontrada")

    comunicacion.estado = payload.estado
    if payload.detalle:
        comunicacion.agente = f"{comunicacion.agente or ''} · {payload.detalle}"[:255]
    db.commit()
    return {"ok": True, "estado": comunicacion.estado.value}
