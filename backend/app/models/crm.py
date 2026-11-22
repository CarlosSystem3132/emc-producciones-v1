"""Tablas del CRM: empresas, contactos y leads."""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.common import (
    GUID,
    EstadoLead,
    PrioridadLead,
    TamanoEmpresa,
    TimestampMixin,
    uuid_pk,
)


class Empresa(Base, TimestampMixin):
    __tablename__ = "empresas"

    id: Mapped[uuid.UUID] = uuid_pk()
    razon_social: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    nombre_comercial: Mapped[str | None] = mapped_column(String(255))
    rubro: Mapped[str | None] = mapped_column(String(150), index=True)
    ciudad: Mapped[str | None] = mapped_column(String(150))
    pais: Mapped[str | None] = mapped_column(String(150))
    sitio_web: Mapped[str | None] = mapped_column(String(255))
    linkedin: Mapped[str | None] = mapped_column(String(255))
    facebook: Mapped[str | None] = mapped_column(String(255))
    instagram: Mapped[str | None] = mapped_column(String(255))
    tamano_empresa: Mapped[TamanoEmpresa | None] = mapped_column(
        Enum(TamanoEmpresa, name="tamano_empresa", native_enum=False)
    )
    estado: Mapped[EstadoLead] = mapped_column(
        Enum(EstadoLead, name="estado_lead", native_enum=False),
        default=EstadoLead.prospecto,
        nullable=False,
        index=True,
    )
    ejecutivo_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("usuarios.id", ondelete="SET NULL"), index=True
    )
    origen: Mapped[str | None] = mapped_column(String(50))  # web, chat, whatsapp, importacion, prospeccion
    creado_por: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("usuarios.id", ondelete="SET NULL")
    )
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    ejecutivo: Mapped["Usuario | None"] = relationship(  # noqa: F821
        back_populates="empresas_asignadas", foreign_keys=[ejecutivo_id]
    )
    contactos: Mapped[list["Contacto"]] = relationship(
        back_populates="empresa", cascade="all, delete-orphan"
    )
    leads: Mapped[list["Lead"]] = relationship(back_populates="empresa")


class Contacto(Base):
    __tablename__ = "contactos"

    id: Mapped[uuid.UUID] = uuid_pk()
    empresa_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("empresas.id", ondelete="CASCADE"), index=True
    )
    nombre: Mapped[str] = mapped_column(String(150), nullable=False)
    cargo: Mapped[str | None] = mapped_column(String(150))
    email: Mapped[str | None] = mapped_column(String(255), index=True)
    whatsapp: Mapped[str | None] = mapped_column(String(50), index=True)
    telefono: Mapped[str | None] = mapped_column(String(50))
    estado: Mapped[str] = mapped_column(String(20), default="activo", nullable=False)

    empresa: Mapped["Empresa"] = relationship(back_populates="contactos")


class Lead(Base, TimestampMixin):
    __tablename__ = "leads"

    id: Mapped[uuid.UUID] = uuid_pk()
    empresa_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("empresas.id", ondelete="CASCADE"), index=True
    )
    contacto_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("contactos.id", ondelete="SET NULL")
    )
    ejecutivo_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("usuarios.id", ondelete="SET NULL"), index=True
    )
    origen: Mapped[str | None] = mapped_column(String(50))
    rubro: Mapped[str | None] = mapped_column(String(150), index=True)
    interes: Mapped[str | None] = mapped_column(String(100))
    prioridad: Mapped[PrioridadLead] = mapped_column(
        Enum(PrioridadLead, name="prioridad_lead", native_enum=False),
        default=PrioridadLead.media,
        nullable=False,
    )
    paquete_interes_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("paquetes.id", ondelete="SET NULL")
    )
    stand_interes_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("stands.id", ondelete="SET NULL")
    )
    estado: Mapped[EstadoLead] = mapped_column(
        Enum(EstadoLead, name="estado_lead", native_enum=False),
        default=EstadoLead.prospecto,
        nullable=False,
        index=True,
    )
    proxima_accion: Mapped[str | None] = mapped_column(Text)
    fecha_proxima_accion: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    empresa: Mapped["Empresa"] = relationship(back_populates="leads")
