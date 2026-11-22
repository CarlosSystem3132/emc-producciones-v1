"""Comunicación comercial: plantillas, campañas, comunicaciones, actividades,
documentos y notificaciones."""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.common import (
    GUID,
    CanalComunicacion,
    EstadoActivo,
    EstadoCampana,
    EstadoComunicacion,
    EstadoNotificacion,
    TipoActividad,
    TipoDocumento,
    TipoNotificacion,
    TimestampMixin,
    uuid_pk,
)


class Plantilla(Base):
    __tablename__ = "plantillas"

    id: Mapped[uuid.UUID] = uuid_pk()
    nombre: Mapped[str] = mapped_column(String(150), nullable=False)
    tipo: Mapped[str] = mapped_column(String(50), nullable=False)  # invitacion, propuesta, contrato, nutricion
    canal: Mapped[CanalComunicacion] = mapped_column(
        Enum(CanalComunicacion, name="canal_comunicacion", native_enum=False), nullable=False
    )
    contenido: Mapped[str] = mapped_column(Text, nullable=False)
    estado: Mapped[EstadoActivo] = mapped_column(
        Enum(EstadoActivo, name="estado_activo", native_enum=False),
        default=EstadoActivo.activo,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class Campana(Base):
    __tablename__ = "campanas"

    id: Mapped[uuid.UUID] = uuid_pk()
    nombre: Mapped[str] = mapped_column(String(150), nullable=False)
    segmento: Mapped[str | None] = mapped_column(String(150))
    plantilla_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("plantillas.id", ondelete="SET NULL")
    )
    canal: Mapped[CanalComunicacion] = mapped_column(
        Enum(CanalComunicacion, name="canal_comunicacion", native_enum=False), nullable=False
    )
    estado: Mapped[EstadoCampana] = mapped_column(
        Enum(EstadoCampana, name="estado_campana", native_enum=False),
        default=EstadoCampana.borrador,
        nullable=False,
        index=True,
    )
    fecha_inicio: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    fecha_fin: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    limite_diario: Mapped[int | None] = mapped_column(Integer)
    creado_por: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("usuarios.id", ondelete="SET NULL")
    )


class Comunicacion(Base):
    __tablename__ = "comunicaciones"

    id: Mapped[uuid.UUID] = uuid_pk()
    empresa_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("empresas.id", ondelete="SET NULL"), index=True
    )
    lead_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("leads.id", ondelete="SET NULL")
    )
    contacto_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("contactos.id", ondelete="SET NULL")
    )
    canal: Mapped[CanalComunicacion] = mapped_column(
        Enum(CanalComunicacion, name="canal_comunicacion", native_enum=False), nullable=False
    )
    plantilla_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("plantillas.id", ondelete="SET NULL")
    )
    contenido: Mapped[str | None] = mapped_column(Text)
    estado: Mapped[EstadoComunicacion] = mapped_column(
        Enum(EstadoComunicacion, name="estado_comunicacion", native_enum=False),
        default=EstadoComunicacion.enviado,
        nullable=False,
    )
    agente: Mapped[str | None] = mapped_column(String(100))  # usuario o agente de IA
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class Actividad(Base):
    __tablename__ = "actividades"

    id: Mapped[uuid.UUID] = uuid_pk()
    empresa_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("empresas.id", ondelete="SET NULL"), index=True
    )
    lead_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("leads.id", ondelete="SET NULL")
    )
    usuario_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("usuarios.id", ondelete="SET NULL")
    )
    tipo: Mapped[TipoActividad] = mapped_column(
        Enum(TipoActividad, name="tipo_actividad", native_enum=False), nullable=False
    )
    descripcion: Mapped[str | None] = mapped_column(Text)
    resultado: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class Documento(Base):
    __tablename__ = "documentos"

    id: Mapped[uuid.UUID] = uuid_pk()
    empresa_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("empresas.id", ondelete="SET NULL")
    )
    lead_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("leads.id", ondelete="SET NULL")
    )
    tipo: Mapped[TipoDocumento] = mapped_column(
        Enum(TipoDocumento, name="tipo_documento", native_enum=False), nullable=False
    )
    nombre: Mapped[str] = mapped_column(String(255), nullable=False)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class Notificacion(Base):
    __tablename__ = "notificaciones"

    id: Mapped[uuid.UUID] = uuid_pk()
    usuario_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("usuarios.id", ondelete="CASCADE"), index=True
    )
    tipo: Mapped[TipoNotificacion] = mapped_column(
        Enum(TipoNotificacion, name="tipo_notificacion", native_enum=False), nullable=False
    )
    titulo: Mapped[str] = mapped_column(String(255), nullable=False)
    mensaje: Mapped[str | None] = mapped_column(Text)
    canal: Mapped[str] = mapped_column(String(20), default="panel", nullable=False)
    estado: Mapped[EstadoNotificacion] = mapped_column(
        Enum(EstadoNotificacion, name="estado_notificacion", native_enum=False),
        default=EstadoNotificacion.pendiente,
        nullable=False,
    )
    referencia_id: Mapped[uuid.UUID | None] = mapped_column(GUID())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
