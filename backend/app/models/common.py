"""Tipos y mixins compartidos por todos los modelos."""
from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import CHAR, TypeDecorator


class GUID(TypeDecorator):
    """UUID portable: usa UUID nativo en PostgreSQL y CHAR(36) en SQLite (tests)."""

    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PgUUID(as_uuid=True))
        return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        return str(value) if dialect.name != "postgresql" else value

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        return uuid.UUID(str(value))


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


def uuid_pk() -> Mapped[uuid.UUID]:
    return mapped_column(GUID(), primary_key=True, default=uuid.uuid4)


# ---------- Enumeraciones de negocio ----------

class RolUsuario(str, enum.Enum):
    admin = "admin"
    ejecutivo = "ejecutivo"
    presidencia = "presidencia"


class EstadoUsuario(str, enum.Enum):
    activo = "activo"
    bloqueado = "bloqueado"
    inactivo = "inactivo"


class EstadoLead(str, enum.Enum):
    prospecto = "prospecto"
    contactado = "contactado"
    interesado = "interesado"
    propuesta_enviada = "propuesta_enviada"
    en_negociacion = "en_negociacion"
    reserva_temporal = "reserva_temporal"
    reservado = "reservado"
    vendido = "vendido"
    descartado = "descartado"


class PrioridadLead(str, enum.Enum):
    alta = "alta"
    media = "media"
    baja = "baja"


class TamanoEmpresa(str, enum.Enum):
    pequena = "pequeña"
    mediana = "mediana"
    grande = "grande"


class TipoZona(str, enum.Enum):
    interior = "interior"
    exterior = "exterior"


class TipoStand(str, enum.Enum):
    stand = "stand"
    cancha = "cancha"
    espacio_exterior = "espacio_exterior"


class EstadoStand(str, enum.Enum):
    disponible = "disponible"
    bloqueado_temporal = "bloqueado_temporal"
    reservado = "reservado"
    vendido = "vendido"
    no_disponible = "no_disponible"


class EstadoReserva(str, enum.Enum):
    bloqueado = "bloqueado"
    reservado = "reservado"
    vendido = "vendido"
    expirado = "expirado"
    cancelado = "cancelado"


class EstadoActivo(str, enum.Enum):
    activo = "activo"
    inactivo = "inactivo"


class EstadoCampana(str, enum.Enum):
    borrador = "borrador"
    aprobada = "aprobada"
    enviando = "enviando"
    finalizada = "finalizada"


class CanalComunicacion(str, enum.Enum):
    email = "email"
    whatsapp = "whatsapp"
    chat = "chat"
    pdf = "pdf"


class EstadoComunicacion(str, enum.Enum):
    pendiente = "pendiente"  # en cola (campaña o esperando despacho n8n)
    enviado = "enviado"
    entregado = "entregado"
    leido = "leido"
    respondido = "respondido"
    error = "error"


class TipoActividad(str, enum.Enum):
    llamada = "llamada"
    nota = "nota"
    correo = "correo"
    whatsapp = "whatsapp"
    reunion = "reunion"
    cambio_estado = "cambio_estado"


class TipoDocumento(str, enum.Enum):
    propuesta = "propuesta"
    contrato = "contrato"
    comprobante = "comprobante"


class TipoNotificacion(str, enum.Enum):
    reserva = "reserva"
    lead = "lead"
    seguimiento = "seguimiento"
    alerta = "alerta"


class EstadoNotificacion(str, enum.Enum):
    pendiente = "pendiente"
    enviado = "enviado"
    leido = "leido"
