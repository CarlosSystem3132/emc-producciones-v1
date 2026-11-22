"""Chat flotante con IA supervisada (Fase 3 — docs/09).

Principios (docs/09 — Agentes de inteligencia artificial):
- La IA es un asistente comercial supervisado.
- Puede informar sobre el evento, stands, paquetes y proceso de reserva.
- No puede confirmar ventas, definir precios ni inventar información.
- Siempre sugiere derivar la conversación con un ejecutivo de ventas.

Funcionamiento:
- El router de IA (services/ia_router.py) prueba Gemini → Groq → OpenRouter →
  DeepSeek con failover automático por cuotas agotadas.
- Si ningún proveedor responde (sin claves o todos agotados), responde con la
  base de conocimiento local por palabras clave. El chat nunca queda roto.
"""
# (las llamadas a proveedores las realiza services/ia_router.py)

# ---------------------------------------------------------------------------
# Base de conocimiento aprobada (solo información verificada del evento)
# ---------------------------------------------------------------------------

BASE_CONOCIMIENTO = """
EXPOINCO 2027 — Expo Inmobiliaria y Construcción Internacional de El Alto.

Datos oficiales:
- Evento: 1ra Expoinmobiliaria y Construcción Internacional en El Alto, Bolivia.
- Organiza: EMC Producciones.
- Fecha prevista: abril de 2027, en El Alto, Bolivia.
- Espacios: 52 stands interiores en 6 zonas del pabellón y canchas exteriores
  para maquinaria pesada.
- Participan más de 150 empresas nacionales e internacionales de los rubros:
  urbanizaciones y condominios, inmobiliaria y proyectos, diseño, estructuras
  y construcción, maquinaria pesada y equipos, materiales y obra fina,
  domótica y seguridad.

Proceso de reserva de stands:
1. El cliente elige su stand en el plano interactivo de la web.
2. Solicita la reserva con el formulario (empresa, contacto y stand elegido).
3. El stand queda bloqueado temporalmente (30 minutos) mientras un ejecutivo
   de ventas lo contacta.
4. El ejecutivo confirma la reserva, envía la propuesta y coordina el pago.
5. Al confirmar la venta, el stand pasa a vendido y no vuelve a estar disponible.

Tipos de espacio:
- Stands interiores: estándar, premium y esquina, distribuidos en 6 zonas.
- Canchas de maquinaria: espacios exteriores para maquinaria pesada y equipos.

Políticas:
- Los precios y condiciones comerciales los define y confirma un ejecutivo de
  ventas; el asistente no cotiza ni confirma ventas.
- No se comparten datos de otros expositores.
"""

SYSTEM_PROMPT = (
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
    "que solo atiendes consultas del evento.\n\n"
    f"BASE DE CONOCIMIENTO OFICIAL:\n{BASE_CONOCIMIENTO}"
)

# Respuestas locales por palabras clave (fallback sin IA / sin red)
FAQ: list[tuple[list[str], str]] = [
    (
        ["precio", "costo", "cotiz", "cuánto", "cuanto", "valor"],
        "Los valores de los stands y paquetes los define un ejecutivo de ventas "
        "según el tipo de espacio y las condiciones de cada empresa. Puedes "
        "dejar tus datos en el formulario de reserva o por WhatsApp y un "
        "ejecutivo te enviará la propuesta personalizada. 📄",
    ),
    (
        ["reserv", "bloque", "apartar", "apartir"],
        "Para reservar un stand: elige tu stand en el plano interactivo, "
        "solicita la reserva con el formulario y el stand queda bloqueado 30 "
        "minutos mientras un ejecutivo te contacta para confirmar. 🗺️",
    ),
    (
        ["cuándo", "cuando", "fecha", "día", "dia", "horario"],
        "La EXPOINCO 2027 está prevista para abril de 2027 en El Alto, "
        "Bolivia. Las fechas y horarios definitivos se anunciarán en esta "
        "web. 📅",
    ),
    (
        ["dónde", "donde", "lugar", "ubicación", "ubicacion", "alto"],
        "El evento se realizará en El Alto, Bolivia, organizado por EMC "
        "Producciones. 📍",
    ),
    (
        ["stand", "espacio", "pabellón", "pabellon", "zona"],
        "Contamos con 52 stands interiores distribuidos en 6 zonas del "
        "pabellón (estándar, premium y esquina) y canchas exteriores para "
        "maquinaria pesada. Puedes ver la disponibilidad en el plano "
        "interactivo de esta web. 🗺️",
    ),
    (
        ["maquinaria", "cancha", "pesada", "equipo"],
        "Tenemos canchas exteriores especiales para maquinaria pesada y "
        "equipos. Un ejecutivo te ayudará a elegir la ubicación según el "
        "tamaño de tu equipo. 🏗️",
    ),
    (
        ["paquete", "beneficio", "inclu"],
        "Tenemos paquetes de participación con distintos beneficios para "
        "expositores. Un ejecutivo te enviará el detalle completo según tu "
        "rubro y el espacio que necesitas. 📦",
    ),
    (
        ["contacto", "hablar", "ejecutivo", "asesor", "whatsapp", "correo", "email"],
        "Puedes dejar tus datos en el formulario de reserva, escribirnos por "
        "WhatsApp o indicarme tu empresa y contacto y un ejecutivo de ventas "
        "te atenderá personalmente. 💬",
    ),
    (
        ["registro", "inscri", "expositor", "participar", "particip"],
        "¡Genial que quieras participar! Registra tu empresa en el formulario "
        "de esta web o escríbenos por WhatsApp. Un ejecutivo te acompañará en "
        "todo el proceso. 🎉",
    ),
]

