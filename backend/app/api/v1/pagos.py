"""Integración con pagos (Fase 4 — docs/10).

Registro de pagos contra reservas: método, referencia, confirmación y anulación.
El pago confirmado no cambia el estado de la reserva por sí solo: la venta se
confirma con /reservas/{id}/vender (docs/06).
"""
import uuid
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_admin
from app.db.session import get_db
from app.models.comercial import Pago
from app.models.reserva import Reserva
from app.models.user import Usuario

router = APIRouter(tags=["pagos"])

METODOS = {"efectivo", "transferencia", "qr", "tarjeta", "otro"}


class PagoIn(BaseModel):
    monto: float = Field(gt=0, le=10_000_000)
    metodo: str = Field(default="efectivo", max_length=30)
    referencia: str | None = Field(default=None, max_length=120)
    notas: str | None = Field(default=None, max_length=1000)


def _reserva_or_404(reserva_id: uuid.UUID, db: Session) -> Reserva:
    reserva = db.get(Reserva, reserva_id)
    if reserva is None:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")
    return reserva


def _check_reserva_permiso(reserva: Reserva, user: Usuario) -> None:
    if user.is_admin:
        return
    if reserva.ejecutivo_id != user.id:
        raise HTTPException(status_code=403, detail="Sin permiso sobre esta reserva")


@router.post("/reservas/{reserva_id}/pagos", status_code=status.HTTP_201_CREATED)
def registrar_pago(
    reserva_id: uuid.UUID,
    payload: PagoIn,
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
) -> dict:
    reserva = _reserva_or_404(reserva_id, db)
    _check_reserva_permiso(reserva, user)

    if payload.metodo not in METODOS:
        raise HTTPException(status_code=400, detail=f"Método inválido. Usa: {', '.join(sorted(METODOS))}")

    pago = Pago(
        reserva_id=reserva.id,
        empresa_id=reserva.empresa_id,
        monto=Decimal(str(payload.monto)),
        metodo=payload.metodo,
        referencia=payload.referencia,
        notas=payload.notas,
        registrado_por=user.id,
    )
    db.add(pago)
    db.commit()
    return {"id": str(pago.id), "estado": pago.estado, "monto": float(pago.monto)}


@router.get("/reservas/{reserva_id}/pagos")
def pagos_de_reserva(
    reserva_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
) -> list[dict]:
    reserva = _reserva_or_404(reserva_id, db)
    _check_reserva_permiso(reserva, user)
    pagos = db.scalars(
        select(Pago).where(Pago.reserva_id == reserva.id).order_by(Pago.created_at.desc())
    ).all()
    return [_pago_out(p) for p in pagos]


@router.get("/pagos")
def listar_pagos(
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
) -> list[dict]:
    pagos = db.scalars(select(Pago).order_by(Pago.created_at.desc()).limit(200)).all()
    return [_pago_out(p) for p in pagos]


@router.post("/pagos/{pago_id}/confirmar")
def confirmar_pago(
    pago_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
) -> dict:
    pago = db.get(Pago, pago_id)
    if pago is None:
        raise HTTPException(status_code=404, detail="Pago no encontrado")
    reserva = db.get(Reserva, pago.reserva_id)
    _check_reserva_permiso(reserva, user)
    if pago.estado != "pendiente":
        raise HTTPException(status_code=409, detail=f"El pago está en estado {pago.estado}")
    pago.estado = "confirmado"
    db.commit()
    return {"ok": True, "estado": pago.estado}


@router.post("/pagos/{pago_id}/anular")
def anular_pago(
    pago_id: uuid.UUID,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
) -> dict:
    pago = db.get(Pago, pago_id)
    if pago is None:
        raise HTTPException(status_code=404, detail="Pago no encontrado")
    if pago.estado == "anulado":
        raise HTTPException(status_code=409, detail="El pago ya está anulado")
    pago.estado = "anulado"
    db.commit()
    return {"ok": True, "estado": pago.estado}


def _pago_out(p: Pago) -> dict:
    return {
        "id": str(p.id),
        "reserva_id": str(p.reserva_id),
        "empresa_id": str(p.empresa_id) if p.empresa_id else None,
        "monto": float(p.monto),
        "metodo": p.metodo,
        "referencia": p.referencia,
        "estado": p.estado,
        "notas": p.notas,
        "created_at": p.created_at.isoformat(),
    }
