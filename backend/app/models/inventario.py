"""Inventario: zonas, stands y paquetes comerciales."""
from __future__ import annotations

import uuid

from sqlalchemy import Column, Enum, ForeignKey, Numeric, String, Table, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.db.base import Base
from app.models.common import (
    GUID,
    EstadoActivo,
    EstadoStand,
    TipoStand,
    TipoZona,
    TimestampMixin,
    uuid_pk,
)


class Zona(Base):
    __tablename__ = "zonas"

    id: Mapped[uuid.UUID] = uuid_pk()
    nombre: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    tipo: Mapped[TipoZona] = mapped_column(
        Enum(TipoZona, name="tipo_zona", native_enum=False), nullable=False
    )
    descripcion: Mapped[str | None] = mapped_column(Text)
    capacidad: Mapped[int | None] = mapped_column()

    stands: Mapped[list["Stand"]] = relationship(back_populates="zona")


class Stand(Base, TimestampMixin):
    __tablename__ = "stands"

    id: Mapped[uuid.UUID] = uuid_pk()
    codigo: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    zona_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("zonas.id", ondelete="RESTRICT"), index=True
    )
    tipo: Mapped[TipoStand] = mapped_column(
        Enum(TipoStand, name="tipo_stand", native_enum=False),
        default=TipoStand.stand,
        nullable=False,
    )
    dimensiones: Mapped[str | None] = mapped_column(String(100))
    precio_base: Mapped[float | None] = mapped_column(Numeric(12, 2))
    descripcion: Mapped[str | None] = mapped_column(Text)
    estado: Mapped[EstadoStand] = mapped_column(
        Enum(EstadoStand, name="estado_stand", native_enum=False),
        default=EstadoStand.disponible,
        nullable=False,
        index=True,
    )
    ejecutivo_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("usuarios.id", ondelete="SET NULL")
    )
    reserva_activa_id: Mapped[uuid.UUID | None] = mapped_column(GUID())

    zona: Mapped["Zona"] = relationship(back_populates="stands")
    paquetes: Mapped[list["Paquete"]] = relationship(
        secondary="paquete_stand", back_populates="stands"
    )


paquete_stand = Table(
    "paquete_stand",
    Base.metadata,
    Column("paquete_id", GUID(), ForeignKey("paquetes.id", ondelete="CASCADE"), primary_key=True),
    Column("stand_id", GUID(), ForeignKey("stands.id", ondelete="CASCADE"), primary_key=True),
)


class Paquete(Base, TimestampMixin):
    __tablename__ = "paquetes"

    id: Mapped[uuid.UUID] = uuid_pk()
    nombre: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text)
    precio: Mapped[float | None] = mapped_column(Numeric(12, 2))
    beneficios: Mapped[list | None] = mapped_column(JSON().with_variant(JSONB, "postgresql"))
    condiciones: Mapped[str | None] = mapped_column(Text)
    estado: Mapped[EstadoActivo] = mapped_column(
        Enum(EstadoActivo, name="estado_activo", native_enum=False),
        default=EstadoActivo.activo,
        nullable=False,
    )

    stands: Mapped[list["Stand"]] = relationship(
        secondary="paquete_stand", back_populates="paquetes"
    )
