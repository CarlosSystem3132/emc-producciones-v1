"""Configuración de los agentes de IA (docs/09) editable desde el panel.

Cada agente tiene:
- prompt_sistema: instrucciones que el administrador puede editar.
- modo_autonomia: cómo trabaja el agente:
    - "automatico": ejecuta sus acciones sin pedir confirmación.
    - "asistido": propone y espera confirmación humana (por defecto).
    - "manual": solo actúa cuando un humano lo solicita expresamente.
- activo: si está desactivado, el agente no interviene (fallback local).
"""
from __future__ import annotations

import uuid

from sqlalchemy import Boolean, Enum, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.common import EstadoActivo, TimestampMixin, uuid_pk


class ConfigAgente(Base, TimestampMixin):
    __tablename__ = "config_agentes"

    id: Mapped[uuid.UUID] = uuid_pk()
    clave: Mapped[str] = mapped_column(String(30), unique=True, index=True, nullable=False)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text)
    prompt_sistema: Mapped[str] = mapped_column(Text, nullable=False)
    modo_autonomia: Mapped[str] = mapped_column(
        String(20), nullable=False, default="asistido"
    )  # automatico | asistido | manual
    activo: Mapped[EstadoActivo] = mapped_column(
        Enum(EstadoActivo, name="estado_activo", native_enum=False),
        default=EstadoActivo.activo,
        nullable=False,
    )
