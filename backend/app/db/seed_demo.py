"""Datos de prueba para el sistema comercial EMC Producciones.

Crea una base de demostración completa para probar todos los módulos:
ejecutivos, empresas reales del sector (Bolivia), contactos, leads,
plantillas, secuencias de seguimiento, patrocinadores y un flujo de
reserva → pago → factura de ejemplo.

Uso:

    python -m app.db.seed_demo          # crea los datos (omite si ya existen)
    python -m app.db.seed_demo --force  # vuelve a crear (borra demo previa)

Requiere haber ejecutado antes:  alembic upgrade head && python -m app.db.seed_plano
"""
import sys
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.common import (
    CanalComunicacion,
    EstadoActivo,
    EstadoLead,
    EstadoReserva,
    EstadoStand,
    PrioridadLead,
    RolUsuario,
    TamanoEmpresa,
)
from app.models.comercial import Factura, Pago
from app.models.comunicaciones import Plantilla
from app.models.crm import Contacto, Empresa, Lead
from app.models.inventario import Stand
from app.models.patrocinadores import Patrocinador  # noqa: F401
from app.models.reserva import Reserva
from app.models.secuencias import Secuencia, SecuenciaInscripcion, SecuenciaPaso
from app.models.user import Usuario

CLAVE_DEMO = "Ejecutivo123*"

# ---------------------------------------------------------------------------
# Usuarios de prueba: 4 ejecutivos (docs/01)
# ---------------------------------------------------------------------------

EJECUTIVOS = [
    {
        "nombre_completo": "María López Quispe",
        "email": "maria.lopez@emcproducciones.com",
        "cargo": "Ejecutiva comercial senior",
        "especialidad": "urbanizaciones inmobiliaria",
        "whatsapp": "+591 700111222",
    },
    {
        "nombre_completo": "Carlos Mamani Choque",
        "email": "carlos.mamani@emcproducciones.com",
        "cargo": "Ejecutivo comercial",
        "especialidad": "construcción estructuras",
        "whatsapp": "+591 700333444",
    },
    {
        "nombre_completo": "Ana Vargas Rojas",
        "email": "ana.vargas@emcproducciones.com",
        "cargo": "Ejecutiva comercial",
        "especialidad": "materiales acabados",
        "whatsapp": "+591 700555666",
    },
    {
        "nombre_completo": "Luis Fernández Gutiérrez",
        "email": "luis.fernandez@emcproducciones.com",
        "cargo": "Ejecutivo comercial",
        "especialidad": "maquinaria seguridad",
        "whatsapp": "+591 700777888",
    },
]

# ---------------------------------------------------------------------------
# Empresas reales del sector en Bolivia (fuentes: ranking Nueva Economía,
# directorio RubrosDirectory del proyecto, sitios oficiales consultados)
# ---------------------------------------------------------------------------

