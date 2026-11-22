"""Servicios de inteligencia comercial supervisada (Fase 3 — docs/09).

Todos los módulos son asistentes supervisados: proponen, no deciden.
La IA (DeepSeek) se usa solo para redactar resúmenes y borradores cuando está
configurada; la clasificación, asignación y las sugerencias funcionan con
reglas determinísticas para que el sistema nunca dependa de la API externa.
"""
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.common import (
    EstadoLead,
    PrioridadLead,
    RolUsuario,
)
from app.models.comunicaciones import Actividad, Comunicacion
from app.models.crm import Contacto, Empresa, Lead
from app.models.reserva import Reserva
from app.models.user import Usuario

# ---------------------------------------------------------------------------
# 0. Agente de estrategia: análisis y plan semanal sugerido
# ---------------------------------------------------------------------------


def analisis_estrategico(db: Session, usuario: Usuario) -> dict:
    """Agente 1 (docs/09): analiza metas, inventario, rubros, avance y
    desempeño; propone plan semanal, segmentos prioritarios y campañas.
    Todo es sugerencia: el administrador aprueba el plan."""
    from app.models.inventario import Stand, Zona

    ahora = datetime.now(timezone.utc)
    desde_semana = ahora - timedelta(days=7)

    # ---- Inventario ----
    conteo = dict(
        db.execute(select(Stand.estado, func.count()).group_by(Stand.estado)).all()
    )
    total_stands = sum(conteo.values())
    ocupados = conteo.get("vendido", 0) + conteo.get("reservado", 0)
    zonas_criticas = []
    for zona in db.scalars(select(Zona)).all():
        total_z = db.scalar(
            select(func.count()).select_from(Stand).where(Stand.zona_id == zona.id)
        ) or 0
        disp_z = db.scalar(
            select(func.count()).select_from(Stand).where(
                Stand.zona_id == zona.id, Stand.estado == "disponible"
            )
        ) or 0
        if total_z and disp_z / total_z <= 0.2:
            zonas_criticas.append({"zona": zona.nombre, "disponibles": disp_z, "total": total_z})

    # ---- Avance semanal ----
    leads_semana = db.scalar(
        select(func.count()).select_from(Lead).where(Lead.created_at >= desde_semana)
    ) or 0
    empresas_semana = db.scalar(
        select(func.count()).select_from(Empresa).where(Empresa.created_at >= desde_semana)
    ) or 0
    reservas_semana = db.scalar(
        select(func.count()).select_from(Reserva).where(Reserva.created_at >= desde_semana)
    ) or 0

    # ---- Rubros con menor cobertura ----
    por_rubro = dict(
        db.execute(
            select(Empresa.rubro, func.count())
            .where(Empresa.deleted_at.is_(None))
            .group_by(Empresa.rubro)
        ).all()
    )
    rubros_debiles = sorted(
        ((r or "sin rubro", n) for r, n in por_rubro.items()), key=lambda x: x[1]
    )[:5]

    # ---- Desempeño por ejecutivo ----
    desempeno = []
    for ejec in db.scalars(
        select(Usuario).where(
            Usuario.rol == RolUsuario.ejecutivo,
            Usuario.deleted_at.is_(None),
        )
    ).all():
        abiertos = db.scalar(
            select(func.count()).select_from(Lead).where(
                Lead.ejecutivo_id == ejec.id,
                Lead.estado.notin_([EstadoLead.vendido, EstadoLead.descartado]),
            )
        ) or 0
        ventas = db.scalar(
            select(func.count()).select_from(Reserva).where(
                Reserva.ejecutivo_id == ejec.id, Reserva.estado == "vendido"
            )
        ) or 0
        desempeno.append({
            "ejecutivo": ejec.nombre_completo,
            "leads_abiertos": abiertos,
            "ventas": ventas,
            "estado": ejec.estado.value,
        })

    # ---- Plan semanal sugerido (reglas sobre los datos) ----
    plan = []
    sin_actividad = db.scalar(
        select(func.count()).select_from(Lead).where(
            Lead.deleted_at.is_(None),
            Lead.estado.notin_([EstadoLead.vendido, EstadoLead.descartado]),
            Lead.id.notin_(select(Comunicacion.lead_id).where(Comunicacion.created_at >= desde_semana)),
        )
    ) or 0
    if sin_actividad:
        plan.append(f"Reactivar {sin_actividad} lead(s) sin interacción esta semana (secuencia de seguimiento).")
    reserva_temporal = db.scalar(
        select(func.count()).select_from(Lead).where(Lead.estado == EstadoLead.reserva_temporal)
    ) or 0
    if reserva_temporal:
        plan.append(f"Cerrar {reserva_temporal} reserva(s) temporales antes de su expiración.")
    if rubros_debiles:
        plan.append(
            "Campaña de prospección a rubros con menor cobertura: "
            + ", ".join(r for r, _ in rubros_debiles[:3])
            + "."
        )
    if zonas_criticas:
        plan.append(
            "Priorizar venta de zonas casi agotadas: "
            + ", ".join(z["zona"] for z in zonas_criticas[:3])
            + "."
        )
    if reservas_semana == 0:
        plan.append("Semana sin reservas: intensificar contacto directo y rondas de negocios.")

    # ---- Segmentos prioritarios y campañas sugeridas ----
    segmentos = [
        {"segmento": f"rubro:{r}", "empresas": n, "prioridad": "alta" if n <= 2 else "media"}
        for r, n in rubros_debiles[:3]
    ]
    campanas = [
        {
            "nombre": f"Prospección {r}",
            "segmento": f"rubro:{r}",
            "plantilla_sugerida": "invitacion",
            "canal": "email",
        }
        for r, _ in rubros_debiles[:3]
    ]

    return {
        "inventario": {
            "total_stands": total_stands,
            "ocupados": ocupados,
            "porcentaje_ocupacion": round(100 * ocupados / total_stands, 1) if total_stands else 0.0,
            "zonas_casi_agotadas": zonas_criticas,
        },
        "avance_semanal": {
            "leads": leads_semana,
            "empresas": empresas_semana,
            "reservas": reservas_semana,
        },
        "rubros_con_menor_cobertura": [
            {"rubro": r, "empresas": n} for r, n in rubros_debiles
        ],
        "desempeno_ejecutivos": desempeno,
        "plan_semanal_sugerido": plan,
        "segmentos_prioritarios": segmentos,
        "campanas_sugeridas": campanas,
        "autonomia": "asistido — el administrador aprueba el plan (docs/09)",
    }


