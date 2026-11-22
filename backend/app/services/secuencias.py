"""Lógica de secuencias de seguimiento (Fase 2 — docs/10).

Las secuencias envían pasos escalonados a los contactos inscritos. FastAPI
posee la lógica crítica; n8n solo despacha el mensaje resultante.
"""
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.comunicaciones import Comunicacion, Plantilla
from app.models.common import CanalComunicacion, EstadoComunicacion
from app.models.crm import Contacto, Empresa
from app.models.secuencias import Secuencia, SecuenciaInscripcion, SecuenciaPaso
from app.services.comunicaciones import (
    despachar_n8n,
    renderizar,
    validar_frecuencia,
    variables_disponibles,
)


def ejecutar_paso(
    db: Session,
    inscripcion: SecuenciaInscripcion,
    ahora: datetime | None = None,
) -> str:
    """Ejecuta el paso pendiente de una inscripción. Devuelve el resultado:
    "enviado", "omitido", "completada" o "sin_pasos"."""
    ahora = ahora or datetime.now(timezone.utc)

    pasos = db.scalars(
        select(SecuenciaPaso)
        .where(SecuenciaPaso.secuencia_id == inscripcion.secuencia_id)
        .order_by(SecuenciaPaso.orden)
    ).all()

    if not pasos:
        inscripcion.estado = "completada"
        return "sin_pasos"

    if inscripcion.paso_actual >= len(pasos):
        inscripcion.estado = "completada"
        return "completada"

    paso = pasos[inscripcion.paso_actual]
    empresa = db.get(Empresa, inscripcion.empresa_id)
    contacto = db.get(Contacto, inscripcion.contacto_id) if inscripcion.contacto_id else None
    secuencia = db.get(Secuencia, inscripcion.secuencia_id)

    canal: CanalComunicacion = secuencia.canal if secuencia else CanalComunicacion.email

    # Contenido del paso: plantilla con variables o mensaje directo
    plantilla = db.get(Plantilla, paso.plantilla_id) if paso.plantilla_id else None
    if plantilla is not None:
        variables = variables_disponibles(empresa, contacto)
        contenido, _ = renderizar(plantilla.contenido, variables)
    else:
        contenido = paso.mensaje or ""

    # Control de frecuencia y duplicados (docs/10)
    if plantilla is not None:
        motivo = validar_frecuencia(
            db, empresa.id, contacto.id if contacto else None, plantilla.id, canal
        )
        if motivo:
            # Se reintenta en 24 h sin avanzar de paso
            inscripcion.proxima_ejecucion = ahora + timedelta(hours=24)
            return "omitido"

    exito = despachar_n8n(
        "comunicacion.enviar",
        {
            "canal": canal.value,
            "empresa": empresa.razon_social,
            "contacto": contacto.nombre if contacto else None,
            "email": contacto.email if contacto else None,
            "whatsapp": contacto.whatsapp if contacto else None,
            "contenido": contenido,
            "evento": f"secuencia:{secuencia.nombre if secuencia else ''}",
        },
    )

    db.add(
        Comunicacion(
            empresa_id=empresa.id,
            lead_id=inscripcion.lead_id,
            contacto_id=inscripcion.contacto_id,
            canal=canal,
            plantilla_id=paso.plantilla_id,
            contenido=contenido,
            estado=EstadoComunicacion.enviado if exito else EstadoComunicacion.pendiente,
            agente=f"secuencia:{secuencia.nombre if secuencia else ''}",
        )
    )

    inscripcion.ultimo_envio = ahora
    inscripcion.paso_actual += 1

    if inscripcion.paso_actual >= len(pasos):
        inscripcion.estado = "completada"
        return "completada"

    siguiente = pasos[inscripcion.paso_actual]
    inscripcion.proxima_ejecucion = ahora + timedelta(days=max(siguiente.dias_espera, 0))
    return "enviado"


def ejecutar_pendientes(db: Session) -> dict:
    """Ejecuta todos los pasos vencidos de las inscripciones activas."""
    ahora = datetime.now(timezone.utc)
    pendientes = db.scalars(
        select(SecuenciaInscripcion).where(
            SecuenciaInscripcion.estado == "activa",
            SecuenciaInscripcion.proxima_ejecucion <= ahora,
        )
    ).all()

    resultados = {"enviados": 0, "omitidos": 0, "completadas": 0, "sin_pasos": 0}
    for inscripcion in pendientes:
        resultado = ejecutar_paso(db, inscripcion, ahora)
        if resultado == "enviado":
            resultados["enviados"] += 1
        elif resultado == "omitido":
            resultados["omitidos"] += 1
        elif resultado == "completada":
            resultados["completadas"] += 1
        else:
            resultados["sin_pasos"] += 1

    db.commit()
    return resultados
