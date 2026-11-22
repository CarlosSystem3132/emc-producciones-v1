#!/usr/bin/env python3
"""Genera `empresas-bolivia-2027.xlsx` — directorio de empresas de Bolivia
para la EXPOINCO 2027 (urbanizaciones, inmobiliarias, distribuidoras,
constructoras, maquinaria pesada, materiales, herramientas e insumos).

Fuentes de datos:
1. `src/components/RubrosDirectory.tsx` — directorio comercial curado del
   proyecto (empresas reales con sitio web / redes, 25 rubros).
2. Investigación web del proyecto (rankings, sitios oficiales, listados
   públicos) — aporta departamento/ciudad y algunos contactos.

Uso:  python3 scripts/generar_empresas_bolivia.py
Salida: empresas-bolivia-2027.xlsx (en la raíz del repositorio)

NOTA: los campos de contacto marcados «Por verificar» deben validarse en el
sitio web de cada empresa antes de usarlos en campañas.
"""
import re
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

RAIZ = Path(__file__).resolve().parent.parent
TSX = RAIZ / "src" / "components" / "RubrosDirectory.tsx"
SALIDA = RAIZ / "empresas-bolivia-2027.xlsx"

CATEGORIAS = [
    "Urbanizaciones",
    "Inmobiliarias",
    "Distribuidoras",
    "Constructoras",
    "Maquinaria pesada",
    "Materiales",
    "Herramientas e insumos",
]

DEPARTAMENTOS = [
    "La Paz", "Santa Cruz", "Cochabamba", "Chuquisaca", "Tarija",
    "Oruro", "Potosí", "Beni", "Pando", "Por verificar",
]

# ---------------------------------------------------------------------------
# 1) Directorio curado del proyecto
# ---------------------------------------------------------------------------

def parsear_directorio() -> list[dict]:
    texto = TSX.read_text(encoding="utf-8")
    empresas = []
    for m in re.finditer(
        r"\{\s*id: '([^']+)',\s*name: '([^']+)',\s*companies: \[(.*?)\],\s*\}",
        texto,
        re.S,
    ):
        rubro_id, rubro_nombre, bloque = m.groups()
        for c in re.finditer(r"name: '([^']+)'.*?url: '([^']+)'", bloque):
            empresas.append({
                "nombre": c.group(1),
                "url": c.group(2),
                "rubro_id": rubro_id,
                "rubro": rubro_nombre,
            })
    return empresas


# ---------------------------------------------------------------------------
# 2) Categorización (las 7 categorías del proyecto)
# ---------------------------------------------------------------------------

CATEGORIA_POR_RUBRO = {
    "maquinaria-pesada": "Maquinaria pesada",
    "cemento": "Materiales", "ladrillo": "Materiales", "ceramica": "Materiales",
    "pisos": "Materiales", "vidrio": "Materiales", "techos": "Materiales",
    "estuco": "Materiales", "fierro": "Materiales", "pegamentos": "Materiales",
    "pintura": "Materiales", "aluminio": "Materiales",
    "tableros-melaminicos": "Materiales", "estanteria-industrial": "Materiales",
    "carpinteria": "Materiales", "marcos-de-ventana": "Materiales",
    "decoracion-de-interior": "Materiales", "equipamiento-de-cocina": "Materiales",
    "banos-sanitarios-griferia": "Materiales", "paisajismo": "Materiales",
    "cerrajeria": "Herramientas e insumos",
    "materiales-electricos": "Herramientas e insumos",
    "domotica": "Herramientas e insumos", "seguridad": "Herramientas e insumos",
}

# Ajustes por marca (una marca puede ser distribuidora/constructora)
CATEGORIA_POR_MARCA = [
    (r"importadora campero|multicenter|homepac|m\.a\.d\. center|equipexitos|todocentro|sawers", "Distribuidoras"),
    (r"incotec|inesco|cofersa|duralit|maltor|\bcim\b|savi", "Constructoras"),
    (r"hansa ltda|agsa|gregomaq|finning|puntomaq|komatsu|saci maquinarias", "Maquinaria pesada"),
]


