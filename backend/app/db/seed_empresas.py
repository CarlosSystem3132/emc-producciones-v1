"""Seed de datos reales: empresas prospecto + plantillas operativas.

A diferencia de `seed_demo` (demostración con registros simulados), este seed
puebla la base ÚNICAMENTE con datos reales y operativos:

- Empresas reales de Bolivia (prospección EXPOINCO 2027) con los campos
  requeridos: razón social, rubro, ciudad (cuando está verificada) y sitio
  web (cuando se conoce). Sin contactos ficticios, sin leads, sin ejecutivos
  de prueba, sin notificaciones ni registros simulados.
- Las 5 plantillas operativas de comunicación (invitación, propuesta,
  confirmación, seguimiento, recordatorio).

Uso:

    python -m app.db.seed_empresas

Idempotente: no duplica empresas cuya razón social ya exista (ignora
mayúsculas) ni plantillas con el mismo nombre.
"""
import sys

from sqlalchemy import func, select

from app.db.session import SessionLocal
from app.models.common import CanalComunicacion, EstadoActivo, EstadoLead
from app.models.comunicaciones import Plantilla
from app.models.crm import Empresa

# (razón social, rubro, ciudad|None, sitio web|None) — fuente:
# directorio comercial EXPOINCO + investigación web verificada (2026).
EMPRESAS = [
    ('Constructora y Consultora SAVI CBBA S.R.L.', 'Constructoras', 'Cochabamba', None),
    ('Industrias Duralit S.A.', 'Constructoras', 'Cochabamba', 'https://duralit.com/'),
    ('Inesco Ingeniería & Construcción S.A.', 'Constructoras', 'La Paz', None),
    ('Ingeniería y Construcciones Técnicas Incotec S.A.', 'Constructoras', 'La Paz', None),
    ('MALTOR S.R.L.', 'Constructoras', 'La Paz', None),
    ('Consultora y Constructora CIM S.R.L.', 'Constructoras', 'Potosí', None),
    ('Empresa Constructora y Comercial Cofersa Ltda.', 'Constructoras', 'Santa Cruz', None),
    ('EquipExitos Bolivia', 'Distribuidoras', 'La Paz', 'https://equipexitos.com/'),
    ('M.A.D. Center', 'Distribuidoras', None, 'https://www.mad-center.com/'),
    ('Homepac S.R.L. (Multicenter)', 'Distribuidoras', 'Santa Cruz', 'https://www.multicenter.com.bo/'),
    ('Importadora Campero', 'Distribuidoras', 'Santa Cruz', 'https://importadoracampero.com.bo/'),
    ('Todocentro', 'Distribuidoras', 'Santa Cruz', 'https://todocentro.com.bo/'),
    ('DOMOBOL Bolivia', 'Herramientas e insumos', 'La Paz', 'https://domobol.com/'),
    ('Dahua Bolivia', 'Herramientas e insumos', 'La Paz', 'https://dahuabolivia.com/'),
    ('Electrored (Bolivia) S.R.L.', 'Herramientas e insumos', 'La Paz', 'https://www.electrored.com.bo/'),
    ('Sawers Bolivia', 'Herramientas e insumos', 'La Paz', 'https://tienda.sawers.com.bo/'),
    ('Papaiz Cerraduras Bolivia', 'Herramientas e insumos', None, 'https://importadoracampero.com.bo/'),
    ('S.I.PRO.C. Seguridad', 'Herramientas e insumos', None, 'https://www.siproc.com/'),
    ('Schneider Electric Bolivia', 'Herramientas e insumos', None, 'https://www.se.com/bo/es/'),
    ('Schneider Smart Home Bolivia', 'Herramientas e insumos', None, 'https://www.se.com/bo/es/'),
    ('Seguridad Privada Boliviana', 'Herramientas e insumos', None, 'https://seguribol.com.bo/'),
    ('Tecnomatic Automatización Bolivia', 'Herramientas e insumos', None, 'https://www.tecnomatic.com.bo/'),
    ('Tigre Bolivia', 'Herramientas e insumos', None, 'https://tigre.bo/'),
    ('Truper Cerraduras & Candados Bolivia', 'Herramientas e insumos', None, 'https://www.truper.com/'),
    ('AGADON', 'Herramientas e insumos', 'Santa Cruz', 'https://www.agadon.com.bo/seguridad-electronica.html'),
    ('Bolivian Group S.R.L.', 'Herramientas e insumos', 'Santa Cruz', 'https://bolivianelectric.com.bo/'),
    ('Haustechnik S.R.L.', 'Herramientas e insumos', 'Santa Cruz', None),
    ('Prosegur Bolivia', 'Herramientas e insumos', 'Santa Cruz', 'https://www.prosegur.com/'),
    ('Bolivia Propiedades Portal Inmobiliario', 'Inmobiliarias', 'La Paz', 'https://www.boliviapropiedades.com/'),
    ('Grupo Sion Inmobiliaria', 'Inmobiliarias', 'La Paz', 'https://www.gruposion.bo/'),
    ('Casa Crédito Inmobiliaria Bolivia', 'Inmobiliarias', None, 'https://casacredito.com/bolivia/'),
    ('InfoCasas Bolivia', 'Inmobiliarias', None, 'https://www.infocasas.com.bo/'),
    ('La Fuente Inmobiliaria', 'Inmobiliarias', None, None),
    ('Latin Bienes Raíces Bolivia', 'Inmobiliarias', None, 'https://www.latinbienesraices.com/'),
    ('RE/MAX Bolivia', 'Inmobiliarias', None, 'https://www.remax.bo/'),
    ('Smart Studio Desarrollos Inmobiliarios', 'Inmobiliarias', None, 'https://www.smartstudio.com.bo/'),
    ('Century 21 Bolivia', 'Inmobiliarias', 'Santa Cruz', 'https://c21.com.bo/'),
    ('Compañía de Inversiones Comversa S.A.', 'Inmobiliarias', 'Santa Cruz', None),
    ('Constructora e Inmobiliaria Aquavista Golf S.A.', 'Inmobiliarias', 'Santa Cruz', None),
    ('Las Palmas del Urubó', 'Inmobiliarias', 'Santa Cruz', 'https://laspalmasdelurubo.com/'),
    ('Urubó Village', 'Inmobiliarias', 'Santa Cruz', 'https://villageurubo.com/'),
    ('Puntomaq / Komatsu Bolivia', 'Maquinaria pesada', None, 'https://www.komatsulatinoamerica.com/bolivia/'),
    ('SACI Maquinarias', 'Maquinaria pesada', None, 'https://www.saci.com.bo/'),
    ('AGSA – Agencias Generales S.A.', 'Maquinaria pesada', 'Santa Cruz', 'https://www.agsa.com/'),
    ('Finning CAT Bolivia', 'Maquinaria pesada', 'Santa Cruz', 'https://www.finning.com/es_BO.html'),
    ('Gregomaq S.R.L.', 'Maquinaria pesada', 'Santa Cruz', 'https://www.gregomaq.com/'),
    ('Hansa Ltda.', 'Maquinaria pesada', 'Santa Cruz', 'https://www.hi.com.bo/'),
    ('FANCESA (Fábrica Nacional de Cemento)', 'Materiales', 'Sucre', 'https://fancesa.com/'),
    ('COBOCE', 'Materiales', 'Cochabamba', 'https://ceramicacoboce.com/'),
    ('Cemento Viacha (La Paz)', 'Materiales', 'Viacha', 'https://soboce.com/'),
    ('Incerpaz', 'Materiales', 'La Paz', None),
    ('SOBOCE S.A.', 'Materiales', 'La Paz', 'https://soboce.com/'),
    ('Aceros Arequipa Bolivia', 'Materiales', None, 'https://acerosarequipa.com/bo/'),
    ('Alvitec Carpintería de Aluminio', 'Materiales', None, 'https://www.alvitec.com.bo/'),
    ('Alvitec Vidrios & Cerramientos', 'Materiales', None, 'https://www.alvitec.com.bo/'),
    ('ArcelorMittal Bolivia', 'Materiales', None, 'https://bolivia.arcelormittal.com/'),
    ('Bosch Professional Bolivia', 'Materiales', None, 'https://www.bosch-professional.com/bo/es/'),
    ('CIF CONDOR S.R.L.', 'Materiales', None, 'https://calaminascondor.com/'),
    ('CONDOR S.R.L. / Calaminas Cóndor', 'Materiales', None, 'https://calaminascondor.com/'),
    ('Cerámica Titán', 'Materiales', None, 'https://ceramicatitan.com/inicio/'),
    ('Chemical Bolivia Ltda.', 'Materiales', None, 'https://wetbolivia.com/'),
    ('Coprodumat Ltda.', 'Materiales', None, 'https://coprodumat.com/'),
    ('DECO-IM', 'Materiales', None, 'https://www.decoim.cl/'),
    ('Duraplac Bolivia', 'Materiales', None, 'https://duraplast.com.pe/'),
    ('Estuco Vichaya', 'Materiales', None, 'https://estucovichaya.com/'),
    ('FLEXCOLOR Bolivia', 'Materiales', None, 'https://flex-color.com/'),
    ('FV / Canal Bolivia (Grifería)', 'Materiales', None, 'https://importadoracampero.com.bo/producto/griferia/'),
    ('IMPOAL Bolivia', 'Materiales', None, 'https://impoal.net/'),
    ('Industrias del Oriente – MAXXI', 'Materiales', None, 'https://ioriente.com/'),
    ('Itacamba Cemento S.A.', 'Materiales', None, 'https://www.itacamba.com/'),
    ('Italpissos Bolivia', 'Materiales', None, 'https://italpisos.com.ec/'),
    ('Laminex Bolivia', 'Materiales', None, 'https://www.laminexbolivia.com/'),
    ('Makita Bolivia', 'Materiales', None, 'https://www.makita.com.bo/'),
    ('Mapei Bolivia', 'Materiales', None, 'https://mapei.com/bo/'),
    ('Milter Bolivia', 'Materiales', None, 'https://milter.bo/'),
    ('Monterrey (Puertas & Ventanas PVC)', 'Materiales', None, 'https://www.monterrey.com.bo/'),
    ('Monterrey Aceros Bolivia', 'Materiales', None, 'https://www.monterrey.com.bo/'),
    ('Monterrey Calaminas & Estructuras', 'Materiales', None, 'https://www.monterrey.com.bo/'),
    ('Monterrey Yesos & Acabados', 'Materiales', None, 'https://www.monterrey.com.bo/'),
    ('Morales Ltda.', 'Materiales', None, 'https://www.morales.com.bo/'),
    ('Morales Ltda. Baños y Sanitarios', 'Materiales', None, 'https://www.morales.com.bo/'),
    ('Morales Ltda. Diseño Interior', 'Materiales', None, 'https://www.morales.com.bo/'),
    ('Morales Ltda. Materiales Cerámicos', 'Materiales', None, 'https://www.morales.com.bo/'),
    ('Morales Ltda. Revestimientos', 'Materiales', None, 'https://morales.com.bo/'),
    ('Partner Bolivia (Sistemas Deceuninck)', 'Materiales', None, 'https://www.partner.com.bo/'),
    ('Partner Bolivia Aluminio', 'Materiales', None, 'https://www.partner.com.bo/'),
    ('Partner Bolivia Cristal', 'Materiales', None, 'https://www.partner.com.bo/'),
    ('Pinturas Coral Bolivia', 'Materiales', None, 'https://www.coral.com.bo/'),
    ('Pinturas MONOPOL', 'Materiales', None, 'https://www.pinturasmonopol.com/'),
    ('Pinturas Monopol (Pegamentos & Colas)', 'Materiales', None, 'https://www.pinturasmonopol.com/'),
    ('Plamat Bolivia (Sistemas de Ventanas)', 'Materiales', None, 'https://www.plamat.com.bo/'),
    ('Plamat Perfiles de Aluminio', 'Materiales', None, 'https://www.plamat.com.bo/'),
    ('ProVen SRL (Ventanas PVC & Aislamiento)', 'Materiales', None, 'https://www.provensrl.com/'),
    ('ProVen SRL Aluminio', 'Materiales', None, 'https://www.provensrl.com/'),
    ('ProVen SRL Vidriería', 'Materiales', None, 'https://www.provensrl.com/'),
    ('Rojas Glass', 'Materiales', None, 'https://rojasglass.com.bo/'),
    ('SACI Agro & Jardín Bolivia', 'Materiales', None, 'https://www.saci.com.bo/'),
    ('SOBOLMA', 'Materiales', None, 'https://sobolma.com/'),
    ('Sika Bolivia', 'Materiales', None, 'https://bol.sika.com/'),
    ('Sika Morteros & Yesos Bolivia', 'Materiales', None, 'https://bol.sika.com/'),
    ('Sika Pinturas y Revestimientos Bolivia', 'Materiales', None, 'https://bol.sika.com/'),
    ('Sinter Bolivia', 'Materiales', None, 'https://sinterbolivia.com/'),
    ('Sorimex S.R.L.', 'Materiales', None, 'https://sorimex.com/'),
    ('TODO TECHO Bolivia', 'Materiales', None, 'https://todotechobolivia.com/'),
    ('TecnoSuisse Bolivia', 'Materiales', None, 'https://www.tecnosuisse.com/'),
    ('Tigre Riego Bolivia', 'Materiales', None, 'https://tigre.bo/'),
    ('Truper Bolivia (Salcedo Importaciones)', 'Materiales', None, 'https://www.truper.com/'),
    ('VidrAlum Bolivia', 'Materiales', None, 'https://www.vidralum.com.bo/'),
    ('VidrAlum Bolivia (Aluminio y Cerramientos)', 'Materiales', None, 'https://www.vidralum.com.bo/'),
    ('VidrAlum Bolivia (Vidrios Templados)', 'Materiales', None, 'https://www.vidralum.com.bo/'),
    ('Weber / Saint-Gobain Bolivia', 'Materiales', None, 'https://saint-gobain.com/'),
    ('Cemento Warnes (Santa Cruz)', 'Materiales', 'Warnes', 'https://soboce.com/'),
    ('Cerabol Ltda.', 'Materiales', 'Santa Cruz', 'https://www.cerabol.com/'),
    ('Cerámica Gladymar', 'Materiales', 'Santa Cruz', 'https://gladymar.com.bo/'),
    ('Cristembo', 'Materiales', 'Santa Cruz', 'https://www.cristembo.com/'),
    ('Faboce S.R.L.', 'Materiales', 'Santa Cruz', 'https://www.faboce.com.bo/'),
    ('Industrias Ferrotodo', 'Materiales', 'Santa Cruz', 'https://ferrotodo.com/'),
    ('Cemento El Puente (Tarija)', 'Materiales', 'Tarija', 'https://soboce.com/'),
    ('Ciudad Milenio Urbanizaciones y Lotes', 'Urbanizaciones', 'El Alto', None),
    ('Condado del Valle Urbanizaciones', 'Urbanizaciones', None, None),
    ('Inbolsa — Terrenos & Lotes Urbanos', 'Urbanizaciones', None, 'https://www.inbolsa.com/'),
    ('Kalomai Park Resort & Urbanizaciones', 'Urbanizaciones', None, None),
    ('Lotes al Día — Venta de Terrenos en Cuotas', 'Urbanizaciones', None, None),
    ('Lotes y Urbanizaciones La Paz - El Alto', 'Urbanizaciones', None, None),
    ('TerraVida — Lotes & Condominios Ecológicos', 'Urbanizaciones', None, None),
    ('Terranova Urbanizaciones', 'Urbanizaciones', None, None),
    ('Terreno & Lotes Bolivia', 'Urbanizaciones', None, None),
    ('TerrenoBolivia — Lotes y Terrenos', 'Urbanizaciones', None, None),
    ('Colinas del Urubó Condominio Privado', 'Urbanizaciones', 'Santa Cruz', None),
    ('El Pahuichi Urbanizaciones', 'Urbanizaciones', 'Santa Cruz', 'https://elpahuichi.com.bo/'),
    ('Macororó Inversiones S.R.L.', 'Urbanizaciones', 'Santa Cruz', None),
    ('Mar Adentro Urbanización & Crystal Lagoons', 'Urbanizaciones', 'Santa Cruz', None),
    ('Parque Industrial Latinoamericano S.R.L.', 'Urbanizaciones', 'Santa Cruz', None),
    ('Playa Turquesa', 'Urbanizaciones', 'Santa Cruz', 'https://playaturquesa.bo/'),
]

