"""Notificaciones al equipo comercial (docs/08).

Cada notificación se registra en el panel **y** se despacha por los canales de
contacto que el usuario registró (WhatsApp y correo). El despacho externo lo
realiza n8n (Gmail / WhatsApp Cloud API): la lógica crítica vive en FastAPI.

El número de WhatsApp que el administrador registra al crear el ejecutivo es
el que se usa para notificarle (docs/07 y docs/08).
"""
import uuid

from sqlalchemy.orm import Session

from app.models.common import TipoNotificacion
from app.models.comunicaciones import Notificacion
from app.models.user import Usuario
from app.services.comunicaciones import despachar_n8n


def notificar(
    db: Session,
    usuario_id: uuid.UUID,
    tipo: TipoNotificacion,
    titulo: str,
    mensaje: str,
    referencia_id: uuid.UUID | None = None,
) -> Notificacion | None:
    """Registra la notificación en el panel y la envía por WhatsApp y correo
    si el usuario tiene esos datos de contacto registrados.

    El envío externo es asíncrono vía n8n: si n8n no está configurado, la
    notificación queda igualmente registrada en el panel."""
    usuario = db.get(Usuario, usuario_id)
    if usuario is None:
        return None

    notificacion = Notificacion(
        usuario_id=usuario_id,
        tipo=tipo,
        titulo=titulo,
        mensaje=mensaje,
        canal="panel",
        referencia_id=referencia_id,
    )
    db.add(notificacion)

    texto = f"📢 {titulo}\n{mensaje}\n— EMC Producciones · EXPOINCO 2027"

    # WhatsApp: usa el número que el admin registró al crear al ejecutivo
    if usuario.whatsapp:
        despachar_n8n(
            "notificacion.enviar",
            {
                "canal": "whatsapp",
                "para": usuario.whatsapp,
                "nombre": usuario.nombre_completo,
                "mensaje": texto,
            },
        )

    # Correo de contacto (o el correo de acceso como respaldo)
    correo = usuario.correo_contacto or usuario.email
    if correo:
        despachar_n8n(
            "notificacion.enviar",
            {
                "canal": "email",
                "para": correo,
                "nombre": usuario.nombre_completo,
                "mensaje": texto,
            },
        )

    return notificacion