def categoria_de(nombre: str, rubro_id: str) -> str:
    bajo = nombre.lower()
    for patron, cat in CATEGORIA_POR_MARCA:
        if re.search(patron, bajo):
            return cat
    if rubro_id == "urbanizaciones":
        if re.search(r"urbanizaci|condominio|lote|terreno|playa|park resort|terravida", bajo):
            return "Urbanizaciones"
        return "Inmobiliarias"
    return CATEGORIA_POR_RUBRO.get(rubro_id, "Materiales")


# ---------------------------------------------------------------------------
# 3) Unificación de marcas repetidas en varios sub-rubros
# ---------------------------------------------------------------------------

MARCAS = [
    (r"todocentro", "Todocentro"),
    (r"ferrotodo", "Industrias Ferrotodo"),
    (r"hansa", "Hansa Ltda."),
    (r"gladymar", "Cerámica Gladymar"),
    (r"importadora campero", "Importadora Campero"),
    (r"coprodumat", "Coprodumat Ltda."),
    (r"cerabol", "Cerabol Ltda."),
    (r"faboce", "Faboce S.R.L."),
    (r"deco-im", "DECO-IM"),
    (r"duralit", "Industrias Duralit S.A."),
    (r"coboce", "COBOCE"),
    (r"electrored", "Electrored (Bolivia) S.R.L."),
    (r"agadon", "AGADON"),
    (r"bolivian group", "Bolivian Group S.R.L."),
    (r"cristembo", "Cristembo"),
    (r"homepac|multicenter", "Homepac S.R.L. (Multicenter)"),
    (r"aceros arequipa", "Aceros Arequipa Bolivia"),
    (r"arcelormittal", "ArcelorMittal Bolivia"),
    (r"bosch professional", "Bosch Professional Bolivia"),
    (r"makita", "Makita Bolivia"),
    (r"italpissos", "Italpissos Bolivia"),
    (r"laminex", "Laminex Bolivia"),
    (r"mapei", "Mapei Bolivia"),
    (r"flexcolor", "FLEXCOLOR Bolivia"),
    (r"estuco vichaya|super yeso vichaya", "Estuco Vichaya"),
    (r"info ?casas", "InfoCasas Bolivia"),
    (r"century 21", "Century 21 Bolivia"),
    (r"re/max", "RE/MAX Bolivia"),
    (r"grupo sion", "Grupo Sion Inmobiliaria"),
    (r"impoal", "IMPOAL Bolivia"),
    (r"equipexitos", "EquipExitos Bolivia"),
    (r"agsa", "AGSA – Agencias Generales S.A."),
    (r"gregomaq", "Gregomaq S.R.L."),
    (r"finning", "Finning CAT Bolivia"),
    (r"siproc", "S.I.PRO.C. Seguridad"),
    (r"seguribol|seguridad privada boliviana", "Seguridad Privada Boliviana"),
    (r"prosegur", "Prosegur Bolivia"),
]


def marca_canonica(nombre: str) -> str:
    bajo = nombre.lower()
    for patron, canonico in MARCAS:
        if re.search(patron, bajo):
            return canonico
    return nombre


# ---------------------------------------------------------------------------
# 4) Enriquecimiento por investigación web (depto/ciudad/contacto)
#    «fuente» indica el origen verificado de cada dato.
# ---------------------------------------------------------------------------

WEB = "sitio oficial / investigación web"
RANKING = "Ranking Nueva Economía (desarrolladores inmobiliarios)"
LISTADO = "listado público (organismo/registro)"

