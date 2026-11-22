"""Plantillas con variables {{variable}} (Fase 2).

- CRUD de plantillas (admin crea/edita; ejecutivo puede usarlas).
- Creación desde PDF: se extrae el texto del documento para editarlo/crear
  la plantilla sin escribir código (pensado en usuarios no técnicos).
- Renderizado/preview con variables.
- Envío directo a una empresa/contacto con control de frecuencia.
"""
import io
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_admin
from app.db.session import get_db
from app.models.comunicaciones import Plantilla
from app.models.crm import Contacto, Empresa
from app.models.user import Usuario
from app.schemas.comunicacion import (
    EnviarComunicacion,
    PlantillaCreate,
    PlantillaOut,
    PlantillaUpdate,
    RenderOut,
    RenderRequest,
)
from app.services.comunicaciones import (
    registrar_envio,
    renderizar,
    variables_disponibles,
)

router = APIRouter(prefix="/plantillas", tags=["plantillas"])


def _get_plantilla_or_404(plantilla_id: uuid.UUID, db: Session) -> Plantilla:
    plantilla = db.get(Plantilla, plantilla_id)
    if plantilla is None:
        raise HTTPException(status_code=404, detail="Plantilla no encontrada")
    return plantilla


@router.post("/extraer-pdf")
async def extraer_pdf(
    archivo: UploadFile = File(...),
    _: Usuario = Depends(require_admin),
) -> dict:
    """Extrae el texto de un PDF para crear una plantilla sin escribir contenido
    a mano. El texto se devuelve para que el administrador lo revise y ajuste
    las variables {{...}} antes de guardar (usuario no técnico)."""
    if not (archivo.filename or "").lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="El archivo debe ser un PDF")

    contenido = await archivo.read()
    if len(contenido) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="El PDF no puede superar 10 MB")
    if not contenido:
        raise HTTPException(status_code=400, detail="El archivo está vacío")

    try:
        from pypdf import PdfReader

        reader = PdfReader(io.BytesIO(contenido))
        paginas = len(reader.pages)
        texto = "\n".join((pagina.extract_text() or "") for pagina in reader.pages[:30]).strip()
    except Exception:
        raise HTTPException(
            status_code=422,
            detail="No se pudo leer el PDF. Intenta con otro archivo (no escaneado).",
        )

    if not texto:
        raise HTTPException(
            status_code=422,
            detail="El PDF no contiene texto extraíble. Si es una imagen, escribe el contenido manualmente.",
        )

    return {
        "texto": texto,
        "paginas": paginas,
        "nombre_sugerido": (archivo.filename or "Plantilla").rsplit(".", 1)[0][:150],
    }


@router.get("", response_model=list[PlantillaOut])
def list_plantillas(
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
) -> list[Plantilla]:
    return list(db.scalars(select(Plantilla).order_by(Plantilla.nombre)))


@router.post("", response_model=PlantillaOut, status_code=status.HTTP_201_CREATED)
def create_plantilla(
    payload: PlantillaCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
) -> Plantilla:
    plantilla = Plantilla(**payload.model_dump())
    db.add(plantilla)
    db.commit()
    db.refresh(plantilla)
    return plantilla


@router.get("/{plantilla_id}", response_model=PlantillaOut)
def get_plantilla(
    plantilla_id: uuid.UUID,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
) -> Plantilla:
    return _get_plantilla_or_404(plantilla_id, db)


@router.patch("/{plantilla_id}", response_model=PlantillaOut)
def update_plantilla(
    plantilla_id: uuid.UUID,
    payload: PlantillaUpdate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
) -> Plantilla:
    plantilla = _get_plantilla_or_404(plantilla_id, db)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(plantilla, field, value)
    db.commit()
    db.refresh(plantilla)
    return plantilla


@router.post("/{plantilla_id}/render", response_model=RenderOut)
def render_plantilla(
    plantilla_id: uuid.UUID,
    payload: RenderRequest,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
) -> RenderOut:
    """Preview del contenido con variables sustituidas."""
    plantilla = _get_plantilla_or_404(plantilla_id, db)
    contenido, faltantes = renderizar(plantilla.contenido, payload.variables)
    return RenderOut(contenido=contenido, variables_faltantes=faltantes)


@router.post("/{plantilla_id}/enviar")
def enviar_plantilla(
    plantilla_id: uuid.UUID,
    payload: EnviarComunicacion,
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
) -> dict:
    """Envía la plantilla renderizada a una empresa/contacto.

    - Completa variables estándar (empresa, contacto, cargo…).
    - Previene duplicados y controla frecuencia (docs/10).
    - Despacha a n8n (Gmail/WhatsApp) y registra la comunicación.
    """
    plantilla = _get_plantilla_or_404(plantilla_id, db)
    empresa = db.get(Empresa, payload.empresa_id)
    if empresa is None or empresa.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")

    contacto = None
    if payload.contacto_id:
        contacto = db.get(Contacto, payload.contacto_id)
        if contacto is None or contacto.empresa_id != empresa.id:
            raise HTTPException(status_code=404, detail="Contacto no encontrado")
    elif empresa.contactos:
        contacto = empresa.contactos[0]

    variables = variables_disponibles(empresa, contacto)
    variables.update(payload.variables_extra)
    contenido, faltantes = renderizar(plantilla.contenido, variables)

    canal = payload.canal or plantilla.canal
    comunicacion, motivo = registrar_envio(
        db,
        empresa=empresa,
        contacto=contacto,
        plantilla=plantilla,
        canal=canal,
        contenido_renderizado=contenido,
        agente=user.email,
    )
    if motivo:
        raise HTTPException(status_code=409, detail=motivo)

    db.commit()
    return {
        "comunicacion_id": str(comunicacion.id),
        "estado": comunicacion.estado.value,
        "contenido": contenido,
        "variables_faltantes": faltantes,
    }
