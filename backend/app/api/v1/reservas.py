"""Reservas y bloqueos temporales de stands (docs/06-reglas-de-reserva.md).

Flujo web:
1. La empresa selecciona un stand "Disponible" y envía sus datos.
2. Se crea/actualiza empresa + contacto + lead (oportunidad).
3. Se asigna un ejecutivo automáticamente.
4. El stand pasa a "Bloqueado temporal" por 30 minutos.

Reglas:
- Un stand no puede tener más de una reserva activa.
- El ejecutivo confirma ("Reservado" detiene el conteo), vende ("Vendido")
  o extiende UNA vez por 30 o 60 minutos (con motivo).
- Si expiran los 30 minutos, el stand vuelve a "Disponible" y la
  oportunidad permanece registrada para seguimiento.
- Cada cambio de estado queda auditado en `actividades`.
"""
import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_admin
from app.db.session import get_db
from app.models.common import (
    EstadoLead,
    EstadoReserva,
    EstadoStand,
    EstadoUsuario,
    RolUsuario,
    TipoActividad,
    TipoNotificacion,
)
from app.models.comunicaciones import Actividad
from app.models.crm import Contacto, Empresa, Lead
from app.models.inventario import Stand
from app.models.reserva import Reserva
from app.models.user import Usuario
from app.schemas.reserva import (
    ReservaExtendRequest,
    ReservaList,
    ReservaOut,
    ReservaVenderRequest,
    SolicitudReserva,
)

router = APIRouter(prefix="/reservas", tags=["reservas"])

DURACION_BLOQUEO_MIN = 30  # docs/06


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _auditar(
    db: Session,
    reserva: Reserva,
    usuario_id: uuid.UUID | None,
    descripcion: str,
) -> None:
    db.add(
        Actividad(
            empresa_id=reserva.empresa_id,
            lead_id=reserva.lead_id,
            usuario_id=usuario_id,
            tipo=TipoActividad.cambio_estado,
            descripcion=descripcion,
        )
    )


def _notificar(
    db: Session,
    usuario_id: uuid.UUID,
    titulo: str,
    mensaje: str,
    reserva_id: uuid.UUID,
) -> None:
    """Notifica al usuario por panel + WhatsApp + correo (docs/08), usando los
    datos de contacto registrados al crear al ejecutivo."""
    from app.services.notificaciones import notificar as _notificar_multicanal

    _notificar_multicanal(
        db,
        usuario_id,
        TipoNotificacion.reserva,
        titulo,
        mensaje,
        referencia_id=reserva_id,
    )


def liberar_expiradas(db: Session) -> int:
    """Libera bloqueos expirados. Se ejecuta también si el usuario cierra el
    navegador: la expiración es por marca de tiempo en el servidor."""
    expiradas = db.scalars(
        select(Reserva).where(
            Reserva.estado == EstadoReserva.bloqueado,
            Reserva.fecha_expiracion < _utcnow(),
        )
    ).all()
    for reserva in expiradas:
        reserva.estado = EstadoReserva.expirado
        stand = db.get(Stand, reserva.stand_id)
        if stand is not None and stand.estado == EstadoStand.bloqueado_temporal:
            stand.estado = EstadoStand.disponible
            stand.reserva_activa_id = None
        if reserva.lead_id:
            lead = db.get(Lead, reserva.lead_id)
            if lead is not None and lead.estado == EstadoLead.reserva_temporal:
                lead.estado = EstadoLead.interesado  # queda para seguimiento
        _auditar(db, reserva, None, "Reserva expirada automáticamente (30 min)")
        if reserva.ejecutivo_id:
            _notificar(
                db,
                reserva.ejecutivo_id,
                "Reserva expirada",
                f"El bloqueo del stand {stand.codigo if stand else ''} expiró.",
                reserva.id,
            )
    if expiradas:
        db.commit()
    return len(expiradas)


