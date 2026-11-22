"""Reservas y bloqueos temporales de stands."""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.common import GUID, EstadoReserva, TimestampMixin, uuid_pk


class Reserva(Base, TimestampMixin):
    __tablename__ = "reservas"

    id: Mapped[uuid.UUID] = uuid_pk()
    empresa_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("empresas.id", ondelete="RESTRICT"), index=True
    )
    lead_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("leads.id", ondelete="SET NULL")
    )
    stand_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("stands.id", ondelete="RESTRICT"), index=True
    )
    ejecutivo_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("usuarios.id", ondelete="SET NULL")
    )
    estado: Mapped[EstadoReserva] = mapped_column(
        Enum(EstadoReserva, name="estado_reserva", native_enum=False),
        default=EstadoReserva.bloqueado,
        nullable=False,
        index=True,
    )
    fecha_inicio: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    fecha_expiracion: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    fecha_extension: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    motivo_extension: Mapped[str | None] = mapped_column(Text)
    monto: Mapped[float | None] = mapped_column(Numeric(12, 2))
    comprobante_url: Mapped[str | None] = mapped_column(String(500))
    contrato_url: Mapped[str | None] = mapped_column(String(500))
