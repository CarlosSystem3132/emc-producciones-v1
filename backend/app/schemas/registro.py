"""Schemas del formulario público de registro de empresas."""
from pydantic import BaseModel, EmailStr, Field


class RegistroPublico(BaseModel):
    """Formulario web público (docs/02 — módulo público)."""
    # Empresa
    razon_social: str = Field(min_length=2, max_length=255)
    nombre_comercial: str | None = Field(default=None, max_length=255)
    rubro: str | None = Field(default=None, max_length=150)
    ciudad: str | None = Field(default=None, max_length=150)
    pais: str | None = Field(default=None, max_length=150)
    sitio_web: str | None = Field(default=None, max_length=255)
    # Contacto
    nombre_contacto: str = Field(min_length=2, max_length=150)
    cargo_contacto: str | None = Field(default=None, max_length=150)
    email: EmailStr | None = None
    whatsapp: str | None = Field(default=None, max_length=50)
    telefono: str | None = Field(default=None, max_length=50)
    # Solicitud
    tipo_solicitud: str = Field(default="registro", description="registro | propuesta")
    mensaje: str | None = Field(default=None, max_length=1000)


class RegistroPublicoOut(BaseModel):
    ok: bool = True
    mensaje: str
