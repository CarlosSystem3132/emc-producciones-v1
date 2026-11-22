"""Secuencias de seguimiento comercial (Fase 2 — docs/10).

- CRUD de secuencias y sus pasos (admin).
- Inscripción de empresas/contactos (el ejecutivo solo inscribe las suyas).
- Ejecución de pasos vencidos (manual o invocada por n8n).
"""
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_admin
from app.db.session import get_db
from app.models.common import CanalComunicacion
from app.models.crm import Empresa
from app.models.secuencias import Secuencia, SecuenciaInscripcion, SecuenciaPaso
from app.models.user import Usuario
from app.services.secuencias import ejecutar_pendientes

router = APIRouter(prefix="/secuencias", tags=["secuencias"])


class PasoIn(BaseModel):
    orden: int = Field(ge=1, le=50)
    dias_espera: int = Field(ge=0, le=365, default=0)
    plantilla_id: uuid.UUID | None = None
    mensaje: str | None = Field(default=None, max_length=4000)


class SecuenciaIn(BaseModel):
    nombre: str = Field(min_length=3, max_length=150)
    descripcion: str | None = Field(default=None, max_length=1000)
    canal: CanalComunicacion = CanalComunicacion.email
    pasos: list[PasoIn] = Field(default_factory=list)


class SecuenciaUpdate(BaseModel):
    nombre: str | None = Field(default=None, min_length=3, max_length=150)
    descripcion: str | None = None
    estado: str | None = None  # activo | inactivo


class InscripcionIn(BaseModel):
    empresa_id: uuid.UUID
    contacto_id: uuid.UUID | None = None
    lead_id: uuid.UUID | None = None


def _secuencia_or_404(secuencia_id: uuid.UUID, db: Session) -> Secuencia:
    secuencia = db.get(Secuencia, secuencia_id)
    if secuencia is None:
        raise HTTPException(status_code=404, detail="Secuencia no encontrada")
    return secuencia


@router.get("")
def listar(db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)) -> list[dict]:
    secuencias = db.scalars(select(Secuencia).order_by(Secuencia.created_at.desc())).all()
    return [
        {
            "id": str(s.id),
            "nombre": s.nombre,
            "descripcion": s.descripcion,
            "canal": s.canal.value,
            "estado": s.estado.value,
            "pasos": len(s.pasos),
            "inscripciones_activas": sum(1 for i in s.inscripciones if i.estado == "activa"),
            "created_at": s.created_at.isoformat(),
        }
        for s in secuencias
    ]


@router.post("", status_code=status.HTTP_201_CREATED)
def crear(
    payload: SecuenciaIn,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
) -> dict:
    secuencia = Secuencia(
        nombre=payload.nombre,
        descripcion=payload.descripcion,
        canal=payload.canal,
    )
    db.add(secuencia)
    db.flush()
    for paso in payload.pasos:
        db.add(SecuenciaPaso(
            secuencia_id=secuencia.id,
            orden=paso.orden,
            dias_espera=paso.dias_espera,
            plantilla_id=paso.plantilla_id,
            mensaje=paso.mensaje,
        ))
    db.commit()
    return {"id": str(secuencia.id), "nombre": secuencia.nombre, "pasos": len(payload.pasos)}


@router.get("/{secuencia_id}")
def detalle(
    secuencia_id: uuid.UUID,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
) -> dict:
    s = _secuencia_or_404(secuencia_id, db)
    return {
        "id": str(s.id),
        "nombre": s.nombre,
        "descripcion": s.descripcion,
        "canal": s.canal.value,
        "estado": s.estado.value,
        "pasos": [
            {
                "id": str(p.id),
                "orden": p.orden,
                "dias_espera": p.dias_espera,
                "plantilla_id": str(p.plantilla_id) if p.plantilla_id else None,
                "mensaje": p.mensaje,
            }
            for p in sorted(s.pasos, key=lambda p: p.orden)
        ],
    }


