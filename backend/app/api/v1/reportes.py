"""Reportes comerciales avanzados y pronóstico de ocupación (Fase 4 — docs/10).

- Ventas por ejecutivo.
- Ocupación por zona.
- Conversión del embudo comercial.
- Efectividad de comunicaciones.
- Pronóstico de ocupación basado en la velocidad actual de reservas/ventas.
"""
import csv
import io
import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_admin
from app.db.session import get_db
from app.models.common import EstadoReserva, RolUsuario
from app.models.comunicaciones import Comunicacion
from app.models.crm import Empresa, Lead
from app.models.inventario import Stand, Zona
from app.models.reserva import Reserva
from app.models.user import Usuario

router = APIRouter(prefix="/reportes", tags=["reportes"])


@router.get("/ventas-por-ejecutivo")
def ventas_por_ejecutivo(
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
) -> list[dict]:
    """Ventas confirmadas y monto total por ejecutivo."""
    filas = db.execute(
        select(
            Usuario.id,
            Usuario.nombre_completo,
            func.count(Reserva.id),
            func.coalesce(func.sum(Reserva.monto), 0),
        )
        .join(Reserva, Reserva.ejecutivo_id == Usuario.id, isouter=True)
        .where(Usuario.rol == RolUsuario.ejecutivo, Usuario.deleted_at.is_(None))
        .group_by(Usuario.id, Usuario.nombre_completo)
    ).all()
    return [
        {
            "ejecutivo_id": str(fid),
            "nombre": nombre,
            "ventas": int(cantidad),
            "monto_total": float(monto),
        }
        for fid, nombre, cantidad, monto in filas
    ]


@router.get("/ocupacion-por-zona")
def ocupacion_por_zona(db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)) -> list[dict]:
    """Ocupación (reservados + vendidos) por zona del pabellón."""
    resultado = []
    zonas = db.scalars(select(Zona).order_by(Zona.nombre)).all()
    for zona in zonas:
        estados = dict(
            db.execute(
                select(Stand.estado, func.count())
                .where(Stand.zona_id == zona.id)
                .group_by(Stand.estado)
            ).all()
        )
        total = sum(estados.values())
        ocupados = estados.get("reservado", 0) + estados.get("vendido", 0)
        resultado.append({
            "zona": zona.nombre,
            "tipo": zona.tipo.value,
            "total": total,
            "disponibles": estados.get("disponible", 0),
            "bloqueados": estados.get("bloqueado_temporal", 0),
            "reservados": estados.get("reservado", 0),
            "vendidos": estados.get("vendido", 0),
            "porcentaje_ocupacion": round(100 * ocupados / total, 1) if total else 0.0,
        })
    return resultado


@router.get("/embudo")
def embudo(db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)) -> list[dict]:
    """Conteo de leads por estado con tasa de conversión al estado siguiente."""
    conteo = dict(
        db.execute(
            select(Lead.estado, func.count())
            .where(Lead.deleted_at.is_(None))
            .group_by(Lead.estado)
        ).all()
    )
    orden = [
        "prospecto", "contactado", "interesado", "propuesta_enviada",
        "en_negociacion", "reserva_temporal", "reservado", "vendido",
    ]
    filas = []
    for i, estado in enumerate(orden):
        cantidad = conteo.get(estado, 0)
        if isinstance(cantidad, str):  # clave enum
            cantidad = conteo.get(next((k for k in conteo if getattr(k, "value", k) == estado), estado), 0)
        siguiente = conteo.get(orden[i + 1], 0) if i + 1 < len(orden) else 0
        filas.append({
            "estado": estado,
            "cantidad": int(cantidad),
            "conversion_siguiente": round(100 * siguiente / cantidad, 1) if cantidad else 0.0,
        })
    return filas


@router.get("/comunicaciones")
def comunicaciones(db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)) -> dict:
    """Efectividad de comunicaciones por canal y estado."""
    por_canal = {}
    for canal, estado, cantidad in db.execute(
        select(Comunicacion.canal, Comunicacion.estado, func.count()).group_by(
            Comunicacion.canal, Comunicacion.estado
        )
    ).all():
        clave = getattr(canal, "value", canal)
        por_canal.setdefault(clave, {})[getattr(estado, "value", estado)] = int(cantidad)
    total = db.scalar(select(func.count()).select_from(Comunicacion)) or 0
    return {"total": int(total), "por_canal": por_canal}


@router.get("/pronostico")
def pronostico_ocupacion(db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)) -> dict:
    """Proyección de ocupación con la velocidad actual de reservas y ventas.

    - Velocidad: reservas + ventas confirmadas por semana en los últimos 30 días.
    - Proyección lineal hacia el 100% de ocupación de stands interiores.
    """
    desde = datetime.now(timezone.utc) - timedelta(days=30)
    reservas_30d = db.scalar(
        select(func.count()).select_from(Reserva).where(
            Reserva.created_at >= desde,
            Reserva.estado.in_([EstadoReserva.reservado, EstadoReserva.vendido]),
        )
    ) or 0
    velocidad_semanal = reservas_30d / 30 * 7

    total_stands = db.scalar(select(func.count()).select_from(Stand)) or 0
    ocupados = db.scalar(
        select(func.count()).select_from(Stand).where(
            Stand.estado.in_(["reservado", "vendido"])
        )
    ) or 0
    restantes = max(total_stands - ocupados, 0)

    if velocidad_semanal > 0:
        semanas_restantes = restantes / velocidad_semanal
        fecha_estimada = datetime.now(timezone.utc) + timedelta(weeks=semanas_restantes)
        fecha_iso = fecha_estimada.date().isoformat()
    else:
        semanas_restantes = None
        fecha_iso = None

    # Pronóstico a la fecha del evento (abril 2027)
    evento = datetime(2027, 4, 30, tzinfo=timezone.utc)
    semanas_al_evento = max((evento - datetime.now(timezone.utc)).days / 7, 0)
    proyectado = min(ocupados + velocidad_semanal * semanas_al_evento, total_stands)

    return {
        "total_stands": total_stands,
        "ocupados": ocupados,
        "porcentaje_actual": round(100 * ocupados / total_stands, 1) if total_stands else 0.0,
        "reservas_ultimos_30_dias": reservas_30d,
        "velocidad_semanal": round(velocidad_semanal, 2),
        "semanas_para_100": round(semanas_restantes, 1) if semanas_restantes is not None else None,
        "fecha_estimada_100": fecha_iso,
        "porcentaje_proyectado_abril_2027": round(100 * proyectado / total_stands, 1) if total_stands else 0.0,
    }


@router.get("/export")
def exportar_csv(
    tipo: str = Query(pattern="^(ventas|ocupacion|embudo)$"),
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
) -> StreamingResponse:
    """Exporta un reporte en CSV (ventas | ocupacion | embudo)."""
    if tipo == "ventas":
        filas = ventas_por_ejecutivo(db, _)
        encabezados = ["ejecutivo_id", "nombre", "ventas", "monto_total"]
    elif tipo == "ocupacion":
        filas = ocupacion_por_zona(db, _)
        encabezados = ["zona", "tipo", "total", "disponibles", "reservados", "vendidos", "porcentaje_ocupacion"]
    else:
        filas = embudo(db, _)
        encabezados = ["estado", "cantidad", "conversion_siguiente"]

    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=encabezados, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(filas)
    buffer.seek(0)

    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="reporte-{tipo}.csv"'},
    )
