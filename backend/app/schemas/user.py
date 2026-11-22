"""Schemas de usuarios (ejecutivos y administradores)."""
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.common import EstadoUsuario, RolUsuario


class UserBase(BaseModel):
    nombre_completo: str = Field(min_length=3, max_length=150)
    email: EmailStr
    telefono: str | None = Field(default=None, max_length=50)
    whatsapp: str | None = Field(default=None, max_length=50)
    correo_contacto: EmailStr | None = None
    cargo: str | None = Field(default=None, max_length=100)
    experiencia: str | None = Field(default=None, max_length=500)
    especialidad: str | None = Field(default=None, max_length=150)
    foto_url: str | None = Field(default=None, max_length=500)


class UserCreate(UserBase):
    """Solo el administrador puede crear ejecutivos (docs/07)."""
    password: str = Field(min_length=8, max_length=128)
    rol: RolUsuario = RolUsuario.ejecutivo
    estado: EstadoUsuario = EstadoUsuario.activo


class UserUpdate(BaseModel):
    """Edición parcial. El administrador edita todo; el ejecutivo solo su perfil."""
    nombre_completo: str | None = Field(default=None, min_length=3, max_length=150)
    telefono: str | None = None
    whatsapp: str | None = None
    correo_contacto: EmailStr | None = None
    cargo: str | None = None
    experiencia: str | None = None
    especialidad: str | None = None
    foto_url: str | None = None
    # Campos exclusivos del administrador
    rol: RolUsuario | None = None
    estado: EstadoUsuario | None = None


class PasswordReset(BaseModel):
    new_password: str = Field(min_length=8, max_length=128)


class PasswordChange(BaseModel):
    """Cambio de contraseña del propio usuario (docs/08 — perfil del ejecutivo)."""
    current_password: str = Field(min_length=1, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)


class UserOut(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    rol: RolUsuario
    estado: EstadoUsuario
    creado_por: uuid.UUID | None = None
    created_at: datetime
    updated_at: datetime


class UserList(BaseModel):
    total: int
    items: list[UserOut]
