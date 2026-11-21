"""Dashboard administrativo (docs/07 — Panel del administrador).

Métricas globales para el admin; el ejecutivo ve sus propios números.
"""
import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.common import (
    EstadoLead,
    EstadoReserva,
    EstadoStand,
    RolUsuario,
    TipoStand,
)
from app.models.crm import Empresa, Lead
from app.models.inventario import Stand
from app.models.reserva import Reserva
from app.models.user import Usuario

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("")
def dashboard(
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
) -> dict:
    admin = user.is_admin

    # ---- Stands ----
    conteo_stands = dict(
        db.execute(select(Stand.estado, func.count()).group_by(Stand.estado)).all()
    )
    total_stands = sum(conteo_stands.values())
    vendidos = conteo_stands.get(EstadoStand.vendido, 0)
    reservados = conteo_stands.get(EstadoStand.reservado, 0)
    ocupados = vendidos + reservados
    porcentaje_ocupacion = round(100 * ocupados / total_stands, 1) if total_stands else 0.0

    # Canchas de maquinaria (tipo cancha)
    canchas = dict(
        db.execute(
            select(Stand.estado, func.count())
            .where(Stand.tipo == TipoStand.cancha)
            .group_by(Stand.estado)
        ).all()
    )

    # ---- Ventas ----
    ventas_q = select(func.coalesce(func.sum(Reserva.monto), 0)).where(
        Reserva.estado == EstadoReserva.vendido
    )
    if not admin:
        ventas_q = ventas_q.where(Reserva.ejecutivo_id == user.id)
    ventas_totales = float(db.scalar(ventas_q) or 0)

    proyectado_q = select(func.coalesce(func.sum(Stand.precio_base), 0)).where(
        Stand.estado.in_([EstadoStand.reservado, EstadoStand.vendido])
    )
    ventas_proyectadas = float(db.scalar(proyectado_q) or 0)

    # ---- Empresas por estado (embudo de empresas) ----
    empresas_q = select(Empresa.estado, func.count()).where(Empresa.deleted_at.is_(None))
    if not admin:
        empresas_q = empresas_q.where(Empresa.ejecutivo_id == user.id)
    empresas_por_estado = {e.value: 0 for e in EstadoLead}
    for estado, cantidad in db.execute(empresas_q.group_by(Empresa.estado)):
        empresas_por_estado[estado.value] = cantidad

    # ---- Leads: embudo ----
    leads_q = select(Lead.estado, func.count()).where(Lead.deleted_at.is_(None))
    if not admin:
        leads_q = leads_q.where(Lead.ejecutivo_id == user.id)
    embudo = {e.value: 0 for e in EstadoLead}
    for estado, cantidad in db.execute(leads_q.group_by(Lead.estado)):
        embudo[estado.value] = cantidad

    # ---- Desempeño por ejecutivo (solo admin) ----
    desempeno = []
    if admin:
        ejecutivos = db.scalars(
            select(Usuario).where(Usuario.deleted_at.is_(None), Usuario.rol == RolUsuario.ejecutivo)
        ).all()
        for ej in ejecutivos:
            abiertos = db.scalar(
                select(func.count()).select_from(Lead).where(
                    Lead.ejecutivo_id == ej.id,
                    Lead.deleted_at.is_(None),
                    Lead.estado.notin_([EstadoLead.vendido, EstadoLead.descartado]),
                )
            ) or 0
            ventas = float(
                db.scalar(
                    select(func.coalesce(func.sum(Reserva.monto), 0)).where(
                        Reserva.ejecutivo_id == ej.id, Reserva.estado == EstadoReserva.vendido
                    )
                ) or 0
            )
            desempeno.append(
                {
                    "ejecutivo_id": str(ej.id),
                    "nombre": ej.nombre_completo,
                    "leads_abiertos": abiertos,
                    "ventas": ventas,
                }
            )
        desempeno.sort(key=lambda d: d["ventas"], reverse=True)

    # ---- Avance semanal ----
    desde = datetime.now(timezone.utc) - timedelta(days=7)
    leads_semana = db.scalar(
        select(func.count()).select_from(Lead).where(Lead.created_at >= desde)
    ) or 0
    reservas_semana = db.scalar(
        select(func.count()).select_from(Reserva).where(Reserva.created_at >= desde)
    ) or 0
    empresas_semana = db.scalar(
        select(func.count()).select_from(Empresa).where(
            Empresa.created_at >= desde, Empresa.deleted_at.is_(None)
        )
    ) or 0

    # ---- Alertas críticas ----
    alertas = []
    por_expirar = db.scalars(
        select(Reserva).where(
            Reserva.estado == EstadoReserva.bloqueado,
            Reserva.fecha_expiracion < datetime.now(timezone.utc) + timedelta(minutes=15),
            Reserva.fecha_expiracion > datetime.now(timezone.utc),
        )
    ).all()
    for r in por_expirar:
        alertas.append(
            {
                "tipo": "reserva_por_expirar",
                "mensaje": f"Reserva {str(r.id)[:8]} por expirar en minutos",
            }
        )
    vendidos_sin_contrato = db.scalar(
        select(func.count()).select_from(Reserva).where(
            Reserva.estado == EstadoReserva.vendido, Reserva.contrato_url.is_(None)
        )
    ) or 0
    if vendidos_sin_contrato:
        alertas.append(
            {
                "tipo": "venta_sin_contrato",
                "mensaje": f"{vendidos_sin_contrato} venta(s) sin contrato adjunto",
            }
        )

    return {
        "stands": {
            "total": total_stands,
            "disponibles": conteo_stands.get(EstadoStand.disponible, 0),
            "bloqueados": conteo_stands.get(EstadoStand.bloqueado_temporal, 0),
            "reservados": reservados,
            "vendidos": vendidos,
            "no_disponibles": conteo_stands.get(EstadoStand.no_disponible, 0),
            "porcentaje_ocupacion": porcentaje_ocupacion,
        },
        "canchas": {
            "disponibles": canchas.get(EstadoStand.disponible, 0),
            "vendidas": canchas.get(EstadoStand.vendido, 0),
        },
        "ventas": {
            "totales": ventas_totales,
            "proyectadas": ventas_proyectadas,
        },
        "empresas_por_estado": empresas_por_estado,
        "embudo": embudo,
        "desempeno_ejecutivos": desempeno,
        "avance_semanal": {
            "empresas": empresas_semana,
            "leads": leads_semana,
            "reservas": reservas_semana,
        },
        "alertas": alertas,
    }
