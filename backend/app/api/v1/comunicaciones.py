"""Registro de comunicaciones (Fase 2) y propuestas PDF.

- Historial de comunicaciones con filtros.
- Generación de propuestas PDF desde plantillas (docs/10).
"""
import io
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.common import CanalComunicacion, EstadoComunicacion, TipoDocumento
from app.models.comunicaciones import Comunicacion, Documento, Plantilla
from app.models.crm import Contacto, Empresa
from app.models.user import Usuario
from app.schemas.comunicacion import ComunicacionList, ComunicacionOut
from app.services.comunicaciones import renderizar, variables_disponibles

router = APIRouter(tags=["comunicaciones"])


@router.get("/comunicaciones", response_model=ComunicacionList)
def list_comunicaciones(
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
    canal: CanalComunicacion | None = Query(default=None),
    estado: EstadoComunicacion | None = Query(default=None),
    empresa_id: uuid.UUID | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> ComunicacionList:
    query = select(Comunicacion)
    if not user.is_admin:
        query = query.join(Empresa, Comunicacion.empresa_id == Empresa.id).where(
            Empresa.ejecutivo_id == user.id
        )
    if canal:
        query = query.where(Comunicacion.canal == canal)
    if estado:
        query = query.where(Comunicacion.estado == estado)
    if empresa_id:
        query = query.where(Comunicacion.empresa_id == empresa_id)

    total = db.scalar(select(func.count()).select_from(query.subquery())) or 0
    items = db.scalars(
        query.order_by(Comunicacion.created_at.desc()).limit(limit).offset(offset)
    ).all()
    return ComunicacionList(
        total=total, items=[ComunicacionOut.model_validate(c) for c in items]
    )


@router.post("/propuestas/pdf")
def generar_propuesta_pdf(
    payload: dict,
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
) -> StreamingResponse:
    """Genera una propuesta comercial en PDF a partir de una plantilla.

    Body: { empresa_id, plantilla_id, contacto_id?, variables_extra? }
    """
    try:
        empresa_id = uuid.UUID(payload["empresa_id"])
        plantilla_id = uuid.UUID(payload["plantilla_id"])
    except (KeyError, ValueError):
        raise HTTPException(status_code=400, detail="Faltan empresa_id o plantilla_id")

    empresa = db.get(Empresa, empresa_id)
    if empresa is None or empresa.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
    if not user.is_admin and empresa.ejecutivo_id != user.id and empresa.creado_por != user.id:
        raise HTTPException(status_code=403, detail="Sin permiso sobre esta empresa")

    plantilla = db.get(Plantilla, plantilla_id)
    if plantilla is None:
        raise HTTPException(status_code=404, detail="Plantilla no encontrada")

    contacto = None
    contacto_id = payload.get("contacto_id")
    if contacto_id:
        contacto = db.get(Contacto, uuid.UUID(contacto_id))
    elif empresa.contactos:
        contacto = empresa.contactos[0]

    variables = variables_disponibles(empresa, contacto)
    # Datos del ejecutivo asignado (Agente 3, docs/09)
    if empresa.ejecutivo is not None:
        variables.update({
            "ejecutivo": empresa.ejecutivo.nombre_completo,
            "ejecutivo_cargo": empresa.ejecutivo.cargo or "",
            "ejecutivo_email": empresa.ejecutivo.correo_contacto or empresa.ejecutivo.email,
            "ejecutivo_whatsapp": empresa.ejecutivo.whatsapp or "",
        })
    variables.update(payload.get("variables_extra") or {})
    contenido, _ = renderizar(plantilla.contenido, variables)

    pdf = _crear_pdf(empresa, plantilla.nombre, contenido, empresa.ejecutivo)

    db.add(
        Documento(
            empresa_id=empresa.id,
            tipo=TipoDocumento.propuesta,
            nombre=f"Propuesta {empresa.razon_social} — {plantilla.nombre}",
            url="generado://propuesta.pdf",
        )
    )
    db.commit()

    nombre_archivo = f"propuesta-{empresa.razon_social[:30].replace(' ', '_')}.pdf"
    return StreamingResponse(
        io.BytesIO(pdf),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{nombre_archivo}"'},
    )


def _crear_pdf(empresa: Empresa, nombre_plantilla: str, contenido: str, ejecutivo=None) -> bytes:
    """Propuesta PDF con membrete de EMC Producciones (reportlab)."""
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.units import cm
    from reportlab.pdfgen import canvas as canvas_mod

    buffer = io.BytesIO()
    c = canvas_mod.Canvas(buffer, pagesize=letter)
    ancho, alto = letter

    # Membrete
    c.setFillColorRGB(0.7, 0.25, 0.16)
    c.rect(0, alto - 3 * cm, ancho, 3 * cm, stroke=0, fill=1)
    c.setFillColorRGB(1, 1, 1)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(2 * cm, alto - 1.8 * cm, "EMC PRODUCCIONES")
    c.setFont("Helvetica", 10)
    c.drawString(2 * cm, alto - 2.5 * cm, "EXPOINCO 2027 · Expoinmobiliaria y Construcción Internacional")

    # Cuerpo
    c.setFillColorRGB(0, 0, 0)
    y = alto - 4.5 * cm
    c.setFont("Helvetica-Bold", 13)
    c.drawString(2 * cm, y, f"Propuesta comercial: {nombre_plantilla}")
    y -= 1.0 * cm
    c.setFont("Helvetica", 11)
    c.drawString(2 * cm, y, f"Para: {empresa.razon_social}")
    if empresa.ciudad:
        y -= 0.6 * cm
        c.drawString(2 * cm, y, f"Ciudad: {empresa.ciudad}")

    y -= 1.2 * cm
    c.setFont("Helvetica", 11)
    for linea in contenido.splitlines():
        if y < 3 * cm:
            c.showPage()
            y = alto - 2.5 * cm
            c.setFont("Helvetica", 11)
        # Salto de línea simple por longitud
        while len(linea) > 95:
            c.drawString(2 * cm, y, linea[:95])
            linea = linea[95:]
            y -= 0.55 * cm
            if y < 3 * cm:
                c.showPage()
                y = alto - 2.5 * cm
                c.setFont("Helvetica", 11)
        c.drawString(2 * cm, y, linea)
        y -= 0.55 * cm

    # Pie con datos del ejecutivo asignado (Agente 3, docs/09)
    c.setFont("Helvetica-Oblique", 8)
    c.setFillColorRGB(0.4, 0.4, 0.4)
    if ejecutivo is not None:
        c.setFont("Helvetica", 9)
        c.setFillColorRGB(0.2, 0.2, 0.2)
        c.drawString(2 * cm, 2.6 * cm, f"Atentamente: {ejecutivo.nombre_completo} — {ejecutivo.cargo or 'Ejecutivo de ventas'}")
        contacto_linea = " · ".join(
            x for x in [
                ejecutivo.correo_contacto or ejecutivo.email,
                f"WhatsApp {ejecutivo.whatsapp}" if ejecutivo.whatsapp else None,
            ] if x
        )
        if contacto_linea:
            c.drawString(2 * cm, 2.25 * cm, contacto_linea)
        c.setFont("Helvetica-Oblique", 8)
        c.setFillColorRGB(0.4, 0.4, 0.4)
    c.drawString(2 * cm, 1.8 * cm, "Documento generado automáticamente por el sistema comercial de EMC Producciones.")
    c.drawString(2 * cm, 1.3 * cm, "www.expoinmobiliariayconstruccion.com")

    c.save()
    return buffer.getvalue()
