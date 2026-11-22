"""Campañas de comunicación (Fase 2).

Flujo (docs/07 — Campañas):
1. Crear campaña con segmento (estado de empresa o rubro) y plantilla.
2. Generar comunicaciones pendientes para el segmento (con control de duplicados).
3. Aprobar (admin) y despachar con límite diario.
"""
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_admin
from app.db.session import get_db
from app.models.common import EstadoCampana, EstadoComunicacion
from app.models.comunicaciones import Campana, Comunicacion, Plantilla
from app.models.crm import Empresa
from app.models.user import Usuario
from app.schemas.comunicacion import (
    CampanaCreate,
    CampanaList,
    CampanaOut,
    GenerarResultado,
)
from app.services.comunicaciones import (
    despachar_n8n,
    renderizar,
    validar_frecuencia,
    variables_disponibles,
)

router = APIRouter(prefix="/campanas", tags=["campañas"])


def _get_campana_or_404(campana_id: uuid.UUID, db: Session) -> Campana:
    campana = db.get(Campana, campana_id)
    if campana is None:
        raise HTTPException(status_code=404, detail="Campaña no encontrada")
    return campana


@router.get("", response_model=CampanaList)
def list_campanas(
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
) -> CampanaList:
    items = list(db.scalars(select(Campana).order_by(Campana.nombre)))
    return CampanaList(total=len(items), items=[CampanaOut.model_validate(c) for c in items])


@router.post("", response_model=CampanaOut, status_code=status.HTTP_201_CREATED)
def create_campana(
    payload: CampanaCreate,
    db: Session = Depends(get_db),
    user: Usuario = Depends(require_admin),
) -> Campana:
    if db.get(Plantilla, payload.plantilla_id) is None:
        raise HTTPException(status_code=404, detail="Plantilla no encontrada")
    campana = Campana(**payload.model_dump(), creado_por=user.id)
    db.add(campana)
    db.commit()
    db.refresh(campana)
    return campana


@router.post("/{campana_id}/generar", response_model=GenerarResultado)
def generar_comunicaciones(
    campana_id: uuid.UUID,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
) -> GenerarResultado:
    """Genera comunicaciones pendientes para las empresas del segmento.

    segmento: estado de empresa (p. ej. 'interesado') o 'rubro:<valor>'.
    """
    campana = _get_campana_or_404(campana_id, db)
    if campana.estado != EstadoCampana.borrador:
        raise HTTPException(status_code=409, detail="Solo se genera desde estado borrador")

    plantilla = db.get(Plantilla, campana.plantilla_id)
    query = select(Empresa).where(Empresa.deleted_at.is_(None))
    if campana.segmento:
        if campana.segmento.startswith("rubro:"):
            query = query.where(Empresa.rubro == campana.segmento.split(":", 1)[1])
        else:
            query = query.where(Empresa.estado == campana.segmento)
    empresas = db.scalars(query).all()

    generadas = 0
    omitidas = 0
    for empresa in empresas:
        contacto = empresa.contactos[0] if empresa.contactos else None
        motivo = validar_frecuencia(
            db, empresa.id, contacto.id if contacto else None, plantilla.id, campana.canal
        )
        if motivo:
            omitidas += 1
            continue

        variables = variables_disponibles(empresa, contacto)
        contenido, _ = renderizar(plantilla.contenido, variables)
        db.add(
            Comunicacion(
                empresa_id=empresa.id,
                contacto_id=contacto.id if contacto else None,
                canal=campana.canal,
                plantilla_id=plantilla.id,
                contenido=contenido,
                estado=EstadoComunicacion.pendiente,
                agente=f"campaña:{campana.nombre}",
            )
        )
        generadas += 1

    campana.estado = EstadoCampana.aprobada
    db.commit()
    return GenerarResultado(generadas=generadas, omitidas=omitidas)


@router.post("/{campana_id}/despachar")
def despachar_campana(
    campana_id: uuid.UUID,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
) -> dict:
    """Despacha a n8n las comunicaciones pendientes respetando el límite diario."""
    campana = _get_campana_or_404(campana_id, db)
    if campana.estado not in (EstadoCampana.aprobada, EstadoCampana.enviando):
        raise HTTPException(status_code=409, detail="La campaña no está aprobada")

    pendientes = db.scalars(
        select(Comunicacion).where(
            Comunicacion.plantilla_id == campana.plantilla_id,
            Comunicacion.estado == EstadoComunicacion.pendiente,
            Comunicacion.agente == f"campaña:{campana.nombre}",
        ).order_by(Comunicacion.created_at).limit(campana.limite_diario or 50)
    ).all()

    enviadas = 0
    for comunicacion in pendientes:
        empresa = db.get(Empresa, comunicacion.empresa_id)
        exito = despachar_n8n(
            "comunicacion.enviar",
            {
                "canal": comunicacion.canal.value,
                "empresa": empresa.razon_social if empresa else None,
                "contenido": comunicacion.contenido,
                "campana": campana.nombre,
            },
        )
        if exito:
            comunicacion.estado = EstadoComunicacion.enviado
            enviadas += 1

    campana.estado = EstadoCampana.enviando
    if campana.fecha_inicio is None:
        campana.fecha_inicio = datetime.now(timezone.utc)
    db.commit()
    return {"despachadas": enviadas, "pendientes_restantes": len(pendientes) - enviadas}
