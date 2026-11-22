"""Notificaciones del panel y utilidades para automatizaciones (n8n).

- GET /notificaciones: bandeja del usuario actual.
- POST /notificaciones/{id}/leer: marcar como leída.
- GET /reservas/por-expirar: bloqueos que expiran pronto (para recordatorios).
"""
import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, ConfigDict
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_admin
from app.db.session import get_db
from app.models.common import EstadoNotificacion, EstadoReserva
from app.models.comunicaciones import Notificacion
from app.models.reserva import Reserva
from app.models.user import Usuario

router = APIRouter(tags=["notificaciones"])


class NotificacionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tipo: str
    titulo: str
    mensaje: str | None = None
    estado: str
    referencia_id: uuid.UUID | None = None
    created_at: datetime


class NotificacionList(BaseModel):
    total: int
    no_leidas: int
    items: list[NotificacionOut]


class ReservaPorExpirar(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    empresa_id: uuid.UUID
    stand_id: uuid.UUID
    ejecutivo_id: uuid.UUID | None = None
    fecha_expiracion: datetime | None = None


@router.get("/notificaciones", response_model=NotificacionList)
def list_notificaciones(
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
    solo_no_leidas: bool = Query(default=False),
    limit: int = Query(default=50, ge=1, le=200),
) -> NotificacionList:
    base = select(Notificacion).where(Notificacion.usuario_id == user.id)
    if solo_no_leidas:
        base = base.where(Notificacion.estado != EstadoNotificacion.leido)

    total = db.scalar(select(func.count()).select_from(base.subquery())) or 0
    no_leidas = db.scalar(
        select(func.count()).select_from(Notificacion).where(
            Notificacion.usuario_id == user.id,
            Notificacion.estado != EstadoNotificacion.leido,
        )
    ) or 0
    items = db.scalars(base.order_by(Notificacion.created_at.desc()).limit(limit)).all()
    return NotificacionList(
        total=total,
        no_leidas=no_leidas,
        items=[NotificacionOut.model_validate(n) for n in items],
    )


@router.post("/notificaciones/{notificacion_id}/leer")
def marcar_leida(
    notificacion_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
) -> dict:
    notificacion = db.get(Notificacion, notificacion_id)
    if notificacion is None or notificacion.usuario_id != user.id:
        return {"ok": False}
    notificacion.estado = EstadoNotificacion.leido
    db.commit()
    return {"ok": True}


@router.get("/reservas/por-expirar", response_model=list[ReservaPorExpirar])
def reservas_por_expirar(
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
    en_minutos: int = Query(default=15, ge=1, le=120),
) -> list[Reserva]:
    """Bloqueos temporales que expiran dentro de N minutos (recordatorios n8n)."""
    ahora = datetime.now(timezone.utc)
    return list(
        db.scalars(
            select(Reserva).where(
                Reserva.estado == EstadoReserva.bloqueado,
                Reserva.fecha_expiracion <= ahora + timedelta(minutes=en_minutos),
                Reserva.fecha_expiracion > ahora,
            ).order_by(Reserva.fecha_expiracion)
        )
    )
