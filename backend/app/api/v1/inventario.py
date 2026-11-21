"""Inventario: zonas, stands y paquetes (CRUD administrativo).

Lectura de disponibilidad para usuarios autenticados;
el plano interactivo público usa /public/plano.
"""
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_admin
from app.db.session import get_db
from app.models.common import EstadoStand, TipoStand, TipoZona
from app.models.inventario import Paquete, Stand, Zona
from app.models.user import Usuario
from app.schemas.inventario import (
    PaqueteCreate,
    PaqueteOut,
    PaqueteUpdate,
    StandCreate,
    StandList,
    StandOut,
    StandUpdate,
    ZonaCreate,
    ZonaOut,
    ZonaUpdate,
)

router = APIRouter(prefix="/inventario", tags=["inventario"])


# ---------- Zonas ----------

@router.get("/zonas", response_model=list[ZonaOut])
def list_zonas(db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)) -> list[Zona]:
    return list(db.scalars(select(Zona).order_by(Zona.nombre)))


@router.post("/zonas", response_model=ZonaOut, status_code=status.HTTP_201_CREATED)
def create_zona(
    payload: ZonaCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
) -> Zona:
    if db.scalar(select(Zona).where(Zona.nombre == payload.nombre)):
        raise HTTPException(status_code=409, detail="La zona ya existe")
    zona = Zona(**payload.model_dump())
    db.add(zona)
    db.commit()
    db.refresh(zona)
    return zona


@router.patch("/zonas/{zona_id}", response_model=ZonaOut)
def update_zona(
    zona_id: uuid.UUID,
    payload: ZonaUpdate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
) -> Zona:
    zona = db.get(Zona, zona_id)
    if zona is None:
        raise HTTPException(status_code=404, detail="Zona no encontrada")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(zona, field, value)
    db.commit()
    db.refresh(zona)
    return zona


# ---------- Stands ----------

@router.get("/stands", response_model=StandList)
def list_stands(
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
    zona_id: uuid.UUID | None = Query(default=None),
    estado: EstadoStand | None = Query(default=None),
    tipo: TipoStand | None = Query(default=None),
    limit: int = Query(default=200, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
) -> StandList:
    query = select(Stand)
    if zona_id:
        query = query.where(Stand.zona_id == zona_id)
    if estado:
        query = query.where(Stand.estado == estado)
    if tipo:
        query = query.where(Stand.tipo == tipo)
    total = db.scalar(select(func.count()).select_from(query.subquery())) or 0
    items = db.scalars(query.order_by(Stand.codigo).limit(limit).offset(offset)).all()
    return StandList(total=total, items=[StandOut.model_validate(s) for s in items])


@router.post("/stands", response_model=StandOut, status_code=status.HTTP_201_CREATED)
def create_stand(
    payload: StandCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
) -> Stand:
    if db.scalar(select(Stand).where(Stand.codigo == payload.codigo)):
        raise HTTPException(status_code=409, detail="El código de stand ya existe")
    if db.get(Zona, payload.zona_id) is None:
        raise HTTPException(status_code=404, detail="Zona no encontrada")
    stand = Stand(**payload.model_dump())
    db.add(stand)
    db.commit()
    db.refresh(stand)
    return stand


@router.patch("/stands/{stand_id}", response_model=StandOut)
def update_stand(
    stand_id: uuid.UUID,
    payload: StandUpdate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
) -> Stand:
    stand = db.get(Stand, stand_id)
    if stand is None:
        raise HTTPException(status_code=404, detail="Stand no encontrado")

    data = payload.model_dump(exclude_unset=True)

    # docs/06: un stand vendido no vuelve a disponible sin autorización del admin
    if data.get("estado") == EstadoStand.disponible and stand.estado == EstadoStand.vendido:
        raise HTTPException(
            status_code=409,
            detail="Un stand vendido no puede volver a disponible sin autorización especial",
        )

    if "codigo" in data and data["codigo"] != stand.codigo:
        if db.scalar(select(Stand).where(Stand.codigo == data["codigo"])):
            raise HTTPException(status_code=409, detail="El código de stand ya existe")

    for field, value in data.items():
        setattr(stand, field, value)
    db.commit()
    db.refresh(stand)
    return stand


@router.delete("/stands/{stand_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_stand(
    stand_id: uuid.UUID,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
) -> None:
    stand = db.get(Stand, stand_id)
    if stand is None:
        raise HTTPException(status_code=404, detail="Stand no encontrado")
    if stand.estado == EstadoStand.vendido:
        raise HTTPException(status_code=409, detail="No se puede eliminar un stand vendido")
    db.delete(stand)
    db.commit()


# ---------- Paquetes ----------

@router.get("/paquetes", response_model=list[PaqueteOut])
def list_paquetes(db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)) -> list[Paquete]:
    return list(db.scalars(select(Paquete).order_by(Paquete.precio.desc())))


@router.post("/paquetes", response_model=PaqueteOut, status_code=status.HTTP_201_CREATED)
def create_paquete(
    payload: PaqueteCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
) -> Paquete:
    if db.scalar(select(Paquete).where(Paquete.nombre == payload.nombre)):
        raise HTTPException(status_code=409, detail="El paquete ya existe")
    paquete = Paquete(**payload.model_dump())
    db.add(paquete)
    db.commit()
    db.refresh(paquete)
    return paquete


@router.patch("/paquetes/{paquete_id}", response_model=PaqueteOut)
def update_paquete(
    paquete_id: uuid.UUID,
    payload: PaqueteUpdate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
) -> Paquete:
    paquete = db.get(Paquete, paquete_id)
    if paquete is None:
        raise HTTPException(status_code=404, detail="Paquete no encontrado")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(paquete, field, value)
    db.commit()
    db.refresh(paquete)
    return paquete


@router.put("/paquetes/{paquete_id}/stands/{stand_id}", response_model=PaqueteOut)
def asociar_stand(
    paquete_id: uuid.UUID,
    stand_id: uuid.UUID,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
) -> Paquete:
    paquete = db.get(Paquete, paquete_id)
    stand = db.get(Stand, stand_id)
    if paquete is None or stand is None:
        raise HTTPException(status_code=404, detail="Paquete o stand no encontrado")
    if stand not in paquete.stands:
        paquete.stands.append(stand)
        db.commit()
    db.refresh(paquete)
    return paquete
