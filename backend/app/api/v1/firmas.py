"""Firma digital de contratos (Fase 4 — docs/10).

Flujo supervisado:
1. El ejecutivo solicita la firma de un contrato de reserva → se genera un
   token de uso único.
2. El cliente abre el enlace público, revisa los datos y firma.
3. Se registra el firmante, el hash de la firma, la IP y la fecha.

No se almacenan imágenes de firma: se guarda un hash verificable del documento
aceptado, suficiente para trazabilidad del consentimiento.
"""
import hashlib
import secrets
import uuid

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.comercial import FirmaDigital
from app.models.inventario import Stand
from app.models.reserva import Reserva
from app.models.user import Usuario

router = APIRouter(tags=["firmas-digitales"])


class FirmaSolicitudIn(BaseModel):
    firmante_nombre: str = Field(min_length=3, max_length=150)
    firmante_email: str | None = Field(default=None, max_length=255)


class FirmaFirmaIn(BaseModel):
    firmante_nombre: str = Field(min_length=3, max_length=150)
    acepta: bool = True


def _reserva_or_404(reserva_id: uuid.UUID, db: Session) -> Reserva:
    reserva = db.get(Reserva, reserva_id)
    if reserva is None:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")
    return reserva


def _check_permiso(reserva: Reserva, user: Usuario) -> None:
    if user.is_admin:
        return
    if reserva.ejecutivo_id != user.id:
        raise HTTPException(status_code=403, detail="Sin permiso sobre esta reserva")


@router.post("/reservas/{reserva_id}/firmas", status_code=status.HTTP_201_CREATED)
def solicitar_firma(
    reserva_id: uuid.UUID,
    payload: FirmaSolicitudIn,
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
) -> dict:
    reserva = _reserva_or_404(reserva_id, db)
    _check_permiso(reserva, user)

    firma = FirmaDigital(
        reserva_id=reserva.id,
        token=secrets.token_hex(32),
        firmante_nombre=payload.firmante_nombre,
        firmante_email=payload.firmante_email,
    )
    db.add(firma)
    db.commit()
    return {
        "id": str(firma.id),
        "token": firma.token,
        "url_publica": f"/firmar/{firma.token}",
        "estado": firma.estado,
    }


@router.get("/reservas/{reserva_id}/firmas")
def listar_firmas(
    reserva_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
) -> list[dict]:
    reserva = _reserva_or_404(reserva_id, db)
    _check_permiso(reserva, user)
    firmas = db.scalars(
        select(FirmaDigital).where(FirmaDigital.reserva_id == reserva.id)
    ).all()
    return [
        {
            "id": str(f.id),
            "token": f.token,
            "firmante_nombre": f.firmante_nombre,
            "firmante_email": f.firmante_email,
            "estado": f.estado,
            "firmada_at": f.firmada_at.isoformat() if f.firmada_at else None,
        }
        for f in firmas
    ]


def _firma_publica_or_404(token: str, db: Session) -> FirmaDigital:
    firma = db.scalar(select(FirmaDigital).where(FirmaDigital.token == token))
    if firma is None:
        raise HTTPException(status_code=404, detail="Enlace de firma inválido")
    return firma


@router.get("/public/firmas/{token}")
def datos_firma(token: str, db: Session = Depends(get_db)) -> dict:
    """Datos del contrato para la página de firma (sin datos sensibles)."""
    firma = _firma_publica_or_404(token, db)
    reserva = _reserva_or_404(firma.reserva_id, db)
    stand = db.get(Stand, reserva.stand_id)
    return {
        "estado": firma.estado,
        "firmante_nombre": firma.firmante_nombre,
        "reserva": {
            "stand": stand.codigo if stand else "—",
            "estado": reserva.estado.value,
            "monto": float(reserva.monto) if reserva.monto is not None else None,
        },
    }


@router.post("/public/firmas/{token}")
def firmar(
    token: str,
    payload: FirmaFirmaIn,
    request: Request,
    db: Session = Depends(get_db),
) -> dict:
    """El cliente firma el contrato. Registra hash de consentimiento, IP y fecha."""
    firma = _firma_publica_or_404(token, db)
    if firma.estado == "firmada":
        raise HTTPException(status_code=409, detail="El contrato ya fue firmado")
    if not payload.acepta:
        raise HTTPException(status_code=400, detail="Debes aceptar los términos para firmar")

    reserva = _reserva_or_404(firma.reserva_id, db)
    datos = f"{firma.id}|{reserva.id}|{payload.firmante_nombre}|acepta"
    firma.firma_hash = hashlib.sha256(datos.encode("utf-8")).hexdigest()
    firma.firmante_nombre = payload.firmante_nombre
    firma.ip = request.client.host if request.client else None
    firma.estado = "firmada"

    from datetime import datetime, timezone
    firma.firmada_at = datetime.now(timezone.utc)
    db.commit()
    return {"ok": True, "estado": firma.estado, "firmada_at": firma.firmada_at.isoformat()}