# ---------------------------------------------------------------------------
# 1. Clasificación automática de leads
# ---------------------------------------------------------------------------


def clasificar_lead(db: Session, lead: Lead) -> dict:
    """Analiza la actividad del lead y propone estado y prioridad.

    Reglas (puntuación):
    - +2 si el interés menciona stand/paquete concreto.
    - +1 por cada comunicación o actividad en los últimos 30 días (máx. +3).
    - +2 si tiene una reserva activa (bloqueado/reservado).
    - +1 si el contacto tiene email o WhatsApp válido.
    - +1 si ya se envió propuesta (estado >= propuesta_enviada).
    """
    score = 0
    motivos: list[str] = []

    interes = (lead.interes or "").lower()
    if any(p in interes for p in ("stand", "paquete", "cancha", "esquina", "premium")):
        score += 2
        motivos.append("interés concreto en un espacio")

    desde = datetime.now(timezone.utc) - timedelta(days=30)
    coms = db.scalar(
        select(func.count()).select_from(Comunicacion).where(
            Comunicacion.lead_id == lead.id, Comunicacion.created_at >= desde
        )
    ) or 0
    acts = db.scalar(
        select(func.count()).select_from(Actividad).where(
            Actividad.lead_id == lead.id, Actividad.created_at >= desde
        )
    ) or 0
    recientes = min(coms + acts, 3)
    if recientes:
        score += recientes
        motivos.append(f"{coms + acts} interacción(es) en los últimos 30 días")

    reserva_activa = db.scalar(
        select(func.count()).select_from(Reserva).where(
            Reserva.lead_id == lead.id,
            Reserva.estado.in_(["bloqueado", "reservado"]),
        )
    )
    if reserva_activa:
        score += 2
        motivos.append("tiene una reserva activa")

    if lead.contacto_id is not None:
        contacto = db.get(Contacto, lead.contacto_id)
        if contacto is not None and (contacto.email or contacto.whatsapp):
            score += 1
            motivos.append("contacto con canal directo (email/WhatsApp)")

    orden_estados = [
        EstadoLead.prospecto,
        EstadoLead.contactado,
        EstadoLead.interesado,
        EstadoLead.propuesta_enviada,
        EstadoLead.en_negociacion,
    ]
    if lead.estado in (EstadoLead.propuesta_enviada, EstadoLead.en_negociacion):
        score += 1
        motivos.append("ya recibió propuesta")

    if score >= 6:
        estado_sugerido = EstadoLead.en_negociacion
    elif score >= 4:
        estado_sugerido = EstadoLead.propuesta_enviada
    elif score >= 2:
        estado_sugerido = EstadoLead.interesado
    elif score >= 1:
        estado_sugerido = EstadoLead.contactado
    else:
        estado_sugerido = EstadoLead.prospecto

    # Nunca retrocede el embudo automáticamente
    if orden_estados.index(estado_sugerido) < orden_estados.index(
        lead.estado if lead.estado in orden_estados else EstadoLead.prospecto
    ):
        estado_sugerido = lead.estado

    if score >= 5:
        prioridad_sugerida = PrioridadLead.alta
    elif score >= 3:
        prioridad_sugerida = PrioridadLead.media
    else:
        prioridad_sugerida = PrioridadLead.baja

    return {
        "puntuacion": score,
        "estado_actual": lead.estado.value,
        "estado_sugerido": estado_sugerido.value,
        "prioridad_sugerida": prioridad_sugerida.value,
        "motivos": motivos,
        "apto_para_venta": score >= 5,
    }