EMPRESAS = [
    # Urbanizaciones & Condominios
    ("Parque Industrial Latinoamericano S.R.L.", "Parque Industrial Latinoamericano", "urbanizaciones", "Santa Cruz", "grande", "https://www.nuevaeconomia.com.bo"),
    ("Constructora e Inmobiliaria Urubó Village S.A.", "Urubó Village", "urbanizaciones", "Santa Cruz", "grande", None),
    ("Macororó Inversiones S.R.L.", "Macororó", "urbanizaciones", "Santa Cruz", "mediana", None),
    ("Colinas del Urubó Condominio Privado", "Colinas del Urubó", "condominios", "Santa Cruz", "mediana", None),
    ("Ciudad Milenio Urbanizaciones y Lotes", "Ciudad Milenio", "urbanizaciones", "El Alto", "mediana", None),
    ("El Pahuichi Urbanizaciones", "El Pahuichi", "urbanizaciones", "Santa Cruz", "grande", None),
    ("Mar Adentro Urbanización & Crystal Lagoons", "Mar Adentro", "urbanizaciones", "Santa Cruz", "grande", None),
    # Inmobiliaria & Proyectos
    ("Constructora e Inmobiliaria Aquavista Golf S.A.", "Aquavista Golf", "inmobiliaria", "Santa Cruz", "grande", None),
    ("Compañía de Inversiones Comversa S.A.", "Comversa", "inversiones inmobiliarias", "Santa Cruz", "grande", None),
    ("Century 21 Bolivia", "Century 21", "bienes raíces", "Santa Cruz", "mediana", None),
    ("Grupo Sion Inmobiliaria", "Grupo Sion", "inmobiliaria", "La Paz", "mediana", None),
    ("Bolivia Propiedades Portal Inmobiliario", "Bolivia Propiedades", "portal inmobiliario", "La Paz", "pequeña", "https://www.boliviapropiedades.com"),
    # Diseño, Estructuras & Construcción
    ("Ingeniería y Construcciones Técnicas Incotec S.A.", "Incotec", "construcción", "La Paz", "grande", None),
    ("Inesco Ingeniería & Construcción S.A.", "Inesco", "ingeniería construcción", "La Paz", "grande", None),
    ("Empresa Constructora y Comercial Cofersa Ltda.", "Cofersa", "construcción", "Santa Cruz", "mediana", None),
    ("Industrias Ferrotodo (Estructuras)", "Ferrotodo", "estructuras metálicas", "Santa Cruz", "mediana", "https://ferrotodo.com"),
    ("Industrias Duralit S.A. (Tejas)", "Duralit", "tejas techos", "Cochabamba", "grande", None),
    ("Cristembo (Industria del Vidrio)", "Cristembo", "vidrio aluminio", "Santa Cruz", "mediana", None),
    # Maquinaria Pesada & Equipos
    ("Finning CAT Bolivia", "Finning CAT", "maquinaria pesada", "Santa Cruz", "grande", None),
    ("Gregomaq S.R.L.", "Gregomaq", "maquinaria pesada", "Santa Cruz", "mediana", None),
    ("Hansa Ltda. (Industria & Construcción)", "Hansa", "equipos industriales", "Santa Cruz", "grande", None),
    ("AGSA – Agencias Generales S.A.", "AGSA", "maquinaria jardín", "Santa Cruz", "mediana", None),
    ("EquipExitos Bolivia", "EquipExitos", "equipos construcción", "La Paz", "pequeña", None),
    # Materiales & Obra Fina
    ("SOBOCE S.A.", "SOBOCE", "cemento materiales", "La Paz", "grande", "https://soboce.com"),
    ("FANCESA (Fábrica Nacional de Cemento)", "FANCESA", "cemento", "Sucre", "grande", None),
    ("Cerámica COBOCE", "COBOCE", "cerámica ladrillos", "Cochabamba", "grande", None),
    ("Cerámica Gladymar", "Gladymar", "cerámica pisos", "Santa Cruz", "grande", None),
    ("Faboce S.R.L. (Pisos & Porcelanatos)", "Faboce", "porcelanatos", "Santa Cruz", "mediana", None),
    ("Importadora Campero", "Importadora Campero", "materiales construcción", "Santa Cruz", "grande", None),
    # Domótica & Seguridad
    ("AGADON Seguridad Electrónica", "AGADON", "seguridad electrónica", "Santa Cruz", "mediana", None),
    ("Bolivian Group S.R.L. (Alarmas & Monitoreo)", "Bolivian Group", "alarmas monitoreo", "Santa Cruz", "mediana", None),
    ("Electrored (Bolivia) S.R.L.", "Electrored", "cctv seguridad", "La Paz", "mediana", None),
    ("DOMOBOL Bolivia", "DOMOBOL", "domótica", "La Paz", "pequeña", None),
    ("Haustechnik S.R.L.", "Haustechnik", "seguridad electrónica", "Santa Cruz", "pequeña", None),
]

# ---------------------------------------------------------------------------
# Plantillas de mensajes (Fase 2)
# ---------------------------------------------------------------------------

