"""Schemas de plantillas, comunicaciones y campañas (Fase 2)."""
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.common import (
    CanalComunicacion,
    EstadoActivo,
    EstadoCampana,
    EstadoComunicacion,
)


# ---------- Plantillas ----------

class PlantillaBase(BaseModel):
    nombre: str = Field(min_length=2, max_length=150)
    tipo: str = Field(max_length=50, description="invitacion, propuesta, contrato, nutricion…")
    canal: CanalComunicacion
    contenido: str = Field(min_length=1)
    estado: EstadoActivo = EstadoActivo.activo


class PlantillaCreate(PlantillaBase):
    pass


class PlantillaUpdate(BaseModel):
    nombre: str | None = Field(default=None, min_length=2, max_length=150)
    tipo: str | None = None
    canal: CanalComunicacion | None = None
    contenido: str | None = None
    estado: EstadoActivo | None = None


class PlantillaOut(PlantillaBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime


class RenderRequest(BaseModel):
    variables: dict[str, str] = Field(default_factory=dict)


class RenderOut(BaseModel):
    contenido: str
    variables_faltantes: list[str]


# ---------- Comunicaciones ----------

class EnviarComunicacion(BaseModel):
    """Envío de una plantilla a una empresa/contacto (Fase 2).
    El plantilla_id viene en la ruta."""
    empresa_id: uuid.UUID
    contacto_id: uuid.UUID | None = None
    canal: CanalComunicacion | None = None  # por defecto, el de la plantilla
    variables_extra: dict[str, str] = Field(default_factory=dict)


class ComunicacionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    empresa_id: uuid.UUID | None = None
    lead_id: uuid.UUID | None = None
    contacto_id: uuid.UUID | None = None
    canal: CanalComunicacion
    plantilla_id: uuid.UUID | None = None
    contenido: str | None = None
    estado: EstadoComunicacion
    agente: str | None = None
    created_at: datetime


class ComunicacionList(BaseModel):
    total: int
    items: list[ComunicacionOut]


# ---------- Campañas ----------

class CampanaCreate(BaseModel):
    nombre: str = Field(min_length=2, max_length=150)
    segmento: str | None = Field(default=None, max_length=150, description="estado de empresa o rubro")
    plantilla_id: uuid.UUID
    canal: CanalComunicacion
    limite_diario: int = Field(default=50, ge=1, le=1000)


class CampanaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    nombre: str
    segmento: str | None = None
    plantilla_id: uuid.UUID | None = None
    canal: CanalComunicacion
    estado: EstadoCampana
    fecha_inicio: datetime | None = None
    fecha_fin: datetime | None = None
    limite_diario: int | None = None
    creado_por: uuid.UUID | None = None


class CampanaList(BaseModel):
    total: int
    items: list[CampanaOut]


class GenerarResultado(BaseModel):
    generadas: int
    omitidas: int
