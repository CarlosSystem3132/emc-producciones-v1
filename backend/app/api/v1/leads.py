"""CRUD de leads y embudo comercial.

Reglas (docs/04):
- El ejecutivo ve únicamente sus leads; el admin ve todos.
- Estados del embudo: prospecto → contactado → interesado → propuesta_enviada
  → en_negociacion → reserva_temporal → reservado → vendido / descartado.
- El cambio de estado queda registrado como actividad (auditoría).
"""
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_admin
from app.db.session import get_db
from app.models.common import EstadoLead, PrioridadLead, TipoActividad
from app.models.comunicaciones import Actividad
from app.models.crm import Empresa, Lead
from app.models.user import Usuario
from app.schemas.lead import LeadCreate, LeadList, LeadOut, LeadUpdate

router = APIRouter(prefix="/leads", tags=["leads"])


def _get_lead_or_404(lead_id: uuid.UUID, db: Session, user: Usuario) -> Lead:
    lead = db.get(Lead, lead_id)
    if lead is None or lead.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Lead no encontrado")
    if not user.is_admin and lead.ejecutivo_id != user.id:
        raise HTTPException(status_code=403, detail="Sin permiso sobre este lead")
    return lead


@router.get("", response_model=LeadList)
def list_leads(
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
    estado: EstadoLead | None = Query(default=None),
    prioridad: PrioridadLead | None = Query(default=None),
    rubro: str | None = Query(default=None),
    ejecutivo_id: uuid.UUID | None = Query(default=None),
    search: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> LeadList:
    query = select(Lead).where(Lead.deleted_at.is_(None))
    if not user.is_admin:
        query = query.where(Lead.ejecutivo_id == user.id)
    if estado:
        query = query.where(Lead.estado == estado)
    if prioridad:
        query = query.where(Lead.prioridad == prioridad)
    if rubro:
        query = query.where(Lead.rubro == rubro)
    if ejecutivo_id:
        query = query.where(Lead.ejecutivo_id == ejecutivo_id)
    if search:
        query = query.where(Lead.proxima_accion.ilike(f"%{search}%"))

    total = db.scalar(select(func.count()).select_from(query.subquery())) or 0
    items = db.scalars(
        query.order_by(Lead.created_at.desc()).limit(limit).offset(offset)
    ).all()
    return LeadList(total=total, items=[LeadOut.model_validate(l) for l in items])


@router.get("/embudo", tags=["leads"])
def embudo(
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
) -> dict:
    """Conteo de leads por estado (embudo comercial)."""
    query = select(Lead.estado, func.count()).where(Lead.deleted_at.is_(None))
    if not user.is_admin:
        query = query.where(Lead.ejecutivo_id == user.id)
    query = query.group_by(Lead.estado)
    conteo = {estado.value: 0 for estado in EstadoLead}
    for estado, cantidad in db.execute(query):
        conteo[estado.value] = cantidad
    return conteo


@router.post("", response_model=LeadOut, status_code=status.HTTP_201_CREATED)
def create_lead(
    payload: LeadCreate,
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
) -> Lead:
    empresa = db.get(Empresa, payload.empresa_id)
    if empresa is None or empresa.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
    if not user.is_admin and empresa.ejecutivo_id != user.id and empresa.creado_por != user.id:
        raise HTTPException(status_code=403, detail="Sin permiso sobre esta empresa")

    data = payload.model_dump()
    if not user.is_admin:
        data["ejecutivo_id"] = user.id
    elif data.get("ejecutivo_id") is None:
        data["ejecutivo_id"] = empresa.ejecutivo_id or user.id

    lead = Lead(**data)
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return lead


@router.get("/{lead_id}", response_model=LeadOut)
def get_lead(
    lead_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
) -> Lead:
    return _get_lead_or_404(lead_id, db, user)


@router.patch("/{lead_id}", response_model=LeadOut)
def update_lead(
    lead_id: uuid.UUID,
    payload: LeadUpdate,
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
) -> Lead:
    lead = _get_lead_or_404(lead_id, db, user)
    data = payload.model_dump(exclude_unset=True)

    if not user.is_admin:
        data.pop("ejecutivo_id", None)

    estado_anterior = lead.estado
    for field, value in data.items():
        setattr(lead, field, value)

    # Auditoría: registrar cambios de estado como actividad
    if "estado" in data and data["estado"] != estado_anterior:
        db.add(
            Actividad(
                empresa_id=lead.empresa_id,
                lead_id=lead.id,
                usuario_id=user.id,
                tipo=TipoActividad.cambio_estado,
                descripcion=f"Estado: {estado_anterior.value} → {lead.estado.value}",
            )
        )
    db.commit()
    db.refresh(lead)
    return lead


@router.delete("/{lead_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_lead(
    lead_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
) -> None:
    lead = _get_lead_or_404(lead_id, db, user)
    lead.deleted_at = lead.created_at  # soft delete
    db.commit()