ENRIQUECIMIENTO: dict[str, dict] = {
    # --- Santa Cruz ---
    "Urubó Village": {"dep": "Santa Cruz", "ciudad": "Santa Cruz", "fuente": RANKING},
    "Macororó Inversiones S.R.L.": {"dep": "Santa Cruz", "ciudad": "Santa Cruz", "fuente": RANKING},
    "Constructora e Inmobiliaria Aquavista Golf S.A.": {"dep": "Santa Cruz", "ciudad": "Santa Cruz", "fuente": RANKING},
    "Compañía de Inversiones Comversa S.A.": {"dep": "Santa Cruz", "ciudad": "Santa Cruz", "fuente": RANKING},
    "Parque Industrial Latinoamericano S.R.L.": {"dep": "Santa Cruz", "ciudad": "Santa Cruz", "fuente": RANKING},
    "Empresa Constructora y Comercial Cofersa Ltda.": {"dep": "Santa Cruz", "ciudad": "Santa Cruz", "fuente": RANKING},
    "El Pahuichi Urbanizaciones": {"dep": "Santa Cruz", "ciudad": "Santa Cruz", "fuente": WEB},
    "Mar Adentro Urbanización & Crystal Lagoons": {"dep": "Santa Cruz", "ciudad": "Santa Cruz", "fuente": WEB},
    "Colinas del Urubó Condominio Privado": {"dep": "Santa Cruz", "ciudad": "Santa Cruz", "fuente": WEB},
    "Century 21 Bolivia": {"dep": "Santa Cruz", "ciudad": "Santa Cruz", "fuente": WEB},
    "Las Palmas del Urubó": {"dep": "Santa Cruz", "ciudad": "Santa Cruz", "fuente": WEB},
    "Playa Turquesa": {"dep": "Santa Cruz", "ciudad": "Santa Cruz", "fuente": WEB},
    "Todocentro": {"dep": "Santa Cruz", "ciudad": "Santa Cruz", "fuente": WEB},
    "Industrias Ferrotodo": {"dep": "Santa Cruz", "ciudad": "Santa Cruz", "fuente": WEB},
    "Hansa Ltda.": {"dep": "Santa Cruz", "ciudad": "Santa Cruz", "fuente": WEB},
    "AGSA – Agencias Generales S.A.": {"dep": "Santa Cruz", "ciudad": "Santa Cruz", "fuente": WEB},
    "Gregomaq S.R.L.": {"dep": "Santa Cruz", "ciudad": "Santa Cruz", "fuente": WEB},
    "Finning CAT Bolivia": {"dep": "Santa Cruz", "ciudad": "Santa Cruz", "fuente": WEB},
    "Cerámica Gladymar": {"dep": "Santa Cruz", "ciudad": "Santa Cruz", "fuente": WEB},
    "Faboce S.R.L.": {"dep": "Santa Cruz", "ciudad": "Santa Cruz", "fuente": WEB},
    "Cerabol Ltda.": {"dep": "Santa Cruz", "ciudad": "Santa Cruz", "fuente": WEB},
    "Importadora Campero": {"dep": "Santa Cruz", "ciudad": "Santa Cruz", "fuente": WEB},
    "Homepac S.R.L. (Multicenter)": {"dep": "Santa Cruz", "ciudad": "Santa Cruz", "fuente": WEB},
    "Cristembo": {"dep": "Santa Cruz", "ciudad": "Santa Cruz", "fuente": WEB},
    "AGADON": {"dep": "Santa Cruz", "ciudad": "Santa Cruz", "fuente": WEB},
    "Bolivian Group S.R.L.": {"dep": "Santa Cruz", "ciudad": "Santa Cruz", "fuente": WEB},
    "Haustechnik S.R.L.": {"dep": "Santa Cruz", "ciudad": "Santa Cruz", "telefono": "+591 3 0000000", "fuente": "BoliviaHub (teléfono por confirmar)"},
    "Cemento Warnes (Santa Cruz)": {"dep": "Santa Cruz", "ciudad": "Warnes", "fuente": WEB},
    "Prosegur Bolivia": {"dep": "Santa Cruz", "ciudad": "Santa Cruz", "fuente": WEB},
    # --- La Paz ---
    "Grupo Sion Inmobiliaria": {"dep": "La Paz", "ciudad": "La Paz", "fuente": WEB},
    "Bolivia Propiedades Portal Inmobiliario": {"dep": "La Paz", "ciudad": "La Paz", "fuente": WEB},
    "SOBOCE S.A.": {"dep": "La Paz", "ciudad": "La Paz", "correo": "info@soboce.com", "fuente": WEB},
    "Cemento Viacha (La Paz)": {"dep": "La Paz", "ciudad": "Viacha", "fuente": WEB},
    "Electrored (Bolivia) S.R.L.": {"dep": "La Paz", "ciudad": "La Paz", "fuente": WEB},
    "DOMOBOL Bolivia": {"dep": "La Paz", "ciudad": "La Paz", "fuente": WEB},
    "Sawers Bolivia": {"dep": "La Paz", "ciudad": "La Paz", "fuente": WEB},
    "Dahua Bolivia": {"dep": "La Paz", "ciudad": "La Paz", "fuente": WEB},
    "Incerpaz": {"dep": "La Paz", "ciudad": "La Paz", "fuente": WEB},
    "EquipExitos Bolivia": {"dep": "La Paz", "ciudad": "La Paz", "fuente": WEB},
    "Ingeniería y Construcciones Técnicas Incotec S.A.": {"dep": "La Paz", "ciudad": "La Paz", "fuente": RANKING},
    "Inesco Ingeniería & Construcción S.A.": {"dep": "La Paz", "ciudad": "La Paz", "fuente": RANKING},
    "MALTOR S.R.L.": {"dep": "La Paz", "ciudad": "La Paz", "fuente": LISTADO + " (ANH)"},
    # --- El Alto ---
    "Ciudad Milenio Urbanizaciones y Lotes": {"dep": "La Paz", "ciudad": "El Alto", "fuente": WEB},
    # --- Cochabamba ---
    "COBOCE": {"dep": "Cochabamba", "ciudad": "Cochabamba", "fuente": WEB},
    "Industrias Duralit S.A.": {"dep": "Cochabamba", "ciudad": "Cochabamba", "fuente": WEB},
    "Constructora y Consultora SAVI CBBA S.R.L.": {"dep": "Cochabamba", "ciudad": "Cochabamba", "telefono": "+591 76900333", "fuente": LISTADO + " (ANH)"},
    # --- Chuquisaca ---
    "FANCESA (Fábrica Nacional de Cemento)": {"dep": "Chuquisaca", "ciudad": "Sucre", "red": "facebook.com/CementoFancesa", "fuente": WEB},
    # --- Tarija ---
    "Cemento El Puente (Tarija)": {"dep": "Tarija", "ciudad": "Tarija", "fuente": WEB},
    # --- Potosí ---
    "Consultora y Constructora CIM S.R.L.": {"dep": "Potosí", "ciudad": "Potosí", "contacto": "Gerencia", "telefono": "+591 72414282", "fuente": LISTADO + " (MINEDU)"},
}

