"""Schemas de leads (embudo comercial)."""
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.common import EstadoLead, PrioridadLead


class LeadBase(BaseModel):
    origen: str | None = Field(default=None, max_length=50)
    rubro: str | None = Field(default=None, max_length=150)
    interes: str | None = Field(default=None, max_length=100)
    prioridad: PrioridadLead = PrioridadLead.media
    estado: EstadoLead = EstadoLead.prospecto
    proxima_accion: str | None = None
    fecha_proxima_accion: datetime | None = None


class LeadCreate(LeadBase):
    empresa_id: uuid.UUID
    contacto_id: uuid.UUID | None = None
    paquete_interes_id: uuid.UUID | None = None
    stand_interes_id: uuid.UUID | None = None


class LeadUpdate(BaseModel):
    contacto_id: uuid.UUID | None = None
    paquete_interes_id: uuid.UUID | None = None
    stand_interes_id: uuid.UUID | None = None
    origen: str | None = None
    rubro: str | None = None
    interes: str | None = None
    prioridad: PrioridadLead | None = None
    estado: EstadoLead | None = None
    proxima_accion: str | None = None
    fecha_proxima_accion: datetime | None = None
    ejecutivo_id: uuid.UUID | None = None  # solo admin reasigna


class LeadOut(LeadBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    empresa_id: uuid.UUID
    contacto_id: uuid.UUID | None = None
    ejecutivo_id: uuid.UUID | None = None
    paquete_interes_id: uuid.UUID | None = None
    stand_interes_id: uuid.UUID | None = None
    created_at: datetime


class LeadList(BaseModel):
    total: int
    items: list[LeadOut]
