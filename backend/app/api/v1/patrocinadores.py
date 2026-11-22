"""Panel de patrocinadores (Fase 4 — docs/10).

- Gestión de patrocinadores (admin): alta, edición, baja lógica y orden.
- Listado público de patrocinadores activos (para la web).
"""
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_admin
from app.db.session import get_db
from app.models.common import EstadoActivo
from app.models.patrocinadores import Patrocinador
from app.models.user import Usuario

router = APIRouter(tags=["patrocinadores"])

CATEGORIAS = {"oro", "plata", "bronce", "aliado"}


class PatrocinadorIn(BaseModel):
    nombre: str = Field(min_length=2, max_length=150)
    categoria: str | None = Field(default="aliado", max_length=50)
    logo_url: str | None = Field(default=None, max_length=500)
    sitio_web: str | None = Field(default=None, max_length=255)
    orden: int = Field(default=0, ge=0, le=999)


class PatrocinadorUpdate(BaseModel):
    nombre: str | None = Field(default=None, min_length=2, max_length=150)
    categoria: str | None = None
    logo_url: str | None = None
    sitio_web: str | None = None
    orden: int | None = Field(default=None, ge=0, le=999)
    estado: str | None = None  # activo | inactivo


def _or_404(patrocinador_id: uuid.UUID, db: Session) -> Patrocinador:
    p = db.get(Patrocinador, patrocinador_id)
    if p is None:
        raise HTTPException(status_code=404, detail="Patrocinador no encontrado")
    return p


def _out(p: Patrocinador) -> dict:
    return {
        "id": str(p.id),
        "nombre": p.nombre,
        "categoria": p.categoria,
        "logo_url": p.logo_url,
        "sitio_web": p.sitio_web,
        "estado": p.estado.value,
        "orden": p.orden,
    }


@router.get("/patrocinadores")
def listar(
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
) -> list[dict]:
    patrocinadores = db.scalars(
        select(Patrocinador).order_by(Patrocinador.orden, Patrocinador.nombre)
    ).all()
    return [_out(p) for p in patrocinadores]


@router.post("/patrocinadores", status_code=status.HTTP_201_CREATED)
def crear(
    payload: PatrocinadorIn,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
) -> dict:
    if payload.categoria and payload.categoria not in CATEGORIAS:
        raise HTTPException(status_code=400, detail=f"Categoría inválida. Usa: {', '.join(sorted(CATEGORIAS))}")
    p = Patrocinador(**payload.model_dump())
    db.add(p)
    db.commit()
    return _out(p)


@router.patch("/patrocinadores/{patrocinador_id}")
def actualizar(
    patrocinador_id: uuid.UUID,
    payload: PatrocinadorUpdate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
) -> dict:
    p = _or_404(patrocinador_id, db)
    data = payload.model_dump(exclude_unset=True)
    if "categoria" in data and data["categoria"] is not None and data["categoria"] not in CATEGORIAS:
        raise HTTPException(status_code=400, detail="Categoría inválida")
    if "estado" in data and data["estado"] is not None:
        p.estado = EstadoActivo(data.pop("estado"))
    for campo, valor in data.items():
        setattr(p, campo, valor)
    db.commit()
    return _out(p)


@router.delete("/patrocinadores/{patrocinador_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar(
    patrocinador_id: uuid.UUID,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
) -> None:
    p = _or_404(patrocinador_id, db)
    db.delete(p)
    db.commit()


@router.get("/public/patrocinadores")
def publico(db: Session = Depends(get_db)) -> list[dict]:
    """Patrocinadores activos para la web pública."""
    patrocinadores = db.scalars(
        select(Patrocinador)
        .where(Patrocinador.estado == EstadoActivo.activo)
        .order_by(Patrocinador.orden, Patrocinador.nombre)
    ).all()
    return [
        {"nombre": p.nombre, "categoria": p.categoria, "logo_url": p.logo_url, "sitio_web": p.sitio_web}
        for p in patrocinadores
    ]