PLANTILLAS = [
    {
        "nombre": "Invitación estándar",
        "tipo": "invitacion",
        "canal": CanalComunicacion.email,
        "contenido": (
            "Estimado/a {{contacto}} de {{empresa}}:\n\n"
            "En nombre de EMC Producciones, queremos invitarle a la 1ra Expo "
            "Inmobiliaria y Construcción Internacional de El Alto — EXPOINCO 2027 "
            "(abril 2027). Contamos con stands interiores en 6 zonas y canchas "
            "para maquinaria pesada.\n\n"
            "Prepararemos una propuesta personalizada para el rubro {{rubro}}. "
            "¿Podemos coordinar una llamada?\n\n"
            "Saludos cordiales,\n{{ejecutivo}} · {{ejecutivo_cargo}}\n"
            "WhatsApp: {{ejecutivo_whatsapp}} · {{ejecutivo_email}}"
        ),
    },
    {
        "nombre": "Propuesta comercial",
        "tipo": "propuesta",
        "canal": CanalComunicacion.pdf,
        "contenido": (
            "PROPUESTA COMERCIAL — EXPOINCO 2027\n\n"
            "Empresa: {{empresa}} ({{nombre_comercial}})\n"
            "Rubro: {{rubro}} · Ciudad: {{ciudad}}\n\n"
            "1. Espacio sugerido: stand interior premium o cancha de maquinaria.\n"
            "2. Beneficios: presencia en el plano interactivo, catálogo de "
            "expositores, rondas de negocios y difusión multicanal.\n"
            "3. Inversión: según paquete seleccionado (confirmar con su ejecutivo).\n"
            "4. Reserva: el stand se bloquea 30 minutos al solicitarlo por la web.\n\n"
            "Atentamente,\n{{ejecutivo}} · {{ejecutivo_cargo}}\n"
            "{{ejecutivo_email}} · {{ejecutivo_whatsapp}}"
        ),
    },
    {
        "nombre": "Confirmación de reserva",
        "tipo": "contrato",
        "canal": CanalComunicacion.whatsapp,
        "contenido": (
            "¡Hola {{contacto}}! Tu solicitud de reserva de stand para {{empresa}} "
            "fue recibida. Un ejecutivo confirmará la disponibilidad y te enviará "
            "el contrato para firma digital. — EMC Producciones · EXPOINCO 2027"
        ),
    },
    {
        "nombre": "Seguimiento post-propuesta",
        "tipo": "nutricion",
        "canal": CanalComunicacion.email,
        "contenido": (
            "Hola {{contacto}}, queríamos saber si tuviste la oportunidad de "
            "revisar la propuesta para {{empresa}}. Los stands con mejor ubicación "
            "se asignan por orden de reserva. Quedamos atentos.\n\n"
            "{{ejecutivo}} · EMC Producciones"
        ),
    },
    {
        "nombre": "Recordatorio de pago",
        "tipo": "nutricion",
        "canal": CanalComunicacion.whatsapp,
        "contenido": (
            "Hola {{contacto}}, recordatorio amable: el pago de reserva de "
            "{{empresa}} está pendiente. Coordina con {{ejecutivo}} "
            "({{ejecutivo_whatsapp}}) para confirmar tu stand. ¡Gracias!"
        ),
    },
]

# ---------------------------------------------------------------------------
# Secuencia de seguimiento (Fase 2)
# ---------------------------------------------------------------------------

SECUENCIA = {
    "nombre": "Nutrición estándar expositor",
    "descripcion": "Invitación + 2 seguimientos en 3 semanas para nuevos prospectos.",
    "canal": CanalComunicacion.email,
    "pasos": [
        {"orden": 1, "dias_espera": 0, "plantilla_idx": 0},
        {"orden": 2, "dias_espera": 7, "plantilla_idx": 3},
        {"orden": 3, "dias_espera": 14, "plantilla_idx": 3},
    ],
}

# ---------------------------------------------------------------------------
# Patrocinadores (Fase 4)
# ---------------------------------------------------------------------------

PATROCINADORES = [
    ("Grupo Sion Inmobiliaria", "oro", "https://gruposion.com.bo"),
    ("SOBOCE S.A.", "plata", "https://soboce.com"),
    ("Industrias Ferrotodo", "bronce", "https://ferrotodo.com"),
    ("Todocentro", "aliado", "https://todocentro.com.bo"),
]