# ---------------------------------------------------------------------------
# 2. Asignación automática o sugerida de ejecutivos
# ---------------------------------------------------------------------------


def sugerir_ejecutivo(db: Session, empresa: Empresa) -> dict | None:
    """Sugiere el ejecutivo con menor carga y mejor afinidad de rubro.

    Criterios:
    1) Preferir ejecutivos cuya especialidad coincida con el rubro de la empresa.
    2) Entre ellos (o entre todos si no hay coincidencia), el de menor carga
       de empresas activas asignadas.
    """
    ejecutivos = db.scalars(
        select(Usuario).where(
            Usuario.rol == RolUsuario.ejecutivo,
            Usuario.estado == "activo",
            Usuario.deleted_at.is_(None),
        )
    ).all()
    if not ejecutivos:
        return None

    cargas = dict(
        db.execute(
            select(Empresa.ejecutivo_id, func.count())
            .where(Empresa.deleted_at.is_(None))
            .group_by(Empresa.ejecutivo_id)
        ).all()
    )

    rubro = (empresa.rubro or "").lower()

    def afinidad(u: Usuario) -> bool:
        if not rubro or not u.especialidad:
            return False
        return any(p and p in u.especialidad.lower() for p in rubro.split())

    candidatos = [u for u in ejecutivos if afinidad(u)] or ejecutivos
    elegido = min(candidatos, key=lambda u: cargas.get(u.id, 0))

    return {
        "ejecutivo_id": str(elegido.id),
        "nombre": elegido.nombre_completo,
        "especialidad": elegido.especialidad,
        "empresas_asignadas": cargas.get(elegido.id, 0),
        "por_afinidad": afinidad(elegido),
    }


# ---------------------------------------------------------------------------
# 3. Resúmenes de conversaciones
# ---------------------------------------------------------------------------


