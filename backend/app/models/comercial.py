"""Módulo comercial avanzado (Fase 4 — docs/10).

- Pago: registro de pagos contra una reserva (integración con pagos).
- Factura: registro de facturas emitidas (integración con facturación).
- FirmaDigital: solicitud y firma de contratos (firma digital supervisada).
"""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.common import GUID, TimestampMixin, uuid_pk


class Pago(Base, TimestampMixin):
    __tablename__ = "pagos"

    id: Mapped[uuid.UUID] = uuid_pk()
    reserva_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("reservas.id", ondelete="CASCADE"), index=True
    )
    empresa_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("empresas.id", ondelete="SET NULL")
    )
    monto: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    metodo: Mapped[str] = mapped_column(String(30), nullable=False, default="efectivo")
    # efectivo, transferencia, qr, tarjeta, otro
    referencia: Mapped[str | None] = mapped_column(String(120))
    estado: Mapped[str] = mapped_column(
        String(20), nullable=False, default="pendiente"
    )  # pendiente, confirmado, anulado
    notas: Mapped[str | None] = mapped_column(Text)
    registrado_por: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("usuarios.id", ondelete="SET NULL")
    )


class Factura(Base, TimestampMixin):
    __tablename__ = "facturas"

    id: Mapped[uuid.UUID] = uuid_pk()
    reserva_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("reservas.id", ondelete="SET NULL"), index=True
    )
    empresa_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("empresas.id", ondelete="SET NULL")
    )
    numero: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    nit: Mapped[str | None] = mapped_column(String(50))
    razon_social: Mapped[str | None] = mapped_column(String(255))
    monto: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    estado: Mapped[str] = mapped_column(
        String(20), nullable=False, default="borrador"
    )  # borrador, emitida, anulada
    notas: Mapped[str | None] = mapped_column(Text)


class FirmaDigital(Base, TimestampMixin):
    __tablename__ = "firmas_digitales"

    id: Mapped[uuid.UUID] = uuid_pk()
    reserva_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("reservas.id", ondelete="CASCADE"), index=True
    )
    token: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    firmante_nombre: Mapped[str] = mapped_column(String(150), nullable=False)
    firmante_email: Mapped[str | None] = mapped_column(String(255))
    firma_hash: Mapped[str | None] = mapped_column(String(128))
    ip: Mapped[str | None] = mapped_column(String(50))
    estado: Mapped[str] = mapped_column(
        String(20), nullable=False, default="pendiente"
    )  # pendiente, firmada
    firmada_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
