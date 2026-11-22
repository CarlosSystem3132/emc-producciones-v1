"""CRUD de empresas y contactos.

Reglas (docs/04):
- Cada ejecutivo ve únicamente sus empresas asignadas; el admin ve todas.
- Un ejecutivo puede registrar empresas propias (queda asignado automáticamente).
- El sistema valida duplicados por razón social, correo y WhatsApp.
- El admin puede reasignar empresas entre ejecutivos.
- Importación desde CSV/Excel y exportación CSV (docs/02).
"""
import csv
import io
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from fastapi.responses import StreamingResponse
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_current_user, require_admin
from app.db.session import get_db
from app.models.common import EstadoLead
from app.models.crm import Contacto, Empresa
from app.models.user import Usuario
from app.schemas.empresa import (
    ContactoCreate,
    ContactoOut,
    EmpresaCreate,
    EmpresaDetail,
    EmpresaList,
    EmpresaOut,
    EmpresaUpdate,
)

router = APIRouter(prefix="/empresas", tags=["empresas"])


def _scope_query(user: Usuario, query):
    """El ejecutivo solo ve sus empresas; el admin ve todas."""
    if not user.is_admin:
        query = query.where(
            or_(Empresa.ejecutivo_id == user.id, Empresa.creado_por == user.id)
        )
    return query


def _get_empresa_or_404(empresa_id: uuid.UUID, db: Session, user: Usuario) -> Empresa:
    empresa = db.get(Empresa, empresa_id)
    if empresa is None or empresa.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
    if not user.is_admin and empresa.ejecutivo_id != user.id and empresa.creado_por != user.id:
        raise HTTPException(status_code=403, detail="Sin permiso sobre esta empresa")
    return empresa


def _check_duplicados(
    db: Session,
    razon_social: str | None = None,
    email: str | None = None,
    whatsapp: str | None = None,
    exclude_empresa_id: uuid.UUID | None = None,
) -> None:
    if razon_social:
        q = select(Empresa).where(
            func.lower(Empresa.razon_social) == razon_social.lower(),
            Empresa.deleted_at.is_(None),
        )
        if exclude_empresa_id:
            q = q.where(Empresa.id != exclude_empresa_id)
        if db.scalar(q):
            raise HTTPException(
                status_code=409,
                detail=f"Ya existe una empresa con la razón social '{razon_social}'",
            )
    for campo, valor in (("email", email), ("whatsapp", whatsapp)):
        if valor:
            q = select(Contacto).where(getattr(Contacto, campo) == valor)
            if exclude_empresa_id:
                q = q.where(Contacto.empresa_id != exclude_empresa_id)
            if db.scalar(q):
                raise HTTPException(
                    status_code=409,
                    detail=f"Ya existe un contacto con ese {campo}",
                )