# Empresas de la investigación que NO están en el directorio del proyecto
EXTRAS = [
    {"nombre": "Parque Industrial Latinoamericano S.R.L.", "cat": "Urbanizaciones", "url": ""},
    {"nombre": "Macororó Inversiones S.R.L.", "cat": "Urbanizaciones", "url": ""},
    {"nombre": "Constructora e Inmobiliaria Aquavista Golf S.A.", "cat": "Inmobiliarias", "url": ""},
    {"nombre": "Compañía de Inversiones Comversa S.A.", "cat": "Inmobiliarias", "url": ""},
    {"nombre": "Empresa Constructora y Comercial Cofersa Ltda.", "cat": "Constructoras", "url": ""},
    {"nombre": "Ingeniería y Construcciones Técnicas Incotec S.A.", "cat": "Constructoras", "url": ""},
    {"nombre": "Inesco Ingeniería & Construcción S.A.", "cat": "Constructoras", "url": ""},
    {"nombre": "MALTOR S.R.L.", "cat": "Constructoras", "url": ""},
    {"nombre": "Constructora y Consultora SAVI CBBA S.R.L.", "cat": "Constructoras", "url": ""},
    {"nombre": "Consultora y Constructora CIM S.R.L.", "cat": "Constructoras", "url": ""},
    {"nombre": "Haustechnik S.R.L.", "cat": "Herramientas e insumos", "url": ""},
    {"nombre": "Dahua Bolivia", "cat": "Herramientas e insumos", "url": "https://dahuabolivia.com/"},
    {"nombre": "Incerpaz", "cat": "Materiales", "url": ""},
    {"nombre": "Itacamba Cemento S.A.", "cat": "Materiales", "url": "https://www.itacamba.com/"},
    {"nombre": "Sawers Bolivia", "cat": "Herramientas e insumos", "url": "https://tienda.sawers.com.bo/"},
]


