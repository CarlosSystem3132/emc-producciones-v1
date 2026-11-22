"""Secuencias de seguimiento comercial (Fase 2 — docs/10).

Una secuencia define una serie de pasos (plantillas + días de espera) que se
envían de forma escalonada a una empresa/contacto inscrito. La lógica crítica
permanece en FastAPI; n8n solo despacha los mensajes (docs/03).
"""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.common import (
    GUID,
    CanalComunicacion,
    EstadoActivo,
    TimestampMixin,
    uuid_pk,
)


class Secuencia(Base, TimestampMixin):
    __tablename__ = "secuencias"

    id: Mapped[uuid.UUID] = uuid_pk()
    nombre: Mapped[str] = mapped_column(String(150), nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text)
    canal: Mapped[CanalComunicacion] = mapped_column(
        Enum(CanalComunicacion, name="canal_comunicacion", native_enum=False),
        nullable=False,
    )
    estado: Mapped[EstadoActivo] = mapped_column(
        Enum(EstadoActivo, name="estado_activo", native_enum=False),
        default=EstadoActivo.activo,
        nullable=False,
    )

    pasos: Mapped[list["SecuenciaPaso"]] = relationship(
        back_populates="secuencia",
        cascade="all, delete-orphan",
        order_by="SecuenciaPaso.orden",
    )
    inscripciones: Mapped[list["SecuenciaInscripcion"]] = relationship(
        back_populates="secuencia", cascade="all, delete-orphan"
    )


class SecuenciaPaso(Base):
    __tablename__ = "secuencia_pasos"

    id: Mapped[uuid.UUID] = uuid_pk()
    secuencia_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("secuencias.id", ondelete="CASCADE"), index=True
    )
    orden: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    dias_espera: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    plantilla_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("plantillas.id", ondelete="SET NULL")
    )
    mensaje: Mapped[str | None] = mapped_column(Text)  # texto plano si no hay plantilla
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    secuencia: Mapped["Secuencia"] = relationship(back_populates="pasos")


class SecuenciaInscripcion(Base, TimestampMixin):
    __tablename__ = "secuencia_inscripciones"

    id: Mapped[uuid.UUID] = uuid_pk()
    secuencia_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("secuencias.id", ondelete="CASCADE"), index=True
    )
    empresa_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("empresas.id", ondelete="CASCADE"), index=True
    )
    contacto_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("contactos.id", ondelete="SET NULL")
    )
    lead_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("leads.id", ondelete="SET NULL")
    )
    paso_actual: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    proxima_ejecucion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), index=True, nullable=False
    )
    estado: Mapped[str] = mapped_column(
        String(20), default="activa", nullable=False
    )  # activa, completada, cancelada
    ultimo_envio: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    secuencia: Mapped["Secuencia"] = relationship(back_populates="inscripciones")
