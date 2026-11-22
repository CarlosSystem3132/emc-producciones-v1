"""Chat flotante público (Fase 3 — docs/09).

- POST /public/chat: consultas de visitantes al asistente virtual.
- Sin autenticación; con límite simple de frecuencia por dirección IP.
- La IA es supervisada: no confirma ventas ni inventa información
  (ver app/services/chat_ia.py).
"""
import time

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.common import EstadoUsuario, RolUsuario, TipoNotificacion
from app.models.user import Usuario
from app.services import agentes
from app.services.chat_ia import responder_chat

router = APIRouter(prefix="/public", tags=["public-chat"])

# Palabras que indican interés comercial → notificar al administrador (docs/09)
PALABRAS_INTERES = (
    "reserv", "stand", "paquete", "precio", "cotiz", "expositor",
    "participar", "maquinaria", "cancha", "propuesta",
)

# Límite de frecuencia por IP: máx. 10 consultas por minuto
_LIMITE_CONSULTAS = 10
_VENTANA_SEGUNDOS = 60
_historial_peticiones: dict[str, list[float]] = {}


def _validar_frecuencia(ip: str) -> None:
    ahora = time.monotonic()
    tiempos = [t for t in _historial_peticiones.get(ip, []) if ahora - t < _VENTANA_SEGUNDOS]
    if len(tiempos) >= _LIMITE_CONSULTAS:
        _historial_peticiones[ip] = tiempos
        raise HTTPException(
            status_code=429,
            detail="Demasiadas consultas. Espera un minuto e inténtalo de nuevo.",
        )
    tiempos.append(ahora)
    _historial_peticiones[ip] = tiempos
    # Evita crecimiento del caché
    if len(_historial_peticiones) > 1000:
        _historial_peticiones.clear()


class MensajeChat(BaseModel):
    mensaje: str = Field(min_length=1, max_length=500)
    historial: list[dict] = Field(default_factory=list, max_length=10)


class RespuestaChat(BaseModel):
    respuesta: str
    origen: str  # "ia" | "faq"


@router.post("/chat", response_model=RespuestaChat)
def chat(
    payload: MensajeChat,
    request: Request,
    db: Session = Depends(get_db),
) -> RespuestaChat:
    """Responde una consulta del visitante con el asistente supervisado."""
    ip = request.client.host if request.client else "desconocida"
    _validar_frecuencia(ip)

    historial = [
        {"rol": str(item.get("rol", "")), "contenido": str(item.get("contenido", ""))}
        for item in payload.historial
        if isinstance(item, dict)
    ]
    respuesta, origen = responder_chat(
        payload.mensaje,
        historial,
        prompt_sistema=agentes.prompt_sistema(db, "atencion"),
        usar_ia=agentes.ia_habilitada(db, "atencion"),
    )

    # Agente 5 (docs/09): una consulta con interés comercial notifica al admin
    texto = payload.mensaje.lower()
    if any(p in texto for p in PALABRAS_INTERES):
        from app.services.notificaciones import notificar as _notificar_multicanal

        admins = db.scalars(
            select(Usuario).where(
                Usuario.rol == RolUsuario.admin,
                Usuario.estado == EstadoUsuario.activo,
                Usuario.deleted_at.is_(None),
            )
        ).all()
        for admin in admins:
            _notificar_multicanal(
                db,
                admin.id,
                TipoNotificacion.lead,
                "Nueva consulta desde el chat",
                payload.mensaje[:250],
            )
        db.commit()

    return RespuestaChat(respuesta=respuesta, origen=origen)
