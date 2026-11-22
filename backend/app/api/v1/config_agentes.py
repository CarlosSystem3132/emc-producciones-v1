"""Configuración de agentes de IA (solo administrador).

Permite editar el prompt del sistema y el modo de autonomía de cada agente
(docs/09) desde el panel: Administración → Agentes IA.
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import require_admin
from app.db.session import get_db
from app.models.common import EstadoActivo
from app.models.config_agente import ConfigAgente
from app.models.user import Usuario

router = APIRouter(prefix="/config/agentes", tags=["config-agentes"])

MODOS_VALIDOS = {"automatico", "asistido", "manual"}


class AgenteUpdate(BaseModel):
    prompt_sistema: str | None = Field(default=None, min_length=10, max_length=8000)
    modo_autonomia: str | None = None
    activo: bool | None = None


def _out(c: ConfigAgente) -> dict:
    return {
        "clave": c.clave,
        "nombre": c.nombre,
        "descripcion": c.descripcion,
        "prompt_sistema": c.prompt_sistema,
        "modo_autonomia": c.modo_autonomia,
        "activo": c.activo == EstadoActivo.activo,
    }


@router.get("")
def listar(
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
) -> list[dict]:
    agentes = db.scalars(select(ConfigAgente).order_by(ConfigAgente.clave)).all()
    return [_out(a) for a in agentes]


@router.patch("/{clave}")
def actualizar(
    clave: str,
    payload: AgenteUpdate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
) -> dict:
    agente = db.scalar(select(ConfigAgente).where(ConfigAgente.clave == clave))
    if agente is None:
        raise HTTPException(status_code=404, detail="Agente no encontrado")

    data = payload.model_dump(exclude_unset=True)
    if "modo_autonomia" in data:
        if data["modo_autonomia"] not in MODOS_VALIDOS:
            raise HTTPException(
                status_code=400,
                detail=f"Modo inválido. Usa: {', '.join(sorted(MODOS_VALIDOS))}",
            )
        agente.modo_autonomia = data.pop("modo_autonomia")
    if "activo" in data:
        agente.activo = (
            EstadoActivo.activo if data.pop("activo") else EstadoActivo.inactivo
        )
    for campo, valor in data.items():
        setattr(agente, campo, valor)

    db.commit()
    return _out(agente)