def resumen_conversaciones(db: Session, empresa: Empresa) -> dict:
    """Resume el historial comercial de una empresa (extractivo + IA opcional)."""
    coms = db.scalars(
        select(Comunicacion)
        .where(Comunicacion.empresa_id == empresa.id)
        .order_by(Comunicacion.created_at.desc())
        .limit(20)
    ).all()
    acts = db.scalars(
        select(Actividad)
        .where(Actividad.empresa_id == empresa.id)
        .order_by(Actividad.created_at.desc())
        .limit(20)
    ).all()

    por_canal: dict[str, int] = {}
    for c in coms:
        por_canal[c.canal.value] = por_canal.get(c.canal.value, 0) + 1

    ultimo_evento = max(
        [c.created_at for c in coms] + [a.created_at for a in acts],
        default=None,
    )

    lineas = []
    for c in coms[:5]:
        texto = (c.contenido or "")[:140]
        lineas.append(f"[{c.canal.value}/{c.estado.value}] {texto}")
    for a in acts[:5]:
        lineas.append(f"[{a.tipo.value}] {(a.descripcion or '')[:140]}")

    resumen_local = (
        f"{empresa.razon_social}: {len(coms)} comunicación(es) "
        f"({', '.join(f'{k}: {v}' for k, v in por_canal.items()) or 'sin canales'}), "
        f"{len(acts)} actividad(es) registrada(s). "
        f"Último evento: {ultimo_evento.strftime('%d/%m/%Y') if ultimo_evento else 'sin registro'}."
    )

    # IA opcional para un resumen narrativo (supervisado, nunca inventa datos).
    # Respeta la configuración del Agente 3 (contenido): si está desactivado o
    # en modo manual, se usa solo el resumen local.
    from app.services.chat_ia import texto_ia  # importación local para evitar ciclos
    from app.services import agentes as _agentes

    contexto = "\n".join(lineas)
    resumen_ia = None
    if _agentes.ia_habilitada(db, "contenido"):
        resumen_ia = texto_ia(
            f"Resume en máximo 3 líneas el seguimiento comercial de esta empresa, "
            f"solo con los datos proporcionados:\n{contexto}",
            sistema=_agentes.prompt_sistema(db, "contenido"),
        )

    return {
        "empresa": empresa.razon_social,
        "resumen": resumen_ia or resumen_local,
        "origen": "ia" if resumen_ia else "local",
        "comunicaciones": len(coms),
        "actividades": len(acts),
        "por_canal": por_canal,
        "ultimo_evento": ultimo_evento.isoformat() if ultimo_evento else None,
    }


# ---------------------------------------------------------------------------
# 4. Sugerencias de siguiente acción
# ---------------------------------------------------------------------------


def sugerir_siguiente_accion(db: Session, lead: Lead) -> list[dict]:
    """Propone acciones concretas según el estado y la actividad del lead."""
    sugerencias: list[dict] = []
    desde = datetime.now(timezone.utc) - timedelta(days=7)
    coms_7d = db.scalar(
        select(func.count()).select_from(Comunicacion).where(
            Comunicacion.lead_id == lead.id, Comunicacion.created_at >= desde
        )
    ) or 0

    if lead.estado == EstadoLead.prospecto:
        sugerencias.append({
            "accion": "Contactar por primera vez",
            "detalle": "Enviar la plantilla de invitación por email o WhatsApp y registrar la actividad.",
            "prioridad": "alta",
        })
    if lead.estado == EstadoLead.contactado and coms_7d == 0:
        sugerencias.append({
            "accion": "Re-contactar",
            "detalle": "Sin interacciones en 7 días: reenviar información de stands/paquetes.",
            "prioridad": "alta",
        })
    if lead.estado == EstadoLead.interesado:
        sugerencias.append({
            "accion": "Enviar propuesta",
            "detalle": "Generar la propuesta PDF con el paquete de interés y dar seguimiento en 48 h.",
            "prioridad": "alta",
        })
    if lead.estado == EstadoLead.propuesta_enviada:
        sugerencias.append({
            "accion": "Dar seguimiento a la propuesta",
            "detalle": "Confirmar recepción y agendar una llamada de cierre.",
            "prioridad": "media",
        })
    if lead.estado == EstadoLead.en_negociacion:
        sugerencias.append({
            "accion": "Cerrar la reserva",
            "detalle": "Reservar el stand elegido y coordinar el primer pago.",
            "prioridad": "alta",
        })
    if lead.estado == EstadoLead.reserva_temporal:
        sugerencias.append({
            "accion": "Confirmar antes de la expiración",
            "detalle": "El bloqueo temporal vence pronto: confirmar la reserva o extenderla.",
            "prioridad": "alta",
        })

    if lead.fecha_proxima_accion is not None and lead.fecha_proxima_accion < datetime.now(timezone.utc):
        sugerencias.append({
            "accion": "Cumplir la próxima acción vencida",
            "detalle": f"Compromiso registrado para {lead.fecha_proxima_accion.strftime('%d/%m/%Y')}: {lead.proxima_accion or 'seguimiento'}.",
            "prioridad": "alta",
        })

    if not sugerencias:
        sugerencias.append({
            "accion": "Mantener el contacto",
            "detalle": "Programar un seguimiento periódico y actualizar la información del lead.",
            "prioridad": "baja",
        })
    return sugerencias


