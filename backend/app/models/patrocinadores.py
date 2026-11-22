"""Patrocinadores de la expo (Fase 4 — panel para patrocinadores)."""
from __future__ import annotations

import uuid

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.common import EstadoActivo, TimestampMixin, uuid_pk
from sqlalchemy import Enum


class Patrocinador(Base, TimestampMixin):
    __tablename__ = "patrocinadores"

    id: Mapped[uuid.UUID] = uuid_pk()
    nombre: Mapped[str] = mapped_column(String(150), nullable=False)
    categoria: Mapped[str | None] = mapped_column(String(50))  # oro, plata, bronce, aliado
    logo_url: Mapped[str | None] = mapped_column(String(500))
    sitio_web: Mapped[str | None] = mapped_column(String(255))
    estado: Mapped[EstadoActivo] = mapped_column(
        Enum(EstadoActivo, name="estado_activo", native_enum=False),
        default=EstadoActivo.activo,
        nullable=False,
    )
    orden: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
