"""Schemas de reservas y bloqueos temporales."""
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.common import EstadoReserva
from app.schemas.empresa import ContactoCreate, EmpresaBase


class SolicitudReserva(BaseModel):
    """Flujo web de reserva (docs/06): datos de empresa + contacto + stand."""
    stand_id: uuid.UUID
    empresa: EmpresaBase
    contacto: ContactoCreate
    interes: str | None = Field(default=None, max_length=100)
    paquete_interes_id: uuid.UUID | None = None


class ReservaExtendRequest(BaseModel):
    minutos: int = Field(description="30 o 60 minutos adicionales")
    motivo: str = Field(min_length=3, max_length=500)


class ReservaVenderRequest(BaseModel):
    monto: float = Field(ge=0)
    comprobante_url: str | None = None
    contrato_url: str | None = None


class ReservaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    empresa_id: uuid.UUID
    lead_id: uuid.UUID | None = None
    stand_id: uuid.UUID
    ejecutivo_id: uuid.UUID | None = None
    estado: EstadoReserva
    fecha_inicio: datetime | None = None
    fecha_expiracion: datetime | None = None
    fecha_extension: datetime | None = None
    motivo_extension: str | None = None
    monto: float | None = None
    comprobante_url: str | None = None
    contrato_url: str | None = None
    created_at: datetime


class ReservaList(BaseModel):
    total: int
    items: list[ReservaOut]
