"""Integración con facturación (Fase 4 — docs/10).

Registro y emisión de facturas asociadas a una reserva/venta. Al emitir se
despacha el evento a n8n para integrarlo con el sistema contable.
"""
import uuid
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_admin
from app.db.session import get_db
from app.models.comercial import Factura
from app.models.reserva import Reserva
from app.models.user import Usuario
from app.services.comunicaciones import despachar_n8n

router = APIRouter(prefix="/facturas", tags=["facturas"])


class FacturaIn(BaseModel):
    reserva_id: uuid.UUID | None = None
    numero: str | None = Field(default=None, max_length=50)
    nit: str | None = Field(default=None, max_length=50)
    razon_social: str | None = Field(default=None, max_length=255)
    monto: float | None = Field(default=None, gt=0)
    notas: str | None = Field(default=None, max_length=1000)


def _factura_or_404(factura_id: uuid.UUID, db: Session) -> Factura:
    factura = db.get(Factura, factura_id)
    if factura is None:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    return factura


def _siguiente_numero(db: Session) -> str:
    total = db.scalar(select(func.count()).select_from(Factura)) or 0
    return f"F-{total + 1:05d}"


@router.post("", status_code=status.HTTP_201_CREATED)
def crear(
    payload: FacturaIn,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
) -> dict:
    reserva = None
    if payload.reserva_id is not None:
        reserva = db.get(Reserva, payload.reserva_id)
        if reserva is None:
            raise HTTPException(status_code=404, detail="Reserva no encontrada")

    numero = payload.numero or _siguiente_numero(db)
    if db.scalar(select(Factura).where(Factura.numero == numero)):
        raise HTTPException(status_code=409, detail="El número de factura ya existe")

    monto = payload.monto
    if monto is None and reserva is not None and reserva.monto is not None:
        monto = float(reserva.monto)
    if monto is None:
        raise HTTPException(status_code=400, detail="Indica el monto de la factura")

    factura = Factura(
        reserva_id=payload.reserva_id,
        empresa_id=reserva.empresa_id if reserva else None,
        numero=numero,
        nit=payload.nit,
        razon_social=payload.razon_social,
        monto=Decimal(str(monto)),
        notas=payload.notas,
    )
    db.add(factura)
    db.commit()
    return {"id": str(factura.id), "numero": factura.numero, "estado": factura.estado}


@router.get("")
def listar(db: Session = Depends(get_db), _: Usuario = Depends(require_admin)) -> list[dict]:
    facturas = db.scalars(select(Factura).order_by(Factura.created_at.desc()).limit(200)).all()
    return [_factura_out(f) for f in facturas]


@router.post("/{factura_id}/emitir")
def emitir(
    factura_id: uuid.UUID,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
) -> dict:
    factura = _factura_or_404(factura_id, db)
    if factura.estado != "borrador":
        raise HTTPException(status_code=409, detail=f"La factura está en estado {factura.estado}")
    factura.estado = "emitida"
    db.commit()

    # Notifica al sistema contable vía n8n (si está configurado)
    despachar_n8n(
        "factura.emitida",
        {
            "numero": factura.numero,
            "nit": factura.nit,
            "razon_social": factura.razon_social,
            "monto": float(factura.monto),
        },
    )
    return {"ok": True, "estado": factura.estado}


@router.post("/{factura_id}/anular")
def anular(
    factura_id: uuid.UUID,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
) -> dict:
    factura = _factura_or_404(factura_id, db)
    if factura.estado == "anulada":
        raise HTTPException(status_code=409, detail="La factura ya está anulada")
    factura.estado = "anulada"
    db.commit()
    return {"ok": True, "estado": factura.estado}


def _factura_out(f: Factura) -> dict:
    return {
        "id": str(f.id),
        "reserva_id": str(f.reserva_id) if f.reserva_id else None,
        "numero": f.numero,
        "nit": f.nit,
        "razon_social": f.razon_social,
        "monto": float(f.monto),
        "estado": f.estado,
        "created_at": f.created_at.isoformat(),
    }