# ---------------------------------------------------------------------------
# 5. Prospección asistida
# ---------------------------------------------------------------------------


def prospeccion_asistida(db: Session, usuario: Usuario) -> dict:
    """Analiza la cartera y propone dónde enfocar la prospección.

    - Rubros con menor cobertura de empresas.
    - Zonas con mayor disponibilidad de stands.
    - Empresas dormidas (sin actividad reciente) para reactivar.
    - Borrador de mensaje de prospección (IA opcional, plantilla local si no).
    """
    por_rubro = dict(
        db.execute(
            select(Empresa.rubro, func.count())
            .where(Empresa.deleted_at.is_(None))
            .group_by(Empresa.rubro)
        ).all()
    )
    rubros_ordenados = sorted(
        ((r or "sin rubro", n) for r, n in por_rubro.items()),
        key=lambda x: x[1],
    )[:5]

    # Zonas con mayor disponibilidad
    from app.models.inventario import Stand

    zonas_disp = db.execute(
        select(Stand.zona_id, func.count())
        .where(Stand.estado == "disponible")
        .group_by(Stand.zona_id)
        .order_by(func.count().desc())
        .limit(5)
    ).all()

    # Empresas dormidas: sin comunicación ni actividad en 21 días
    desde = datetime.now(timezone.utc) - timedelta(days=21)
    con_actividad = {
        r[0]
        for r in db.execute(
            select(Comunicacion.empresa_id).where(Comunicacion.created_at >= desde)
        ).all()
    } | {
        r[0]
        for r in db.execute(
            select(Actividad.empresa_id).where(Actividad.created_at >= desde)
        ).all()
    }
    dormidas = db.scalars(
        select(Empresa)
        .where(Empresa.deleted_at.is_(None), Empresa.estado.in_(["prospecto", "contactado"]))
        .limit(50)
    ).all()
    dormidas = [e for e in dormidas if e.id not in con_actividad][:10]

    borrador = (
        "Asunto: Invitación a la EXPOINCO 2027\n\n"
        "Estimado/a {{contacto}}:\n\n"
        "En nombre de EMC Producciones, queremos invitar a {{empresa}} a "
        "participar en la 1ra Expo Inmobiliaria y Construcción Internacional "
        "de El Alto (abril 2027). Contamos con stands interiores y canchas "
        "para maquinaria pesada, y nos gustaría preparar una propuesta "
        "ajustada a su rubro.\n\n"
        "¿Podemos coordinar una llamada esta semana?\n\n"
        "Saludos cordiales,\nEquipo comercial EMC Producciones"
    )

    return {
        "rubros_con_menor_cobertura": [{"rubro": r, "empresas": n} for r, n in rubros_ordenados],
        "zonas_con_mayor_disponibilidad": [
            {"zona_id": str(z), "stands_disponibles": n} for z, n in zonas_disp
        ],
        "empresas_reactivar": [
            {"id": str(e.id), "razon_social": e.razon_social, "rubro": e.rubro}
            for e in dormidas
        ],
        "borrador_mensaje": borrador,
        "origen_borrador": "plantilla",
    }


