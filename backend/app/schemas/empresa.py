"""Schemas de empresas y contactos."""
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.common import EstadoLead, TamanoEmpresa


class ContactoBase(BaseModel):
    nombre: str = Field(min_length=2, max_length=150)
    cargo: str | None = Field(default=None, max_length=150)
    email: EmailStr | None = None
    whatsapp: str | None = Field(default=None, max_length=50)
    telefono: str | None = Field(default=None, max_length=50)
    estado: str = "activo"


class ContactoCreate(ContactoBase):
    pass


class ContactoOut(ContactoBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    empresa_id: uuid.UUID


class EmpresaBase(BaseModel):
    razon_social: str = Field(min_length=2, max_length=255)
    nombre_comercial: str | None = Field(default=None, max_length=255)
    rubro: str | None = Field(default=None, max_length=150)
    ciudad: str | None = Field(default=None, max_length=150)
    pais: str | None = Field(default=None, max_length=150)
    sitio_web: str | None = Field(default=None, max_length=255)
    linkedin: str | None = Field(default=None, max_length=255)
    facebook: str | None = Field(default=None, max_length=255)
    instagram: str | None = Field(default=None, max_length=255)
    tamano_empresa: TamanoEmpresa | None = None
    estado: EstadoLead = EstadoLead.prospecto
    origen: str | None = Field(default=None, max_length=50)


class EmpresaCreate(EmpresaBase):
    ejecutivo_id: uuid.UUID | None = None
    contacto: ContactoCreate | None = None  # contacto principal opcional


class EmpresaUpdate(BaseModel):
    razon_social: str | None = Field(default=None, min_length=2, max_length=255)
    nombre_comercial: str | None = None
    rubro: str | None = None
    ciudad: str | None = None
    pais: str | None = None
    sitio_web: str | None = None
    linkedin: str | None = None
    facebook: str | None = None
    instagram: str | None = None
    tamano_empresa: TamanoEmpresa | None = None
    estado: EstadoLead | None = None
    origen: str | None = None
    ejecutivo_id: uuid.UUID | None = None  # solo admin reasigna


class EmpresaOut(EmpresaBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    ejecutivo_id: uuid.UUID | None = None
    creado_por: uuid.UUID | None = None
    created_at: datetime
    updated_at: datetime


class EmpresaDetail(EmpresaOut):
    contactos: list[ContactoOut] = []


class EmpresaList(BaseModel):
    total: int
    items: list[EmpresaOut]
