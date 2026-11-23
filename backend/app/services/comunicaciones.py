"""Servicios de comunicación comercial (Fase 2).

- Renderizado de plantillas con variables {{variable}}.
- Control de frecuencia y prevención de duplicados (docs/10).
- Despacho a n8n (Gmail / WhatsApp Cloud API vía webhooks).
"""
import json
import re
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.common import CanalComunicacion, EstadoComunicacion
from app.models.comunicaciones import Comunicacion, Plantilla
from app.models.crm import Contacto, Empresa

VAR_PATTERN = re.compile(r"\{\{\s*([a-zA-Z0-9_]+)\s*\}\}")

# Reglas de frecuencia (docs/10 — control de frecuencia y prevención de duplicados)
MAX_POR_EMPRESA_DIA = 5
HORAS_ANTIDUPLICADO = 24


def renderizar(contenido: str, variables: dict[str, str]) -> tuple[str, list[str]]:
    """Sustituye {{variables}}. Devuelve (texto, variables faltantes)."""
    faltantes = [
        nombre
        for nombre in sorted(set(VAR_PATTERN.findall(contenido)))
        if nombre not in variables
    ]

    def reemplazo(match: re.Match) -> str:
        nombre = match.group(1)
        return variables.get(nombre, match.group(0))

    return VAR_PATTERN.sub(reemplazo, contenido), faltantes


def variables_disponibles(empresa: Empresa, contacto: Contacto | None) -> dict[str, str]:
    """Variables estándar para renderizar plantillas."""
    vars_base = {
        "empresa": empresa.razon_social,
        "nombre_comercial": empresa.nombre_comercial or empresa.razon_social,
        "rubro": empresa.rubro or "",
        "ciudad": empresa.ciudad or "",
    }
    if contacto is not None:
        vars_base.update(
            {
                "contacto": contacto.nombre,
                "cargo": contacto.cargo or "",
                "email": contacto.email or "",
                "whatsapp": contacto.whatsapp or "",
            }
        )
    return vars_base


def validar_frecuencia(
    db: Session,
    empresa_id: int,
    contacto_id: int | None,
    plantilla_id: int,
    canal: CanalComunicacion,
) -> str | None:
    """Devuelve un motivo de rechazo si se excede la frecuencia o hay duplicado."""
    ahora = datetime.now(timezone.utc)

    # Duplicado: misma plantilla + contacto/canal en las últimas 24 h
    if contacto_id is not None:
        reciente = db.scalar(
            select(func.count()).select_from(Comunicacion).where(
                Comunicacion.contacto_id == contacto_id,
                Comunicacion.plantilla_id == plantilla_id,
                Comunicacion.canal == canal,
                Comunicacion.created_at >= ahora - timedelta(hours=HORAS_ANTIDUPLICADO),
            )
        )
        if reciente:
            return f"Ya se envió esta plantilla a este contacto en las últimas {HORAS_ANTIDUPLICADO} h"

    # Frecuencia: máximo por empresa y día
    hoy = ahora.replace(hour=0, minute=0, second=0, microsecond=0)
    enviadas = db.scalar(
        select(func.count()).select_from(Comunicacion).where(
            Comunicacion.empresa_id == empresa_id,
            Comunicacion.canal == canal,
            Comunicacion.created_at >= hoy,
        )
    )
    if enviadas and enviadas >= MAX_POR_EMPRESA_DIA:
        return f"Límite diario alcanzado ({MAX_POR_EMPRESA_DIA} comunicaciones por empresa)"

    return None


def despachar_n8n(evento: str, payload: dict) -> bool:
    """Envía el evento al webhook de n8n (Gmail/WhatsApp). Devuelve True si
    n8n lo recibió. Si n8n no está configurado o falla, la comunicación queda
    registrada y puede reintentarse (n8n no contiene lógica crítica)."""
    if not settings.n8n_webhook_url:
        return False
    try:
        req = urllib.request.Request(
            settings.n8n_webhook_url,
            data=json.dumps({"evento": evento, **payload}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10):
            return True
    except (urllib.error.URLError, OSError):
        return False


def registrar_envio(
    db: Session,
    *,
    empresa: Empresa,
    contacto: Contacto | None,
    plantilla: Plantilla,
    canal: CanalComunicacion,
    contenido_renderizado: str,
    lead_id=None,
    agente: str = "panel",
) -> tuple[Comunicacion | None, str | None]:
    """Valida frecuencia/duplicados, registra la comunicacion y despacha a n8n.

    Devuelve (comunicacion, motivo_de_rechazo)."""
    motivo = validar_frecuencia(
        db, empresa.id, contacto.id if contacto else None, plantilla.id, canal
    )
    if motivo:
        return None, motivo

    # 1) Registrar primero para obtener el ID: n8n lo necesita para confirmar
    #    el estado de vuelta en /webhooks/estado-comunicacion (docs/14).
    comunicacion = Comunicacion(
        empresa_id=empresa.id,
        lead_id=lead_id,
        contacto_id=contacto.id if contacto else None,
        canal=canal,
        plantilla_id=plantilla.id,
        contenido=contenido_renderizado,
        estado=EstadoComunicacion.pendiente,
        agente=agente,
    )
    db.add(comunicacion)
    db.flush()  # obtiene comunicacion.id sin confirmar la transacción

    # 2) Despachar a n8n con el ID y el destinatario reales.
    exito = despachar_n8n(
        "comunicacion.enviar",
        {
            "comunicacion_id": str(comunicacion.id),
            "canal": canal.value,
            "empresa": empresa.razon_social,
            "contacto": contacto.nombre if contacto else None,
            "email": contacto.email if contacto else None,
            "whatsapp": contacto.whatsapp if contacto else None,
            "contenido": contenido_renderizado,
        },
    )
    comunicacion.estado = EstadoComunicacion.enviado if exito else EstadoComunicacion.pendiente
    return comunicacion, None
