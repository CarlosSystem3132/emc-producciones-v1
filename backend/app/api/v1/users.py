"""Gestión de usuarios/ejecutivos.

Reglas (docs/07 — Panel del administrador):
- Solo el admin crea, edita, bloquea, desactiva, elimina, cambia roles
  y restablece contraseñas de ejecutivos.
- El ejecutivo puede editar únicamente su propio perfil (sin rol ni estado).
- Si un ejecutivo tiene empresas asignadas, no se elimina físicamente:
  se sugiere reasignar o desactivar.
"""
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_admin
from app.core.security import hash_password
from app.db.session import get_db
from app.models.common import EstadoUsuario
from app.models.crm import Empresa
from app.models.user import Usuario
from app.schemas.user import PasswordReset, UserCreate, UserList, UserOut, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


def _get_user_or_404(user_id: uuid.UUID, db: Session) -> Usuario:
    user = db.get(Usuario, user_id)
    if user is None or user.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user


@router.get("", response_model=UserList)
def list_users(
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
    rol: str | None = Query(default=None),
    estado: str | None = Query(default=None),
    search: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> UserList:
    query = select(Usuario).where(Usuario.deleted_at.is_(None))
    if rol:
        query = query.where(Usuario.rol == rol)
    if estado:
        query = query.where(Usuario.estado == estado)
    if search:
        like = f"%{search}%"
        query = query.where(
            Usuario.nombre_completo.ilike(like) | Usuario.email.ilike(like)
        )
    total = db.scalar(select(func.count()).select_from(query.subquery())) or 0
    users = db.scalars(
        query.order_by(Usuario.created_at.desc()).limit(limit).offset(offset)
    ).all()
    return UserList(total=total, items=[UserOut.model_validate(u) for u in users])


@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(require_admin),
) -> Usuario:
    if db.scalar(select(Usuario).where(Usuario.email == payload.email)):
        raise HTTPException(status_code=409, detail="El correo ya está registrado")
    user = Usuario(
        **payload.model_dump(exclude={"password"}),
        hashed_password=hash_password(payload.password),
        creado_por=admin.id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get("/{user_id}", response_model=UserOut)
def get_user(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    current: Usuario = Depends(get_current_user),
) -> Usuario:
    if not current.is_admin and current.id != user_id:
        raise HTTPException(status_code=403, detail="Sin permiso para ver este usuario")
    return _get_user_or_404(user_id, db)


@router.patch("/{user_id}", response_model=UserOut)
def update_user(
    user_id: uuid.UUID,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    current: Usuario = Depends(get_current_user),
) -> Usuario:
    target = _get_user_or_404(user_id, db)
    data = payload.model_dump(exclude_unset=True)

    if not current.is_admin:
        # El ejecutivo solo puede editarse a sí mismo y sin rol ni estado
        if current.id != user_id:
            raise HTTPException(status_code=403, detail="Sin permiso para editar este usuario")
        data.pop("rol", None)
        data.pop("estado", None)

    for field, value in data.items():
        setattr(target, field, value)
    db.commit()
    db.refresh(target)
    return target


def _set_estado(
    user_id: uuid.UUID, estado: EstadoUsuario, db: Session, admin: Usuario
) -> Usuario:
    target = _get_user_or_404(user_id, db)
    if target.id == admin.id:
        raise HTTPException(status_code=400, detail="No puedes cambiar tu propio estado")
    target.estado = estado
    db.commit()
    db.refresh(target)
    return target


@router.post("/{user_id}/block", response_model=UserOut)
def block_user(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(require_admin),
) -> Usuario:
    return _set_estado(user_id, EstadoUsuario.bloqueado, db, admin)


@router.post("/{user_id}/activate", response_model=UserOut)
def activate_user(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(require_admin),
) -> Usuario:
    return _set_estado(user_id, EstadoUsuario.activo, db, admin)


@router.post("/{user_id}/deactivate", response_model=UserOut)
def deactivate_user(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(require_admin),
) -> Usuario:
    return _set_estado(user_id, EstadoUsuario.inactivo, db, admin)


@router.post("/{user_id}/reset-password", status_code=status.HTTP_204_NO_CONTENT)
def reset_password(
    user_id: uuid.UUID,
    payload: PasswordReset,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
) -> None:
    target = _get_user_or_404(user_id, db)
    target.hashed_password = hash_password(payload.new_password)
    db.commit()


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(require_admin),
) -> None:
    target = _get_user_or_404(user_id, db)
    if target.id == admin.id:
        raise HTTPException(status_code=400, detail="No puedes eliminarte a ti mismo")

    # docs/07: con registros asociados se sugiere reasignar o desactivar
    empresas_asignadas = db.scalar(
        select(func.count()).select_from(Empresa).where(
            Empresa.ejecutivo_id == user_id,
            Empresa.deleted_at.is_(None),
        )
    ) or 0
    if empresas_asignadas > 0:
        raise HTTPException(
            status_code=409,
            detail=(
                f"El usuario tiene {empresas_asignadas} empresa(s) asignadas. "
                "Reasigna las empresas o desactívalo en lugar de eliminarlo."
            ),
        )

    # Soft delete + bloqueo de acceso
    target.deleted_at = datetime.now(timezone.utc)
    target.estado = EstadoUsuario.inactivo
    db.commit()