def seed_demo(force: bool = False) -> None:
    db = SessionLocal()
    try:
        existe = db.scalar(select(Empresa).where(Empresa.origen == "demo"))
        if existe is not None and not force:
            print("Los datos de demo ya existen. Usa --force para recrearlos.")
            return

        if force:
            print("Eliminando datos de demo previos…")
            # Borrado simple y seguro (solo filas demo / dependencias)
            for model in (Factura, Pago, Reserva):
                for fila in db.scalars(select(model)).all():
                    db.delete(fila)
            for insc in db.scalars(select(SecuenciaInscripcion)).all():
                db.delete(insc)
            for paso in db.scalars(select(SecuenciaPaso)).all():
                db.delete(paso)
            for seq in db.scalars(select(Secuencia)).all():
                db.delete(seq)
            for lead in db.scalars(select(Lead)).all():
                db.delete(lead)
            for contacto in db.scalars(select(Contacto)).all():
                db.delete(contacto)
            for empresa in db.scalars(select(Empresa)).all():
                db.delete(empresa)
            for plantilla in db.scalars(select(Plantilla)).all():
                db.delete(plantilla)
            for pat in db.scalars(select(Patrocinador)).all():
                db.delete(pat)
            for usuario in db.scalars(
                select(Usuario).where(Usuario.email.like("%@emcproducciones.com"))
            ).all():
                if usuario.rol == RolUsuario.ejecutivo:
                    db.delete(usuario)
            db.commit()

        # ---- 1. Ejecutivos ----
        ejecutivos: list[Usuario] = []
        for datos in EJECUTIVOS:
            usuario = db.scalar(select(Usuario).where(Usuario.email == datos["email"]))
            if usuario is None:
                usuario = Usuario(
                    **datos,
                    hashed_password=hash_password(CLAVE_DEMO),
                    rol=RolUsuario.ejecutivo,
                )
                db.add(usuario)
                db.flush()
            ejecutivos.append(usuario)
        print(f"✓ {len(ejecutivos)} ejecutivos de ventas")

        # ---- 2. Plantillas ----
        plantillas: list[Plantilla] = []
        for datos in PLANTILLAS:
            p = db.scalar(select(Plantilla).where(Plantilla.nombre == datos["nombre"]))
            if p is None:
                p = Plantilla(**datos, estado=EstadoActivo.activo)
                db.add(p)
                db.flush()
            plantillas.append(p)
        print(f"✓ {len(plantillas)} plantillas de mensajes")

        # ---- 3. Empresas + contactos ----
        contactos: list[Contacto] = []
        for idx, (razon, comercial, rubro, ciudad, tamano, web) in enumerate(EMPRESAS):
            empresa = db.scalar(select(Empresa).where(Empresa.razon_social == razon))
            if empresa is not None:
                continue
            ejecutivo = ejecutivos[idx % len(ejecutivos)]
            empresa = Empresa(
                razon_social=razon,
                nombre_comercial=comercial,
                rubro=rubro,
                ciudad=ciudad,
                pais="Bolivia",
                sitio_web=web,
                tamano_empresa=TamanoEmpresa(tamano),
                estado=EstadoLead.interesado if idx % 3 == 0 else EstadoLead.contactado,
                ejecutivo_id=ejecutivo.id,
                origen="demo",
            )
            db.add(empresa)
            db.flush()
            contacto = Contacto(
                empresa_id=empresa.id,
                nombre=f"Contacto {comercial}",
                cargo="Gerente comercial",
                email=f"contacto{idx + 1}@{comercial.lower().replace(' ', '').replace('.', '')[:18]}.bo",
                whatsapp=f"+591 6{idx + 1:02d}00{idx + 1:02d}",
            )
            db.add(contacto)
            db.flush()
            contactos.append(contacto)
        print(f"✓ {len(EMPRESAS)} empresas con contacto")

        # ---- 4. Leads (embudo variado) ----
        empresas_demo = db.scalars(
            select(Empresa).where(Empresa.origen == "demo").order_by(Empresa.created_at)
        ).all()
        estados = [
            EstadoLead.prospecto,
            EstadoLead.contactado,
            EstadoLead.interesado,
            EstadoLead.propuesta_enviada,
            EstadoLead.en_negociacion,
            EstadoLead.reserva_temporal,
            EstadoLead.vendido,
        ]
        prioridades = [PrioridadLead.alta, PrioridadLead.media, PrioridadLead.baja]
        for idx, empresa in enumerate(empresas_demo):
            if db.scalar(select(Lead).where(Lead.empresa_id == empresa.id)):
                continue
            contacto = next(
                (c for c in contactos if c.empresa_id == empresa.id), None
            )
            lead = Lead(
                empresa_id=empresa.id,
                contacto_id=contacto.id if contacto else None,
                ejecutivo_id=empresa.ejecutivo_id,
                origen="demo",
                rubro=empresa.rubro,
                interes="stand premium" if idx % 2 == 0 else "cancha de maquinaria",
                prioridad=prioridades[idx % len(prioridades)],
                estado=estados[idx % len(estados)],
                proxima_accion="Llamada de seguimiento" if idx % 3 == 0 else None,
                fecha_proxima_accion=(
                    datetime.now(timezone.utc) + timedelta(days=2)
                ) if idx % 3 == 0 else None,
            )
            db.add(lead)
        print(f"✓ {len(empresas_demo)} leads en embudo variado")

        # ---- 5. Secuencia de seguimiento + inscripciones ----
        secuencia = db.scalar(select(Secuencia).where(Secuencia.nombre == SECUENCIA["nombre"]))
        if secuencia is None:
            secuencia = Secuencia(
                nombre=SECUENCIA["nombre"],
                descripcion=SECUENCIA["descripcion"],
                canal=SECUENCIA["canal"],
                estado=EstadoActivo.activo,
            )
            db.add(secuencia)
            db.flush()
            for paso in SECUENCIA["pasos"]:
                db.add(SecuenciaPaso(
                    secuencia_id=secuencia.id,
                    orden=paso["orden"],
                    dias_espera=paso["dias_espera"],
                    plantilla_id=plantillas[paso["plantilla_idx"]].id,
                ))
            for empresa in empresas_demo[:6]:
                contacto = next((c for c in contactos if c.empresa_id == empresa.id), None)
                db.add(SecuenciaInscripcion(
                    secuencia_id=secuencia.id,
                    empresa_id=empresa.id,
                    contacto_id=contacto.id if contacto else None,
                    paso_actual=0,
                    proxima_ejecucion=datetime.now(timezone.utc),
                    estado="activa",
                ))
        print("✓ Secuencia de seguimiento con pasos e inscripciones")

        # ---- 6. Patrocinadores ----
        for orden, (nombre, categoria, web) in enumerate(PATROCINADORES):
            if db.scalar(select(Patrocinador).where(Patrocinador.nombre == nombre)):
                continue
            db.add(Patrocinador(
                nombre=nombre,
                categoria=categoria,
                sitio_web=web,
                estado=EstadoActivo.activo,
                orden=orden,
            ))
        print(f"✓ {len(PATROCINADORES)} patrocinadores")

        # ---- 7. Flujo de ejemplo: reserva → pago → factura ----
        if db.scalar(select(Reserva).where(Reserva.estado == EstadoReserva.vendido)) is None:
            ahora = datetime.now(timezone.utc)

            def _stand(codigo: str) -> Stand | None:
                return db.scalar(select(Stand).where(Stand.codigo == codigo))

            # Reserva vendida con pago confirmado y factura emitida
            s1, s2 = _stand("5"), _stand("6")
            e1 = empresas_demo[0]
            r1 = Reserva(
                empresa_id=e1.id,
                lead_id=None,
                stand_id=s1.id,
                ejecutivo_id=e1.ejecutivo_id,
                estado=EstadoReserva.vendido,
                fecha_inicio=ahora - timedelta(days=10),
                monto=4500,
            )
            db.add(r1)
            db.flush()
            s1.estado = EstadoStand.vendido
            s1.reserva_activa_id = r1.id
            db.add(Pago(
                reserva_id=r1.id,
                empresa_id=e1.id,
                monto=4500,
                metodo="transferencia",
                referencia="TRF-DEMO-001",
                estado="confirmado",
                registrado_por=e1.ejecutivo_id,
            ))
            db.add(Factura(
                reserva_id=r1.id,
                empresa_id=e1.id,
                numero="F-00001",
                nit="1234567001",
                razon_social=e1.razon_social,
                monto=4500,
                estado="emitida",
            ))

            # Reserva confirmada pendiente de pago
            if s2 is not None:
                e2 = empresas_demo[1]
                r2 = Reserva(
                    empresa_id=e2.id,
                    stand_id=s2.id,
                    ejecutivo_id=e2.ejecutivo_id,
                    estado=EstadoReserva.reservado,
                    fecha_inicio=ahora - timedelta(days=2),
                    monto=3800,
                )
                db.add(r2)
                db.flush()
                s2.estado = EstadoStand.reservado
                s2.reserva_activa_id = r2.id
                db.add(Pago(
                    reserva_id=r2.id,
                    empresa_id=e2.id,
                    monto=1900,
                    metodo="qr",
                    referencia="QR-DEMO-002",
                    estado="pendiente",
                    registrado_por=e2.ejecutivo_id,
                ))
            print("✓ Flujo de ejemplo reserva → pago → factura")

        db.commit()
        print("\nDatos de demo cargados. Acceso de prueba:")
        print("  Admin:     admin@emcproducciones.com / (SEED_ADMIN_PASSWORD)")
        print(f"  Ejecutivo: {EJECUTIVOS[0]['email']} / {CLAVE_DEMO}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_demo(force="--force" in sys.argv)