# ---------------------------------------------------------------------------
# 6. Alertas inteligentes
# ---------------------------------------------------------------------------


def alertas_inteligentes(db: Session, usuario: Usuario) -> list[dict]:
    """Alertas accionables según el rol del usuario."""
    alertas: list[dict] = []
    es_admin = usuario.is_admin
    desde = datetime.now(timezone.utc) - timedelta(days=7)

    # Leads sin interacción en 7 días (abiertos)
    abiertos = select(Lead.id).where(
        Lead.deleted_at.is_(None),
        Lead.estado.in_(["prospecto", "contactado", "interesado", "propuesta_enviada", "en_negociacion"]),
    )
    if not es_admin:
        abiertos = abiertos.where(Lead.ejecutivo_id == usuario.id)
    sin_actividad = db.scalar(
        select(func.count()).select_from(Lead).where(
            Lead.id.in_(abiertos),
            Lead.id.notin_(select(Comunicacion.lead_id).where(Comunicacion.created_at >= desde)),
            Lead.id.notin_(select(Actividad.lead_id).where(Actividad.created_at >= desde)),
        )
    ) or 0
    if sin_actividad:
        alertas.append({
            "tipo": "seguimiento",
            "mensaje": f"{sin_actividad} lead(s) abiertos sin interacción en los últimos 7 días.",
        })

    # Reservas bloqueadas por expirar (próximos 30 minutos)
    ahora = datetime.now(timezone.utc)
    expira_q = select(func.count()).select_from(Reserva).where(
        Reserva.estado == "bloqueado",
        Reserva.fecha_expiracion != None,  # noqa: E711
        Reserva.fecha_expiracion > ahora,
        Reserva.fecha_expiracion <= ahora + timedelta(minutes=30),
    )
    if not es_admin:
        expira_q = expira_q.where(Reserva.ejecutivo_id == usuario.id)
    por_expirar = db.scalar(expira_q) or 0
    if por_expirar:
        alertas.append({
            "tipo": "reserva",
            "mensaje": f"{por_expirar} reserva(s) con bloqueo temporal por expirar en menos de 30 minutos.",
        })

    # Leads en reserva temporal sin confirmar
    reserva_temp_q = select(func.count()).select_from(Lead).where(
        Lead.deleted_at.is_(None), Lead.estado == "reserva_temporal"
    )
    if not es_admin:
        reserva_temp_q = reserva_temp_q.where(Lead.ejecutivo_id == usuario.id)
    en_temporal = db.scalar(reserva_temp_q) or 0
    if en_temporal:
        alertas.append({
            "tipo": "reserva",
            "mensaje": f"{en_temporal} lead(s) en reserva temporal esperando confirmación.",
        })

    if es_admin:
        # Empresas sin ejecutivo asignado
        sin_ejecutivo = db.scalar(
            select(func.count()).select_from(Empresa).where(
                Empresa.deleted_at.is_(None), Empresa.ejecutivo_id.is_(None)
            )
        ) or 0
        if sin_ejecutivo:
            alertas.append({
                "tipo": "asignacion",
                "mensaje": f"{sin_ejecutivo} empresa(s) sin ejecutivo asignado. Usa la asignación sugerida.",
            })

        # Ocupación alta por zona (>80%)
        from app.models.inventario import Zona

        zonas = db.scalars(select(Zona)).all()
        for zona in zonas:
            total = db.scalar(
                select(func.count()).select_from(Stand).where(Stand.zona_id == zona.id)
            ) or 0
            ocupados = db.scalar(
                select(func.count()).select_from(Stand).where(
                    Stand.zona_id == zona.id, Stand.estado.in_(["reservado", "vendido"])
                )
            ) or 0
            if total and ocupados / total >= 0.8:
                alertas.append({
                    "tipo": "inventario",
                    "mensaje": f"Zona «{zona.nombre}» al {round(100 * ocupados / total)}% de ocupación.",
                })

    return alertas
