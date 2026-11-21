"""Tabla usuarios: administradores, ejecutivos de ventas y presidencia."""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.common import (
    GUID,
    EstadoUsuario,
    RolUsuario,
    TimestampMixin,
    uuid_pk,
)


class Usuario(Base, TimestampMixin):
    __tablename__ = "usuarios"

    id: Mapped[uuid.UUID] = uuid_pk()
    nombre_completo: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    telefono: Mapped[str | None] = mapped_column(String(50))
    whatsapp: Mapped[str | None] = mapped_column(String(50))
    correo_contacto: Mapped[str | None] = mapped_column(String(255))
    cargo: Mapped[str | None] = mapped_column(String(100))
    experiencia: Mapped[str | None] = mapped_column(String(500))
    especialidad: Mapped[str | None] = mapped_column(String(150))
    foto_url: Mapped[str | None] = mapped_column(String(500))
    rol: Mapped[RolUsuario] = mapped_column(
        Enum(RolUsuario, name="rol_usuario", native_enum=False),
        default=RolUsuario.ejecutivo,
        nullable=False,
    )
    estado: Mapped[EstadoUsuario] = mapped_column(
        Enum(EstadoUsuario, name="estado_usuario", native_enum=False),
        default=EstadoUsuario.activo,
        nullable=False,
    )
    creado_por: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("usuarios.id", ondelete="SET NULL")
    )
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # Relaciones
    empresas_asignadas: Mapped[list["Empresa"]] = relationship(  # noqa: F821
        back_populates="ejecutivo", foreign_keys="Empresa.ejecutivo_id"
    )

    @property
    def is_admin(self) -> bool:
        return self.rol == RolUsuario.admin