def _asignar_ejecutivo_disponible(db: Session) -> uuid.UUID | None:
    """Asigna el ejecutivo activo con menor carga de leads abiertos."""
    subq = (
        select(Lead.ejecutivo_id, func.count().label("carga"))
        .where(Lead.deleted_at.is_(None), Lead.estado.notin_([EstadoLead.vendido, EstadoLead.descartado]))
        .group_by(Lead.ejecutivo_id)
        .subquery()
    )
    row = db.execute(
        select(Usuario, func.coalesce(subq.c.carga, 0))
        .outerjoin(subq, Usuario.id == subq.c.ejecutivo_id)
        .where(
            Usuario.rol == RolUsuario.ejecutivo,
            Usuario.estado == EstadoUsuario.activo,
            Usuario.deleted_at.is_(None),
        )
        .order_by(func.coalesce(subq.c.carga, 0))
        .limit(1)
    ).first()
    return row[0].id if row else None


def _get_reserva_or_404(reserva_id: uuid.UUID, db: Session, user: Usuario) -> Reserva:
    reserva = db.get(Reserva, reserva_id)
    if reserva is None:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")
    if not user.is_admin and reserva.ejecutivo_id != user.id:
        raise HTTPException(status_code=403, detail="Sin permiso sobre esta reserva")
    return reserva


@router.post("/solicitar", response_model=ReservaOut, status_code=status.HTTP_201_CREATED)
def solicitar_reserva(
    payload: SolicitudReserva,
    db: Session = Depends(get_db),
) -> Reserva:
    """Reserva web pública (paso 1-9 del flujo de docs/06)."""
    liberar_expiradas(db)

    stand = db.get(Stand, payload.stand_id)
    if stand is None:
        raise HTTPException(status_code=404, detail="Stand no encontrado")
    if stand.estado != EstadoStand.disponible:
        raise HTTPException(
            status_code=409,
            detail=f"El stand no está disponible (estado: {stand.estado.value})",
        )

    # 1. Empresa: crear o actualizar (evita duplicados por razón social)
    empresa = db.scalar(
        select(Empresa).where(
            func.lower(Empresa.razon_social) == payload.empresa.razon_social.lower(),
            Empresa.deleted_at.is_(None),
        )
    )
    if empresa is None:
        empresa = Empresa(**payload.empresa.model_dump(), creado_por=None)
        db.add(empresa)
        db.flush()
    else:
        for field, value in payload.empresa.model_dump(exclude_unset=True).items():
            setattr(empresa, field, value)

    # 2. Contacto
    contacto = None
    if payload.contacto.email:
        contacto = db.scalar(select(Contacto).where(Contacto.email == payload.contacto.email))
    if contacto is None:
        contacto = Contacto(**payload.contacto.model_dump(), empresa_id=empresa.id)
        db.add(contacto)
        db.flush()

    # 3. Lead (oportunidad) + 4. Asignación de ejecutivo
    ejecutivo_id = empresa.ejecutivo_id or _asignar_ejecutivo_disponible(db)
    if ejecutivo_id is None:
        # docs/09: sin ejecutivo disponible → escalar al administrador
        from app.models.common import EstadoUsuario as _EU
        from app.services.notificaciones import notificar as _notificar_multicanal

        for admin in db.scalars(
            select(Usuario).where(
                Usuario.rol == RolUsuario.admin,
                Usuario.estado == _EU.activo,
                Usuario.deleted_at.is_(None),
            )
        ).all():
            _notificar_multicanal(
                db,
                admin.id,
                TipoNotificacion.reserva,
                "Reserva temporal sin ejecutivo disponible",
                f"{empresa.razon_social} solicitó la reserva del stand {stand.codigo} y no hay ejecutivos activos. Reasignar manualmente.",
            )
    lead = Lead(
        empresa_id=empresa.id,
        contacto_id=contacto.id,
        ejecutivo_id=ejecutivo_id,
        origen="web",
        rubro=empresa.rubro,
        interes=payload.interes,
        paquete_interes_id=payload.paquete_interes_id,
        stand_interes_id=stand.id,
        estado=EstadoLead.reserva_temporal,
    )
    db.add(lead)
    db.flush()

    # 5. Bloqueo temporal de 30 minutos
    ahora = _utcnow()
    reserva = Reserva(
        empresa_id=empresa.id,
        lead_id=lead.id,
        stand_id=stand.id,
        ejecutivo_id=ejecutivo_id,
        estado=EstadoReserva.bloqueado,
        fecha_inicio=ahora,
        fecha_expiracion=ahora + timedelta(minutes=DURACION_BLOQUEO_MIN),
    )
    db.add(reserva)
    db.flush()

    stand.estado = EstadoStand.bloqueado_temporal
    stand.reserva_activa_id = reserva.id

    _auditar(db, reserva, None, f"Reserva temporal creada (stand {stand.codigo}, 30 min)")
    if ejecutivo_id:
        _notificar(
            db,
            ejecutivo_id,
            "Nueva reserva temporal",
            f"{empresa.razon_social} solicitó el stand {stand.codigo}. "
            f"Expira a las {reserva.fecha_expiracion:%H:%M} UTC.",
            reserva.id,
        )
    db.commit()
    db.refresh(reserva)
    return reserva