def construir_filas() -> list[dict]:
    filas: dict[str, dict] = {}

    def agregar(nombre, categoria, rubros, url, red=""):
        canonico = marca_canonica(nombre)
        fila = filas.get(canonico)
        if fila is None:
            filas[canonico] = {
                "nombre": canonico, "categoria": categoria, "rubros": set(rubros),
                "url": url, "red": red,
            }
        else:
            fila["rubros"].update(rubros)
            fila["url"] = fila["url"] or url
            fila["red"] = fila["red"] or red

    for e in parsear_directorio():
        url, red = e["url"], ""
        if "facebook.com" in url or "instagram.com" in url:
            red, url = url, ""
        agregar(e["nombre"], categoria_de(e["nombre"], e["rubro_id"]), [e["rubro"]], url, red)

    for e in EXTRAS:
        agregar(e["nombre"], e["cat"], ["Investigación web"], e["url"])

    resultado = []
    for fila in filas.values():
        enrique = ENRIQUECIMIENTO.get(fila["nombre"], {})
        resultado.append({
            **fila,
            "rubros": ", ".join(sorted(fila["rubros"])),
            "departamento": enrique.get("dep", "Por verificar"),
            "ciudad": enrique.get("ciudad", "Por verificar"),
            "contacto": enrique.get("contacto", "Por verificar"),
            "telefono": enrique.get("telefono", ""),
            "whatsapp": enrique.get("whatsapp", ""),
            "correo": enrique.get("correo", ""),
            "fuente": enrique.get("fuente", "Directorio EXPOINCO (RubrosDirectory)"),
        })
    resultado.sort(key=lambda f: (f["categoria"], f["departamento"], f["nombre"]))
    return resultado


# ---------------------------------------------------------------------------
# 5) Generación del libro Excel
# ---------------------------------------------------------------------------

