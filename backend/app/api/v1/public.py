"""Endpoints públicos (sin autenticación) para el sitio Astro.

- /public/plano: disponibilidad de stands para el plano interactivo.
- /public/registro: formulario de registro de empresas (docs/02).
"""
import uuid

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.common import (
    EstadoLead,
    EstadoNotificacion,
    PrioridadLead,
    TipoActividad,
    TipoNotificacion,
)
from app.models.comunicaciones import Actividad, Notificacion
from app.models.crm import Contacto, Empresa, Lead
from app.models.inventario import Stand, Zona
from app.schemas.inventario import PlanoOut, StandPlano, ZonaOut
from app.schemas.registro import RegistroPublico, RegistroPublicoOut

router = APIRouter(prefix="/public", tags=["public"])


@router.get("/plano", response_model=PlanoOut)
def plano(db: Session = Depends(get_db)) -> PlanoOut:
    zonas = list(db.scalars(select(Zona).order_by(Zona.nombre)))
    stands = db.execute(
        select(Stand, Zona.nombre).join(Zona, Stand.zona_id == Zona.id).order_by(Stand.codigo)
    ).all()
    return PlanoOut(
        zonas=[ZonaOut.model_validate(z) for z in zonas],
        stands=[
            StandPlano(
                id=s.id,
                codigo=s.codigo,
                tipo=s.tipo,
                estado=s.estado,
                dimensiones=s.dimensiones,
                precio_base=float(s.precio_base) if s.precio_base is not None else None,
                zona_id=s.zona_id,
                zona_nombre=zona_nombre,
            )
            for s, zona_nombre in stands
        ],
    )


def _asignar_ejecutivo(db: Session) -> uuid.UUID | None:
    """Ejecutivo activo con menor carga (mismo criterio que reservas)."""
    from app.api.v1.reservas import _asignar_ejecutivo_disponible

    return _asignar_ejecutivo_disponible(db)


@router.post("/registro", response_model=RegistroPublicoOut, status_code=201)
def registro_empresa(
    payload: RegistroPublico,
    db: Session = Depends(get_db),
) -> RegistroPublicoOut:
    """Registro público de empresa interesada (con o sin solicitud de propuesta).

    - Crea/actualiza la empresa (evita duplicados por razón social).
    - Crea el contacto principal.
    - Crea un lead como oportunidad comercial.
    - Asigna un ejecutivo y lo notifica por panel.
    """
    # Empresa: si ya existe, se actualiza en lugar de duplicar
    empresa = db.scalar(
        select(Empresa).where(
            func.lower(Empresa.razon_social) == payload.razon_social.lower(),
            Empresa.deleted_at.is_(None),
        )
    )
    if empresa is None:
        empresa = Empresa(
            razon_social=payload.razon_social,
            nombre_comercial=payload.nombre_comercial,
            rubro=payload.rubro,
            ciudad=payload.ciudad,
            pais=payload.pais,
            sitio_web=payload.sitio_web,
            estado=EstadoLead.prospecto,
            origen="web",
        )
        db.add(empresa)
        db.flush()
    else:
        for campo in ("nombre_comercial", "rubro", "ciudad", "pais", "sitio_web"):
            if getattr(payload, campo):
                setattr(empresa, campo, getattr(payload, campo))

    # Contacto (evita duplicados por email)
    contacto = None
    if payload.email:
        contacto = db.scalar(select(Contacto).where(Contacto.email == payload.email))
    if contacto is None:
        contacto = Contacto(
            empresa_id=empresa.id,
            nombre=payload.nombre_contacto,
            cargo=payload.cargo_contacto,
            email=payload.email,
            whatsapp=payload.whatsapp,
            telefono=payload.telefono,
        )
        db.add(contacto)
        db.flush()

    # Lead como oportunidad
    ejecutivo_id = empresa.ejecutivo_id or _asignar_ejecutivo(db)
    if empresa.ejecutivo_id is None:
        empresa.ejecutivo_id = ejecutivo_id

    lead = Lead(
        empresa_id=empresa.id,
        contacto_id=contacto.id,
        ejecutivo_id=ejecutivo_id,
        origen="web",
        rubro=payload.rubro,
        interes=payload.mensaje or f"Solicitud pública: {payload.tipo_solicitud}",
        prioridad=PrioridadLead.media,
        estado=EstadoLead.prospecto,
    )
    db.add(lead)
    db.flush()

    db.add(
        Actividad(
            empresa_id=empresa.id,
            lead_id=lead.id,
            tipo=TipoActividad.nota,
            descripcion=f"Registro público ({payload.tipo_solicitud})"
            + (f": {payload.mensaje}" if payload.mensaje else ""),
        )
    )
    if ejecutivo_id:
        db.add(
            Notificacion(
                usuario_id=ejecutivo_id,
                tipo=TipoNotificacion.lead,
                titulo="Nuevo registro desde la web",
                mensaje=f"{empresa.razon_social} se registró ({payload.tipo_solicitud}).",
                estado=EstadoNotificacion.pendiente,
                referencia_id=lead.id,
            )
        )
    db.commit()

    return RegistroPublicoOut(
        mensaje="Registro recibido. Un ejecutivo de ventas se pondrá en contacto contigo.",
    )