SALUDO = (
    "¡Hola! 👋 Soy el asistente virtual de EXPOINCO 2027. Puedo informarte "
    "sobre stands, paquetes, maquinaria pesada y el proceso de reserva. "
    "¿En qué te ayudo?"
)

SIN_RESPUESTA = (
    "No tengo información oficial sobre eso. Para darte una respuesta precisa, "
    "te sugiero dejar tus datos en el formulario de reserva o escribir por "
    "WhatsApp: un ejecutivo de ventas te atenderá. ¿Tienes alguna consulta "
    "sobre stands, paquetes o la expo? 🤝"
)


def _faq_local(mensaje: str) -> str:
    texto = mensaje.lower()
    for palabras, respuesta in FAQ:
        if any(p in texto for p in palabras):
            return respuesta
    return SIN_RESPUESTA


def _deepseek(
    mensaje: str,
    historial: list[dict],
    prompt_sistema: str | None = None,
) -> str | None:
    """Consulta el router de IA con el prompt del sistema configurado.
    Devuelve None si no hay proveedores disponibles (fallback FAQ local).
    (El nombre se conserva por compatibilidad con versiones previas.)"""
    from app.services import ia_router

    mensajes = [{"role": "system", "content": prompt_sistema or SYSTEM_PROMPT}]
    for item in historial[-8:]:
        rol = "assistant" if item.get("rol") == "asistente" else "user"
        mensajes.append({"role": rol, "content": str(item.get("contenido", ""))[:1000]})
    mensajes.append({"role": "user", "content": mensaje})

    resultado = ia_router.generar(mensajes, max_tokens=500, temperature=0.3)
    return resultado[0] if resultado else None


def texto_ia(prompt: str, sistema: str | None = None) -> str | None:
    """Genera un texto puntual con el router de IA (para resúmenes internos).
    `sistema` permite usar el prompt configurado del agente correspondiente.
    Devuelve None si ningún proveedor está disponible."""
    from app.services import ia_router

    mensajes = [
        {
            "role": "system",
            "content": sistema or (
                "Eres un asistente interno de análisis comercial de EMC "
                "Producciones. Respondes en español, de forma concisa, "
                "usando únicamente los datos proporcionados. Nunca inventes "
                "información."
            ),
        },
        {"role": "user", "content": prompt},
    ]
    resultado = ia_router.generar(mensajes, max_tokens=300, temperature=0.2)
    return resultado[0] if resultado else None


def responder_chat(
    mensaje: str,
    historial: list[dict] | None = None,
    prompt_sistema: str | None = None,
    usar_ia: bool = True,
) -> tuple[str, str]:
    """Genera la respuesta del chat. Devuelve (respuesta, origen).

    origen es "ia" cuando responde el modelo y "faq" cuando responde la base
    de conocimiento local. Con `usar_ia=False` (agente desactivado o en modo
    manual) responde solo con la FAQ local."""
    mensaje = mensaje.strip()
    if not mensaje:
        return SALUDO, "faq"

    ia = _deepseek(mensaje, historial or [], prompt_sistema) if usar_ia else None
    if ia:
        return ia, "ia"
    return _faq_local(mensaje), "faq"
