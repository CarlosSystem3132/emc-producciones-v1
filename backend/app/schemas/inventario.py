"""Schemas de inventario: zonas, stands y paquetes."""
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.common import EstadoActivo, EstadoStand, TipoStand, TipoZona


# ---------- Zonas ----------

class ZonaBase(BaseModel):
    nombre: str = Field(min_length=2, max_length=150)
    tipo: TipoZona
    descripcion: str | None = None
    capacidad: int | None = Field(default=None, ge=0)


class ZonaCreate(ZonaBase):
    pass


class ZonaUpdate(BaseModel):
    nombre: str | None = Field(default=None, min_length=2, max_length=150)
    tipo: TipoZona | None = None
    descripcion: str | None = None
    capacidad: int | None = Field(default=None, ge=0)


class ZonaOut(ZonaBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID


# ---------- Stands ----------

class StandBase(BaseModel):
    codigo: str = Field(min_length=1, max_length=50)
    tipo: TipoStand = TipoStand.stand
    dimensiones: str | None = Field(default=None, max_length=100)
    precio_base: float | None = Field(default=None, ge=0)
    descripcion: str | None = None


class StandCreate(StandBase):
    zona_id: uuid.UUID


class StandUpdate(BaseModel):
    codigo: str | None = Field(default=None, min_length=1, max_length=50)
    zona_id: uuid.UUID | None = None
    tipo: TipoStand | None = None
    dimensiones: str | None = None
    precio_base: float | None = Field(default=None, ge=0)
    descripcion: str | None = None
    estado: EstadoStand | None = None
    ejecutivo_id: uuid.UUID | None = None


class StandOut(StandBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    zona_id: uuid.UUID
    estado: EstadoStand
    ejecutivo_id: uuid.UUID | None = None
    reserva_activa_id: uuid.UUID | None = None
    created_at: datetime
    updated_at: datetime


class StandList(BaseModel):
    total: int
    items: list[StandOut]


# ---------- Paquetes ----------

class PaqueteBase(BaseModel):
    nombre: str = Field(min_length=2, max_length=100)
    descripcion: str | None = None
    precio: float | None = Field(default=None, ge=0)
    beneficios: list[str] | None = None
    condiciones: str | None = None
    estado: EstadoActivo = EstadoActivo.activo


class PaqueteCreate(PaqueteBase):
    pass


class PaqueteUpdate(BaseModel):
    nombre: str | None = Field(default=None, min_length=2, max_length=100)
    descripcion: str | None = None
    precio: float | None = Field(default=None, ge=0)
    beneficios: list[str] | None = None
    condiciones: str | None = None
    estado: EstadoActivo | None = None


class PaqueteOut(PaqueteBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime


# ---------- Plano público ----------

class StandPlano(BaseModel):
    """Stand recortado para el plano interactivo público."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    codigo: str
    tipo: TipoStand
    estado: EstadoStand
    dimensiones: str | None = None
    precio_base: float | None = None
    zona_id: uuid.UUID
    zona_nombre: str


class PlanoOut(BaseModel):
    zonas: list[ZonaOut]
    stands: list[StandPlano]
