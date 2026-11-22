"""Seed del plano del pabellón: crea zonas y stands 1-52 del plano interactivo.

El mapa visual (src/components/InteractivePlano.tsx) identifica cada stand por
su `codigo` ("1".."52"); por eso los stands se crean con esos códigos.

Uso:
    python -m app.db.seed_plano
"""
from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.common import EstadoStand, TipoStand, TipoZona
from app.models.inventario import Stand, Zona

# id del plano → sector (id == codigo del stand en la API)
SECTORES: dict[int, str] = {
    1: "Lateral Este · Sector Norte (Fila 1)",
    2: "Lateral Este · Sector Norte (Fila 2)",
    3: "Lateral Este · Sector Norte (Fila 3)",
    4: "Acceso Norte · Zona Preferencial",
    5: "Acceso Norte · Zona Preferencial",
    6: "Lateral Oeste · Sector Norte (Fila 1)",
    7: "Lateral Oeste · Sector Norte (Fila 2)",
    8: "Lateral Oeste · Sector Norte (Fila 3)",
    9: "Lateral Oeste · Sector Sur (Fila 1)",
    10: "Lateral Oeste · Sector Sur (Fila 2)",
    11: "Lateral Oeste · Sector Sur (Fila 3)",
    12: "Acceso Sur Principal · Ala Oeste",
    13: "Acceso Sur Principal · Ala Este",
    14: "Lateral Este · Sector Sur (Fila 3)",
    15: "Lateral Este · Sector Sur (Fila 2)",
    16: "Lateral Este · Sector Sur (Fila 1)",
    17: "Pabellón Central Sur · Col. Este (Fila 1)",
    18: "Pabellón Central Sur · Col. Este (Fila 2)",
    19: "Pabellón Central Sur · Col. Este (Fila 3)",
    20: "Pabellón Central Sur · Col. Este (Fila 4)",
    21: "Pabellón Central Sur · Col. Este (Fila 5)",
    22: "Pabellón Central Norte · Col. Este (Fila 1)",
    23: "Pabellón Central Norte · Col. Este (Fila 2)",
    24: "Pabellón Central Norte · Col. Este (Fila 3)",
    25: "Pabellón Central Norte · Col. Este (Fila 4)",
    26: "Pabellón Central Sur · Columna 2 (Fila 1)",
    27: "Pabellón Central Sur · Columna 2 (Fila 2)",
    28: "Pabellón Central Sur · Columna 2 (Fila 3)",
    29: "Pabellón Central Sur · Columna 2 (Fila 4)",
    30: "Pabellón Central Sur · Columna 2 (Fila 5)",
    31: "Pabellón Central Norte · Columna 2 (Fila 1)",
    32: "Pabellón Central Norte · Columna 2 (Fila 2)",
    33: "Pabellón Central Norte · Columna 2 (Fila 3)",
    34: "Pabellón Central Norte · Columna 2 (Fila 4)",
    35: "Pabellón Central Sur · Columna 3 (Fila 1)",
    36: "Pabellón Central Sur · Columna 3 (Fila 2)",
    37: "Pabellón Central Sur · Columna 3 (Fila 3)",
    38: "Pabellón Central Sur · Columna 3 (Fila 4)",
    39: "Pabellón Central Sur · Columna 3 (Fila 5)",
    40: "Pabellón Central Norte · Columna 3 (Fila 1)",
    41: "Pabellón Central Norte · Columna 3 (Fila 2)",
    42: "Pabellón Central Norte · Columna 3 (Fila 3)",
    43: "Pabellón Central Norte · Columna 3 (Fila 4)",
    44: "Pabellón Central Sur · Col. Oeste (Fila 1)",
    45: "Pabellón Central Sur · Col. Oeste (Fila 2)",
    46: "Pabellón Central Sur · Col. Oeste (Fila 3)",
    47: "Pabellón Central Sur · Col. Oeste (Fila 4)",
    48: "Pabellón Central Sur · Col. Oeste (Fila 5)",
    49: "Pabellón Central Norte · Col. Oeste (Fila 1)",
    50: "Pabellón Central Norte · Col. Oeste (Fila 2)",
    51: "Pabellón Central Norte · Col. Oeste (Fila 3)",
    52: "Pabellón Central Norte · Col. Oeste (Fila 4)",
}

DIMENSIONES = "3 × 3 m"
SUPERFICIE_M2 = 9
PRECIO_M2 = 98  # misma tarifa que el frontend (PRICE_PER_M2)
TARIFA = SUPERFICIE_M2 * PRECIO_M2


def zona_de_sector(sector: str) -> str:
    """La zona es la primera parte del sector, antes del separador."""
    return sector.split("·")[0].strip()


def seed_plano() -> None:
    db = SessionLocal()
    try:
        # Zonas
        zonas: dict[str, Zona] = {}
        for nombre in sorted({zona_de_sector(s) for s in SECTORES.values()}):
            zona = db.scalar(select(Zona).where(Zona.nombre == nombre))
            if zona is None:
                tipo = TipoZona.interior if nombre.startswith("Pabellón") else TipoZona.exterior
                zona = Zona(nombre=nombre, tipo=tipo, descripcion=f"Zona {nombre}")
                db.add(zona)
                db.flush()
            zonas[nombre] = zona

        # Stands
        creados = 0
        for stand_id, sector in sorted(SECTORES.items()):
            codigo = str(stand_id)
            if db.scalar(select(Stand).where(Stand.codigo == codigo)):
                continue
            db.add(
                Stand(
                    codigo=codigo,
                    zona_id=zonas[zona_de_sector(sector)].id,
                    tipo=TipoStand.stand,
                    dimensiones=DIMENSIONES,
                    precio_base=TARIFA,
                    descripcion=sector,
                    estado=EstadoStand.disponible,
                )
            )
            creados += 1

        db.commit()
        print(f"[seed_plano] {creados} stands creados en {len(zonas)} zonas (tarifa ${TARIFA}/stand)")
    finally:
        db.close()


if __name__ == "__main__":
    seed_plano()