def generar_xlsx(filas: list[dict]) -> None:
    wb = Workbook()
    cabecera_fill = PatternFill("solid", fgColor="0E1015")
    cabecera_font = Font(bold=True, color="FFFFFF", size=11)
    borde = Border(*[Side(style="thin", color="D0D5DD")] * 4)
    amarillo = PatternFill("solid", fgColor="FAB800")

    # ---------- LEEME ----------
    leeme = wb.active
    leeme.title = "LEEME"
    notas = [
        ("Directorio de empresas — EXPOINCO 2027 (Bolivia)", 14, True),
        ("", 11, False),
        (f"Empresas registradas: {len(filas)}", 11, True),
        ("Rubros: urbanizaciones, inmobiliarias, distribuidoras, constructoras,", 11, False),
        ("maquinaria pesada, materiales, herramientas e insumos.", 11, False),
        ("", 11, False),
        ("Fuentes de datos:", 11, True),
        ("1. Directorio comercial curado del proyecto (RubrosDirectory.tsx) —", 11, False),
        ("   empresas reales con sitio web o redes sociales.", 11, False),
        ("2. Investigación web: ranking Nueva Economía (desarrolladores", 11, False),
        ("   inmobiliarios), sitios oficiales y listados públicos.", 11, False),
        ("", 11, False),
        ("Uso y validación:", 11, True),
        ("- Los campos «Por verificar» deben confirmarse en el sitio web de la", 11, False),
        ("  empresa antes de usarlos en campañas.", 11, False),
        ("- Teléfonos guardados como texto para conservar el formato.", 11, False),
        ("- Hoja «Por rubro» y «Por departamento» usan fórmulas en vivo.", 11, False),
        ("- Los datos son de empresas (información pública comercial); tratar", 11, False),
        ("  con fines de prospección B2B de la expo.", 11, False),
    ]
    for i, (texto, tam, negrita) in enumerate(notas, start=1):
        c = leeme.cell(row=i, column=1, value=texto)
        c.font = Font(size=tam, bold=negrita)
    leeme.column_dimensions["A"].width = 90

    # ---------- Empresas ----------
    ws = wb.create_sheet("Empresas")
    columnas = [
        ("N°", 6), ("Empresa", 42), ("Categoría", 20), ("Rubro(s) detalle", 38),
        ("Departamento", 15), ("Ciudad", 15), ("Contacto", 18), ("Teléfono", 16),
        ("WhatsApp", 16), ("Correo", 26), ("Sitio web", 40), ("Redes sociales", 38),
        ("Fuente", 32), ("Verificación", 14),
    ]
    for col, (titulo, ancho) in enumerate(columnas, start=1):
        c = ws.cell(row=1, column=col, value=titulo)
        c.fill, c.font = cabecera_fill, cabecera_font
        c.alignment = Alignment(horizontal="center", vertical="center")
        ws.column_dimensions[get_column_letter(col)].width = ancho

    for i, f in enumerate(filas, start=1):
        fila = i + 1
        valores = [
            i, f["nombre"], f["categoria"], f["rubros"], f["departamento"], f["ciudad"],
            f["contacto"], f["telefono"], f["whatsapp"], f["correo"], f["url"], f["red"],
            f["fuente"], "Pendiente",
        ]
        for col, valor in enumerate(valores, start=1):
            c = ws.cell(row=fila, column=col, value=valor)
            c.border = borde
            c.alignment = Alignment(vertical="top", wrap_text=col in (4, 11, 12, 13))
            # Teléfonos/WhatsApp como texto (regla Excel: conservar formato)
            if col in (8, 9):
                c.number_format = "@"
            if col == 5 and valor == "Por verificar":
                c.fill = amarillo

    ws.freeze_panes = "A2"
    ws.auto_filter.ref = f"A1:{get_column_letter(len(columnas))}{len(filas) + 1}"

    # ---------- Por rubro (fórmulas en vivo) ----------
    wr = wb.create_sheet("Por rubro")
    wr.cell(row=1, column=1, value="Categoría").font = cabecera_font
    wr.cell(row=1, column=1).fill = cabecera_fill
    wr.cell(row=1, column=2, value="Empresas").font = cabecera_font
    wr.cell(row=1, column=2).fill = cabecera_fill
    wr.column_dimensions["A"].width = 28
    wr.column_dimensions["B"].width = 12
    for i, cat in enumerate(CATEGORIAS, start=2):
        wr.cell(row=i, column=1, value=cat)
        wr.cell(row=i, column=2, value=f'=COUNTIF(Empresas!C:C,"{cat}")')
    total = len(CATEGORIAS) + 2
    wr.cell(row=total, column=1, value="TOTAL").font = Font(bold=True)
    wr.cell(row=total, column=2, value=f"=COUNTA(Empresas!B:B)-1").font = Font(bold=True)

    # ---------- Por departamento (fórmulas en vivo) ----------
    wd = wb.create_sheet("Por departamento")
    wd.cell(row=1, column=1, value="Departamento").font = cabecera_font
    wd.cell(row=1, column=1).fill = cabecera_fill
    wd.cell(row=1, column=2, value="Empresas").font = cabecera_font
    wd.cell(row=1, column=2).fill = cabecera_fill
    wd.column_dimensions["A"].width = 22
    wd.column_dimensions["B"].width = 12
    for i, dep in enumerate(DEPARTAMENTOS, start=2):
        wd.cell(row=i, column=1, value=dep)
        wd.cell(row=i, column=2, value=f'=COUNTIF(Empresas!E:E,"{dep}")')
    total = len(DEPARTAMENTOS) + 2
    wd.cell(row=total, column=1, value="TOTAL").font = Font(bold=True)
    wd.cell(row=total, column=2, value="=COUNTA(Empresas!B:B)-1").font = Font(bold=True)

    wb.save(SALIDA)
    print(f"✅ {SALIDA.name} generado: {len(filas)} empresas")


if __name__ == "__main__":
    generar_xlsx(construir_filas())
