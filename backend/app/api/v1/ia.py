"""Inteligencia comercial supervisada (Fase 3 — docs/09).

- Clasificación automática de leads.
- Asignación sugerida de ejecutivos.
- Sugerencias de siguiente acción.
- Resumen de conversaciones.
- Prospección asistida.
- Alertas inteligentes.

Todos los módulos proponen y el usuario decide: la IA no ejecuta cambios
críticos sin validación humana.
"""
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.common import EstadoLead, PrioridadLead
from app.models.crm import Empresa, Lead
from app.models.user import Usuario
from app.services import agentes as agentes_config
from app.services import ia_comercial

router = APIRouter(tags=["ia-comercial"])


def _lead_or_404(lead_id: uuid.UUID, db: Session) -> Lead:
    lead = db.get(Lead, lead_id)
    if lead is None or lead.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Lead no encontrado")
    return lead


def _check_lead_permiso(lead: Lead, user: Usuario) -> None:
    if user.is_admin:
        return
    if lead.ejecutivo_id != user.id:
        raise HTTPException(status_code=403, detail="Sin permiso sobre este lead")


@router.post("/leads/{lead_id}/clasificar")
def clasificar(
    lead_id: uuid.UUID,
    aplicar: bool = Query(default=False),
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
) -> dict:
    """Analiza el lead y propone estado/prioridad.

    El modo de autonomía del Agente 2 (configurable en el panel) decide:
    - automatico: se aplica siempre (sin pedir confirmación).
    - asistido: se aplica solo con `aplicar=true` (confirmación humana).
    - manual: nunca se aplica automáticamente; requiere cambio manual."""
    lead = _lead_or_404(lead_id, db)
    _check_lead_permiso(lead, user)

    modo = agentes_config.modo_autonomia(db, "prospeccion")
    resultado = ia_comercial.clasificar_lead(db, lead)
    resultado["modo_autonomia"] = modo
    resultado["aplicado"] = False

    if modo == "manual":
        resultado["nota"] = "Agente en modo manual: la sugerencia no se aplica automáticamente."
        return resultado

    if aplicar or modo == "automatico":
        lead.estado = EstadoLead(resultado["estado_sugerido"])
        lead.prioridad = PrioridadLead(resultado["prioridad_sugerida"])
        db.commit()
        resultado["aplicado"] = True
    return resultado


@router.get("/leads/{lead_id}/asignacion-sugerida")
def asignacion_sugerida(
    lead_id: uuid.UUID,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
) -> dict:
    """Sugiere el ejecutivo más adecuado para la empresa del lead."""
    lead = _lead_or_404(lead_id, db)
    empresa = db.get(Empresa, lead.empresa_id)
    sugerencia = ia_comercial.sugerir_ejecutivo(db, empresa)
    if sugerencia is None:
        raise HTTPException(status_code=404, detail="No hay ejecutivos disponibles")
    return sugerencia


@router.post("/leads/{lead_id}/asignar-sugerido")
def asignar_sugerido(
    lead_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
) -> dict:
    """Aplica la asignación sugerida (solo administrador, docs/07).
    En modo manual del Agente 2, la asignación no se aplica por este medio."""
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Solo el administrador reasigna empresas")
    if agentes_config.modo_autonomia(db, "prospeccion") == "manual":
        raise HTTPException(
            status_code=409,
            detail="El Agente de Prospección está en modo manual: reasigna la empresa directamente.",
        )
    lead = _lead_or_404(lead_id, db)
    empresa = db.get(Empresa, lead.empresa_id)
    sugerencia = ia_comercial.sugerir_ejecutivo(db, empresa)
    if sugerencia is None:
        raise HTTPException(status_code=404, detail="No hay ejecutivos disponibles")

    ejecutivo_id = uuid.UUID(sugerencia["ejecutivo_id"])
    empresa.ejecutivo_id = ejecutivo_id
    lead.ejecutivo_id = ejecutivo_id
    db.commit()
    return {"ok": True, "asignado_a": sugerencia["nombre"]}


@router.get("/leads/{lead_id}/sugerencias")
def sugerencias(
    lead_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
) -> list[dict]:
    """Sugerencias de siguiente acción para el lead."""
    lead = _lead_or_404(lead_id, db)
    _check_lead_permiso(lead, user)
    return ia_comercial.sugerir_siguiente_accion(db, lead)


@router.post("/empresas/{empresa_id}/resumen")
def resumen(
    empresa_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
) -> dict:
    """Resumen del seguimiento comercial de una empresa."""
    empresa = db.get(Empresa, empresa_id)
    if empresa is None or empresa.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
    if not user.is_admin and empresa.ejecutivo_id != user.id and empresa.creado_por != user.id:
        raise HTTPException(status_code=403, detail="Sin permiso sobre esta empresa")
    return ia_comercial.resumen_conversaciones(db, empresa)


@router.get("/ia/estado")
def estado_ia(
    _: Usuario = Depends(get_current_user),
) -> list[dict]:
    """Estado del router de IA: qué proveedor responderá y cuáles están
    agotados por cuota diaria (para diagnóstico durante las pruebas)."""
    from app.services import ia_router

    return ia_router.estado()


@router.get("/ia/estrategia")
def estrategia(
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
) -> dict:
    """Agente de estrategia (docs/09): análisis de metas, inventario, rubros,
    avance y desempeño + plan semanal sugerido (requiere aprobación)."""
    return ia_comercial.analisis_estrategico(db, user)


@router.get("/prospeccion")
def prospeccion(
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
) -> dict:
    """Prospección asistida: dónde enfocar el esfuerzo comercial."""
    return ia_comercial.prospeccion_asistida(db, user)


@router.get("/alertas")
def alertas(
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
) -> list[dict]:
    """Alertas inteligentes según el rol del usuario."""
    return ia_comercial.alertas_inteligentes(db, user)
