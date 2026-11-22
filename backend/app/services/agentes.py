"""Configuración de agentes de IA: valores por defecto y acceso desde servicios.

Cada agente (docs/09) tiene en la tabla `config_agentes`:
- `prompt_sistema` editable desde el panel (Administración → Agentes IA).
- `modo_autonomia`: automatico | asistido | manual.
- `activo`: si el agente está habilitado.

Si falta la fila (BD nueva sin seed), se usan los valores por defecto de este
módulo: el sistema siempre funciona.
"""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.common import EstadoActivo
from app.models.config_agente import ConfigAgente

# ---------------------------------------------------------------------------
# Valores por defecto (también los usa el seed_config_agentes)
# ---------------------------------------------------------------------------

PROMPT_ATENCION = (
    "Eres el asistente virtual de EMC Producciones para la EXPOINCO 2027 "
    "(Expo Inmobiliaria y Construcción Internacional de El Alto, Bolivia). "
    "Tu rol es informar y orientar a posibles expositores. Reglas estrictas: "
    "1) Responde en español, breve y amable. "
    "2) Usa únicamente la información oficial de la base de conocimiento; "
    "nunca inventes fechas exactas, precios, descuentos ni condiciones. "
    "3) No confirmes ventas ni reservas; para eso un ejecutivo de ventas "
    "contactará al cliente. "
    "4) Si te preguntan por precios o disponibilidad específica, explica que "
    "un ejecutivo confirmará esa información y sugiere dejar sus datos por el "
    "formulario de reserva o WhatsApp. "
    "5) Si la consulta no está relacionada con la expo, responde cortésmente "
    "que solo atiendes consultas del evento."
)

DEFAULTS: list[dict] = [
    {
        "clave": "estrategia",
        "nombre": "Agente 1 — Estrategia",
        "descripcion": (
            "Analiza metas, inventario, rubros, avance comercial y desempeño. "
            "Propone plan semanal, segmentos prioritarios y campañas."
        ),
        "prompt_sistema": (
            "Eres el Agente de Estrategia comercial de EMC Producciones "
            "(EXPOINCO 2027). Analizas metas, inventario, rubros, avance "
            "comercial y desempeño de ejecutivos. Propones un plan semanal, "
            "segmentos prioritarios y campañas sugeridas. Trabajas con datos "
            "del sistema: nunca inventes cifras ni fechas. Nivel: asistido — "
            "tus propuestas son sugerencias que el administrador aprueba."
        ),
        "modo_autonomia": "asistido",
    },
    {
        "clave": "prospeccion",
        "nombre": "Agente 2 — Prospección",
        "descripcion": (
            "Clasifica leads, detecta duplicados y sugiere asignación de "
            "ejecutivo por afinidad de rubro y carga de trabajo."
        ),
        "prompt_sistema": (
            "Eres el Agente de Prospección de EMC Producciones. Clasificas "
            "leads por puntuación de interés, detectas duplicados y sugieres "
            "la asignación de ejecutivo según afinidad de rubro y menor "
            "carga de trabajo. Solo usas datos registrados en el sistema; "
            "nunca inventes información de empresas. Entregas listas y "
            "asignaciones para validación humana."
        ),
        "modo_autonomia": "asistido",
    },
    {
        "clave": "contenido",
        "nombre": "Agente 3 — Contenido comercial",
        "descripcion": (
            "Prepara invitaciones, propuestas personalizadas y resúmenes de "
            "conversaciones. Todo es borrador hasta su revisión."
        ),
        "prompt_sistema": (
            "Eres el Agente de Contenido Comercial de EMC Producciones. "
            "Redactas invitaciones, propuestas y resúmenes de seguimiento "
            "personalizados para cada empresa, con datos reales del sistema "
            "(empresa, contacto, stand, paquete, ejecutivo asignado). Todo lo "
            "que generas es un borrador que un humano revisa antes de enviar. "
            "No ofrezcas precios ni condiciones que no estén en los datos."
        ),
        "modo_autonomia": "asistido",
    },
    {
        "clave": "difusion",
        "nombre": "Agente 4 — Difusión",
        "descripcion": (
            "Organiza envíos controlados: campañas por segmento, secuencias "
            "de seguimiento, límites diarios y prevención de duplicados."
        ),
        "prompt_sistema": (
            "Eres el Agente de Difusión de EMC Producciones. Organizas envíos "
            "comerciales controlados: respetas el límite de frecuencia "
            "(máximo 5 comunicaciones por empresa al día), evitas duplicados "
            "(24 horas para la misma plantilla y contacto) y segmentas por "
            "estado o rubro. Las campañas masivas requieren aprobación del "
            "administrador."
        ),
        "modo_autonomia": "asistido",
    },
    {
        "clave": "atencion",
        "nombre": "Agente 5 — Atención y reservas",
        "descripcion": (
            "Responde el chat público, captura datos, clasifica interés, "
            "notifica al ejecutivo asignado y vigila reservas temporales."
        ),
        "prompt_sistema": PROMPT_ATENCION,
        "modo_autonomia": "automatico",
    },
]


def get_config(db: Session, clave: str) -> ConfigAgente | None:
    """Devuelve la configuración del agente o None si no existe la fila."""
    return db.scalar(select(ConfigAgente).where(ConfigAgente.clave == clave))


def modo_autonomia(db: Session, clave: str, por_defecto: str = "asistido") -> str:
    config = get_config(db, clave)
    return config.modo_autonomia if config is not None else por_defecto


def agente_activo(db: Session, clave: str) -> bool:
    config = get_config(db, clave)
    return config is None or config.activo == EstadoActivo.activo


def prompt_sistema(db: Session, clave: str, por_defecto: str = "") -> str:
    config = get_config(db, clave)
    return config.prompt_sistema if config is not None else por_defecto


def ia_habilitada(db: Session, clave: str) -> bool:
    """El agente puede usar el modelo de IA solo si está activo y no en modo
    manual (en manual solo actúa cuando un humano lo solicita)."""
    config = get_config(db, clave)
    if config is None:
        return True
    return config.activo == EstadoActivo.activo and config.modo_autonomia != "manual"


def seed_config_agentes() -> None:
    """Crea las filas por defecto si la tabla está vacía (al arrancar)."""
    from app.db.session import SessionLocal

    db = SessionLocal()
    try:
        if db.scalar(select(ConfigAgente).limit(1)) is not None:
            return
        for datos in DEFAULTS:
            db.add(ConfigAgente(**datos))
        db.commit()
        print("Configuración por defecto de agentes de IA creada.")
    finally:
        db.close()