@router.patch("/{secuencia_id}")
def actualizar(
    secuencia_id: uuid.UUID,
    payload: SecuenciaUpdate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
) -> dict:
    s = _secuencia_or_404(secuencia_id, db)
    data = payload.model_dump(exclude_unset=True)
    if "estado" in data:
        if data["estado"] not in ("activo", "inactivo"):
            raise HTTPException(status_code=400, detail="Estado inválido")
        from app.models.common import EstadoActivo
        s.estado = EstadoActivo(data.pop("estado"))
    for campo, valor in data.items():
        setattr(s, campo, valor)
    db.commit()
    return {"ok": True}


@router.post("/{secuencia_id}/pasos", status_code=status.HTTP_201_CREATED)
def agregar_paso(
    secuencia_id: uuid.UUID,
    payload: PasoIn,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
) -> dict:
    s = _secuencia_or_404(secuencia_id, db)
    paso = SecuenciaPaso(
        secuencia_id=s.id,
        orden=payload.orden,
        dias_espera=payload.dias_espera,
        plantilla_id=payload.plantilla_id,
        mensaje=payload.mensaje,
    )
    db.add(paso)
    db.commit()
    return {"id": str(paso.id), "orden": paso.orden}


@router.delete("/{secuencia_id}/pasos/{paso_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_paso(
    secuencia_id: uuid.UUID,
    paso_id: uuid.UUID,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
) -> None:
    _secuencia_or_404(secuencia_id, db)
    paso = db.get(SecuenciaPaso, paso_id)
    if paso is None or paso.secuencia_id != secuencia_id:
        raise HTTPException(status_code=404, detail="Paso no encontrado")
    db.delete(paso)
    db.commit()


@router.post("/{secuencia_id}/inscribir", status_code=status.HTTP_201_CREATED)
def inscribir(
    secuencia_id: uuid.UUID,
    payload: InscripcionIn,
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
) -> dict:
    s = _secuencia_or_404(secuencia_id, db)
    empresa = db.get(Empresa, payload.empresa_id)
    if empresa is None or empresa.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
    if not user.is_admin and empresa.ejecutivo_id != user.id and empresa.creado_por != user.id:
        raise HTTPException(status_code=403, detail="Sin permiso sobre esta empresa")

    existe = db.scalar(
        select(SecuenciaInscripcion).where(
            SecuenciaInscripcion.secuencia_id == s.id,
            SecuenciaInscripcion.empresa_id == empresa.id,
            SecuenciaInscripcion.estado == "activa",
        )
    )
    if existe is not None:
        raise HTTPException(status_code=409, detail="La empresa ya está inscrita en esta secuencia")

    inscripcion = SecuenciaInscripcion(
        secuencia_id=s.id,
        empresa_id=empresa.id,
        contacto_id=payload.contacto_id,
        lead_id=payload.lead_id,
        proxima_ejecucion=datetime.now(timezone.utc),
    )
    db.add(inscripcion)
    db.commit()
    return {"id": str(inscripcion.id), "estado": inscripcion.estado}


@router.post("/ejecutar-pendientes")
def ejecutar(_: Usuario = Depends(require_admin)) -> dict:
    """Ejecuta los pasos vencidos de todas las secuencias (docs/10)."""
    from app.db.session import SessionLocal

    db = SessionLocal()
    try:
        return ejecutar_pendientes(db)
    finally:
        db.close()


@router.get("/inscripciones/listado")
def listar_inscripciones(
    secuencia_id: uuid.UUID | None = Query(default=None),
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
) -> list[dict]:
    query = select(SecuenciaInscripcion).order_by(SecuenciaInscripcion.proxima_ejecucion)
    if secuencia_id:
        query = query.where(SecuenciaInscripcion.secuencia_id == secuencia_id)
    inscripciones = db.scalars(query).all()
    resultado = []
    for i in inscripciones:
        empresa = db.get(Empresa, i.empresa_id)
        if not user.is_admin and empresa is not None and empresa.ejecutivo_id != user.id:
            continue
        resultado.append({
            "id": str(i.id),
            "secuencia_id": str(i.secuencia_id),
            "empresa": empresa.razon_social if empresa else "—",
            "paso_actual": i.paso_actual,
            "proxima_ejecucion": i.proxima_ejecucion.isoformat(),
            "estado": i.estado,
        })
    return resultado