# Plantillas operativas reales (con variables {{...}}); no hay datos simulados.
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
            "3. Inversión: según paquete seleccionado (confirmar con su ejecutivo).\n\n"
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


def seed_empresas(force: bool = False) -> None:
    db = SessionLocal()
    try:
        creadas = 0
        for razon_social, rubro, ciudad, web in EMPRESAS:
            existe = db.scalar(
                select(Empresa).where(
                    func.lower(Empresa.razon_social) == razon_social.lower()
                )
            )
            if existe is not None:
                continue
            db.add(Empresa(
                razon_social=razon_social,
                rubro=rubro,
                ciudad=ciudad,
                pais="Bolivia",
                sitio_web=web,
                estado=EstadoLead.prospecto,
                origen="prospeccion",
            ))
            creadas += 1

        plantillas_creadas = 0
        for datos in PLANTILLAS:
            existe = db.scalar(select(Plantilla).where(Plantilla.nombre == datos["nombre"]))
            if existe is not None:
                continue
            db.add(Plantilla(**datos, estado=EstadoActivo.activo))
            plantillas_creadas += 1

        db.commit()
        print(f"✓ {creadas} empresas reales cargadas ({len(EMPRESAS)} en el listado)")
        print(f"✓ {plantillas_creadas} plantillas operativas cargadas")
        print("Sin datos simulados: no se crean ejecutivos, leads, reservas,")
        print("pagos, notificaciones ni patrocinadores de prueba.")
    finally:
        db.close()


if __name__ == "__main__":
    seed_empresas(force="--force" in sys.argv)
