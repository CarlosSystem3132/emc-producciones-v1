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

from app.api.deps import get_current_user, require_admin, require_admin_o_webhook
from app.db.session import get_db
from app.models.common import EstadoNotificacion, EstadoReserva
from app.models.comunicaciones import Notificacion
from app.models.crm import Contacto, Lead
from app.models.inventario import Stand
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
    empresa: str | None = None
    stand: str | None = None
    contacto: str | None = None
    whatsapp: str | None = None
    email: str | None = None
    canal_preferido: str | None = None
    fecha_expiracion: datetime | None = None
    minutos_restantes: int | None = None
    mensaje: str | None = None


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
    _: Usuario | None = Depends(require_admin_o_webhook),
    en_minutos: int = Query(default=15, ge=1, le=120),
) -> list[ReservaPorExpirar]:
    """Bloqueos temporales que expiran dentro de N minutos (recordatorios n8n).

    Devuelve para cada reserva el contacto a recordar (WhatsApp/email) y un
    mensaje preformateado, para que n8n solo tenga que enviarlo (docs/14).
    """
    ahora = datetime.now(timezone.utc)
    reservas = list(
        db.scalars(
            select(Reserva).where(
                Reserva.estado == EstadoReserva.bloqueado,
                Reserva.fecha_expiracion <= ahora + timedelta(minutes=en_minutos),
                Reserva.fecha_expiracion > ahora,
            ).order_by(Reserva.fecha_expiracion)
        )
    )

    salida: list[ReservaPorExpirar] = []
    for r in reservas:
        empresa = db.get(Empresa, r.empresa_id)
        stand = db.get(Stand, r.stand_id)
        contacto: Contacto | None = None
        if r.lead_id:
            lead = db.get(Lead, r.lead_id)
            if lead is not None and lead.contacto_id:
                contacto = db.get(Contacto, lead.contacto_id)
        if contacto is None and empresa is not None and empresa.contactos:
            contacto = empresa.contactos[0]

        minutos = (
            max(0, int((r.fecha_expiracion - ahora).total_seconds() // 60))
            if r.fecha_expiracion
            else None
        )
        whatsapp = contacto.whatsapp if contacto else None
        email = contacto.email if contacto else None
        canal_preferido = "whatsapp" if whatsapp else ("email" if email else None)
        if canal_preferido is None:
            continue  # sin canal de contacto: no hay a quién recordar
        empresa_nombre = empresa.razon_social if empresa else "tu empresa"
        stand_codigo = stand.codigo if stand else ""
        mensaje = (
            f"⏰ Recordatorio EXPOINCO 2027: el bloqueo temporal del stand "
            f"{stand_codigo} de {empresa_nombre} vence en ~{minutos} min. "
            f"Confirma la reserva con tu ejecutivo antes de que expire. "
            f"— EMC Producciones"
        )
        salida.append(
            ReservaPorExpirar(
                id=r.id,
                empresa=empresa_nombre,
                stand=stand_codigo,
                contacto=contacto.nombre if contacto else None,
                whatsapp=whatsapp,
                email=email,
                canal_preferido=canal_preferido,
                fecha_expiracion=r.fecha_expiracion,
                minutos_restantes=minutos,
                mensaje=mensaje,
            )
        )
    return salida