@router.get("", response_model=ReservaList)
def list_reservas(
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
    estado: EstadoReserva | None = Query(default=None),
    stand_id: uuid.UUID | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> ReservaList:
    liberar_expiradas(db)
    query = select(Reserva)
    if not user.is_admin:
        query = query.where(Reserva.ejecutivo_id == user.id)
    if estado:
        query = query.where(Reserva.estado == estado)
    if stand_id:
        query = query.where(Reserva.stand_id == stand_id)
    total = db.scalar(select(func.count()).select_from(query.subquery())) or 0
    items = db.scalars(
        query.order_by(Reserva.created_at.desc()).limit(limit).offset(offset)
    ).all()
    return ReservaList(total=total, items=[ReservaOut.model_validate(r) for r in items])


@router.get("/{reserva_id}", response_model=ReservaOut)
def get_reserva(
    reserva_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
) -> Reserva:
    liberar_expiradas(db)
    return _get_reserva_or_404(reserva_id, db, user)


@router.post("/{reserva_id}/confirmar", response_model=ReservaOut)
def confirmar_reserva(
    reserva_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
) -> Reserva:
    """Negociación activa: 'Bloqueado' → 'Reservado'. Detiene el conteo."""
    reserva = _get_reserva_or_404(reserva_id, db, user)
    if reserva.estado != EstadoReserva.bloqueado:
        raise HTTPException(
            status_code=409,
            detail=f"Solo se puede confirmar un bloqueo (estado: {reserva.estado.value})",
        )

    reserva.estado = EstadoReserva.reservado
    reserva.fecha_expiracion = None  # se detiene el conteo de 30 min
    stand = db.get(Stand, reserva.stand_id)
    stand.estado = EstadoStand.reservado
    if reserva.lead_id:
        lead = db.get(Lead, reserva.lead_id)
        if lead is not None:
            lead.estado = EstadoLead.reservado

    _auditar(db, reserva, user.id, f"Reserva confirmada (stand {stand.codigo})")
    if reserva.ejecutivo_id:
        _notificar(
            db, reserva.ejecutivo_id, "Reserva confirmada",
            f"El stand {stand.codigo} quedó reservado.", reserva.id,
        )
    db.commit()
    db.refresh(reserva)
    return reserva


@router.post("/{reserva_id}/extender", response_model=ReservaOut)
def extender_reserva(
    reserva_id: uuid.UUID,
    payload: ReservaExtendRequest,
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
) -> Reserva:
    """Extensión única de 30 o 60 minutos con motivo registrado (docs/06)."""
    if payload.minutos not in (30, 60):
        raise HTTPException(status_code=400, detail="La extensión debe ser de 30 o 60 minutos")

    reserva = _get_reserva_or_404(reserva_id, db, user)
    if reserva.estado != EstadoReserva.bloqueado:
        raise HTTPException(
            status_code=409,
            detail="Solo se puede extender un bloqueo temporal activo",
        )
    if reserva.fecha_extension is not None:
        raise HTTPException(status_code=409, detail="La reserva ya fue extendida una vez")

    reserva.fecha_extension = _utcnow()
    reserva.motivo_extension = payload.motivo
    reserva.fecha_expiracion = _utcnow() + timedelta(minutes=payload.minutos)

    _auditar(
        db, reserva, user.id,
        f"Reserva extendida {payload.minutos} min. Motivo: {payload.motivo}",
    )
    db.commit()
    db.refresh(reserva)
    return reserva


@router.post("/{reserva_id}/vender", response_model=ReservaOut)
def vender_reserva(
    reserva_id: uuid.UUID,
    payload: ReservaVenderRequest,
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
) -> Reserva:
    """Venta confirmada: → 'Vendido' + stand 'Vendido'."""
    reserva = _get_reserva_or_404(reserva_id, db, user)
    if reserva.estado not in (EstadoReserva.bloqueado, EstadoReserva.reservado):
        raise HTTPException(
            status_code=409,
            detail=f"No se puede vender desde el estado {reserva.estado.value}",
        )

    reserva.estado = EstadoReserva.vendido
    reserva.monto = payload.monto
    reserva.comprobante_url = payload.comprobante_url
    reserva.contrato_url = payload.contrato_url
    reserva.fecha_expiracion = None

    stand = db.get(Stand, reserva.stand_id)
    stand.estado = EstadoStand.vendido
    if reserva.lead_id:
        lead = db.get(Lead, reserva.lead_id)
        if lead is not None:
            lead.estado = EstadoLead.vendido

    _auditar(db, reserva, user.id, f"Venta confirmada por {payload.monto} (stand {stand.codigo})")
    if reserva.ejecutivo_id:
        _notificar(
            db, reserva.ejecutivo_id, "Stand vendido",
            f"El stand {stand.codigo} se vendió por {payload.monto}.", reserva.id,
        )
    db.commit()
    db.refresh(reserva)
    return reserva


@router.post("/{reserva_id}/cancelar", response_model=ReservaOut)
def cancelar_reserva(
    reserva_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
) -> Reserva:
    """Liberación manual: el stand vuelve a 'Disponible' y el lead queda
    registrado para seguimiento."""
    reserva = _get_reserva_or_404(reserva_id, db, user)
    if reserva.estado in (EstadoReserva.vendido, EstadoReserva.expirado):
        raise HTTPException(
            status_code=409,
            detail=f"No se puede cancelar una reserva {reserva.estado.value}",
        )

    reserva.estado = EstadoReserva.cancelado
    reserva.fecha_expiracion = None
    stand = db.get(Stand, reserva.stand_id)
    if stand.estado in (EstadoStand.bloqueado_temporal, EstadoStand.reservado):
        stand.estado = EstadoStand.disponible
        stand.reserva_activa_id = None
    if reserva.lead_id:
        lead = db.get(Lead, reserva.lead_id)
        if lead is not None:
            lead.estado = EstadoLead.interesado  # queda para seguimiento

    _auditar(db, reserva, user.id, f"Reserva cancelada (stand {stand.codigo})")
    db.commit()
    db.refresh(reserva)
    return reserva


@router.post("/liberar-expiradas")
def liberar_manual(
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
) -> dict:
    """Disparador manual (también lo usará n8n en Fase 2)."""
    cantidad = liberar_expiradas(db)
    return {"liberadas": cantidad}