@router.get("", response_model=EmpresaList)
def list_empresas(
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
    estado: EstadoLead | None = Query(default=None),
    rubro: str | None = Query(default=None),
    ejecutivo_id: uuid.UUID | None = Query(default=None),
    search: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> EmpresaList:
    query = select(Empresa).where(Empresa.deleted_at.is_(None))
    query = _scope_query(user, query)
    if estado:
        query = query.where(Empresa.estado == estado)
    if rubro:
        query = query.where(Empresa.rubro == rubro)
    if ejecutivo_id:
        query = query.where(Empresa.ejecutivo_id == ejecutivo_id)
    if search:
        like = f"%{search}%"
        query = query.where(
            or_(
                Empresa.razon_social.ilike(like),
                Empresa.nombre_comercial.ilike(like),
                Empresa.rubro.ilike(like),
            )
        )
    total = db.scalar(select(func.count()).select_from(query.subquery())) or 0
    items = db.scalars(
        query.order_by(Empresa.updated_at.desc()).limit(limit).offset(offset)
    ).all()
    return EmpresaList(total=total, items=[EmpresaOut.model_validate(e) for e in items])


@router.post("", response_model=EmpresaDetail, status_code=status.HTTP_201_CREATED)
def create_empresa(
    payload: EmpresaCreate,
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
) -> Empresa:
    data = payload.model_dump(exclude={"contacto"})
    _check_duplicados(
        db,
        razon_social=data["razon_social"],
        email=payload.contacto.email if payload.contacto else None,
        whatsapp=payload.contacto.whatsapp if payload.contacto else None,
    )

    # Solo el admin puede asignar a otro ejecutivo; el ejecutivo queda autoasignado
    if not user.is_admin:
        data["ejecutivo_id"] = user.id
    elif data.get("ejecutivo_id") is None:
        data["ejecutivo_id"] = user.id

    empresa = Empresa(**data, creado_por=user.id)
    db.add(empresa)
    db.flush()

    if payload.contacto:
        db.add(Contacto(**payload.contacto.model_dump(), empresa_id=empresa.id))
    db.commit()
    db.refresh(empresa)
    return empresa


# ---------- Importación CSV / Excel ----------

COLUMNAS = {
    "razon_social": "razon_social",
    "razón social": "razon_social",
    "nombre_comercial": "nombre_comercial",
    "rubro": "rubro",
    "ciudad": "ciudad",
    "pais": "pais",
    "país": "pais",
    "sitio_web": "sitio_web",
    "web": "sitio_web",
    "email": "email",
    "correo": "email",
    "whatsapp": "whatsapp",
    "telefono": "telefono",
    "teléfono": "telefono",
    "nombre_contacto": "nombre_contacto",
    "contacto": "nombre_contacto",
    "cargo_contacto": "cargo_contacto",
    "cargo": "cargo_contacto",
}


def _leer_filas(archivo: UploadFile) -> list[dict[str, str]]:
    """Devuelve filas normalizadas desde CSV (.csv) o Excel (.xlsx)."""
    nombre = (archivo.filename or "").lower()
    contenido = archivo.file.read()

    if nombre.endswith(".xlsx"):
        try:
            from openpyxl import load_workbook
        except ImportError:
            raise HTTPException(status_code=500, detail="openpyxl no está instalado en el servidor")
        wb = load_workbook(io.BytesIO(contenido), read_only=True, data_only=True)
        hoja = wb.active
        filas_raw = [["" if c is None else str(c) for c in fila] for fila in hoja.iter_rows(values_only=True)]
    else:
        # CSV: acepta ; o , como separador y BOM de Excel
        texto = contenido.decode("utf-8-sig", errors="replace")
        sample = texto[:2048]
        delimitador = ";" if sample.count(";") > sample.count(",") else ","
        filas_raw = list(csv.reader(io.StringIO(texto), delimiter=delimitador))

    if not filas_raw:
        return []

    encabezados = [COLUMNAS.get(h.strip().lower(), "") for h in filas_raw[0]]
    if "razon_social" not in encabezados:
        raise HTTPException(
            status_code=400,
            detail="El archivo debe tener una columna 'razon_social' (o 'Razón social')",
        )

    filas: list[dict[str, str]] = []
    for fila in filas_raw[1:]:
        datos = {campo: valor.strip() for campo, valor in zip(encabezados, fila) if campo}
        if any(datos.values()):
            filas.append(datos)
    return filas


@router.post("/import")
def import_empresas(
    archivo: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
) -> dict:
    """Importa empresas desde CSV o Excel con validación de duplicados
    (razón social, correo y WhatsApp — docs/02)."""
    filas = _leer_filas(archivo)

    creadas = 0
    duplicadas = 0
    errores: list[str] = []

    for i, fila in enumerate(filas, start=2):  # fila 1 = encabezados
        razon_social = fila.get("razon_social", "")
        if not razon_social:
            errores.append(f"Fila {i}: falta razón social")
            continue

        existe = db.scalar(
            select(Empresa).where(
                func.lower(Empresa.razon_social) == razon_social.lower(),
                Empresa.deleted_at.is_(None),
            )
        )
        if existe:
            duplicadas += 1
            continue

        email = fila.get("email") or None
        whatsapp = fila.get("whatsapp") or None
        if email and db.scalar(select(Contacto).where(Contacto.email == email)):
            duplicadas += 1
            continue

        empresa = Empresa(
            razon_social=razon_social,
            nombre_comercial=fila.get("nombre_comercial") or None,
            rubro=fila.get("rubro") or None,
            ciudad=fila.get("ciudad") or None,
            pais=fila.get("pais") or None,
            sitio_web=fila.get("sitio_web") or None,
            origen="importacion",
            ejecutivo_id=user.id,
            creado_por=user.id,
        )
        db.add(empresa)
        db.flush()

        if fila.get("nombre_contacto") or email or whatsapp:
            db.add(
                Contacto(
                    empresa_id=empresa.id,
                    nombre=fila.get("nombre_contacto") or "Contacto",
                    cargo=fila.get("cargo_contacto") or None,
                    email=email,
                    whatsapp=whatsapp,
                    telefono=fila.get("telefono") or None,
                )
            )
        creadas += 1

    db.commit()
    return {"creadas": creadas, "duplicadas": duplicadas, "errores": errores}


# ---------- Exportación CSV ----------

@router.get("/export")
def export_empresas(
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
) -> StreamingResponse:
    """Exporta las empresas visibles para el usuario a CSV (UTF-8 con BOM
    para Excel)."""
    query = select(Empresa).where(Empresa.deleted_at.is_(None))
    query = _scope_query(user, query)
    empresas = db.scalars(query.order_by(Empresa.razon_social)).all()

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(
        [
            "razon_social", "nombre_comercial", "rubro", "ciudad", "pais",
            "sitio_web", "estado", "origen", "ejecutivo_id", "created_at",
        ]
    )
    for e in empresas:
        writer.writerow(
            [
                e.razon_social, e.nombre_comercial or "", e.rubro or "",
                e.ciudad or "", e.pais or "", e.sitio_web or "",
                e.estado.value, e.origen or "", str(e.ejecutivo_id or ""),
                e.created_at.isoformat() if e.created_at else "",
            ]
        )

    buffer.seek(0)
    return StreamingResponse(
        io.BytesIO(buffer.getvalue().encode("utf-8-sig")),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="empresas.csv"'},
    )


@router.get("/{empresa_id}", response_model=EmpresaDetail)
def get_empresa(
    empresa_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
) -> Empresa:
    return _get_empresa_or_404(empresa_id, db, user)


@router.patch("/{empresa_id}", response_model=EmpresaDetail)
def update_empresa(
    empresa_id: uuid.UUID,
    payload: EmpresaUpdate,
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
) -> Empresa:
    empresa = _get_empresa_or_404(empresa_id, db, user)
    data = payload.model_dump(exclude_unset=True)

    if not user.is_admin:
        data.pop("ejecutivo_id", None)  # reasignar es exclusivo del admin

    if "razon_social" in data:
        _check_duplicados(db, razon_social=data["razon_social"], exclude_empresa_id=empresa_id)

    for field, value in data.items():
        setattr(empresa, field, value)
    db.commit()
    db.refresh(empresa)
    return empresa


@router.delete("/{empresa_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_empresa(
    empresa_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
) -> None:
    empresa = _get_empresa_or_404(empresa_id, db, user)
    empresa.deleted_at = empresa.updated_at  # soft delete
    db.commit()


# ---------- Contactos ----------

@router.get("/{empresa_id}/contactos", response_model=list[ContactoOut])
def list_contactos(
    empresa_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
) -> list[Contacto]:
    empresa = _get_empresa_or_404(empresa_id, db, user)
    return list(empresa.contactos)


@router.post(
    "/{empresa_id}/contactos",
    response_model=ContactoOut,
    status_code=status.HTTP_201_CREATED,
)
def create_contacto(
    empresa_id: uuid.UUID,
    payload: ContactoCreate,
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
) -> Contacto:
    empresa = _get_empresa_or_404(empresa_id, db, user)
    _check_duplicados(db, email=payload.email, whatsapp=payload.whatsapp)
    contacto = Contacto(**payload.model_dump(), empresa_id=empresa.id)
    db.add(contacto)
    db.commit()
    db.refresh(contacto)
    return contacto


@router.patch(
    "/{empresa_id}/contactos/{contacto_id}",
    response_model=ContactoOut,
)
def update_contacto(
    empresa_id: uuid.UUID,
    contacto_id: uuid.UUID,
    payload: ContactoCreate,
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
) -> Contacto:
    _get_empresa_or_404(empresa_id, db, user)
    contacto = db.get(Contacto, contacto_id)
    if contacto is None or contacto.empresa_id != empresa_id:
        raise HTTPException(status_code=404, detail="Contacto no encontrado")
    _check_duplicados(
        db,
        email=payload.email,
        whatsapp=payload.whatsapp,
        exclude_empresa_id=empresa_id,
    )
    for field, value in payload.model_dump().items():
        setattr(contacto, field, value)
    db.commit()
    db.refresh(contacto)
    return contacto


@router.delete(
    "/{empresa_id}/contactos/{contacto_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_contacto(
    empresa_id: uuid.UUID,
    contacto_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
) -> None:
    _get_empresa_or_404(empresa_id, db, user)
    contacto = db.get(Contacto, contacto_id)
    if contacto is None or contacto.empresa_id != empresa_id:
        raise HTTPException(status_code=404, detail="Contacto no encontrado")
    db.delete(contacto)
    db.commit()
