"""Dependencias de autenticación y autorización."""
import uuid

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt import DecodeError, ExpiredSignatureError
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.common import EstadoUsuario, RolUsuario
from app.models.user import Usuario

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

_credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Credenciales inválidas",
    headers={"WWW-Authenticate": "Bearer"},
)


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> Usuario:
    try:
        payload = decode_access_token(token)
        user_id = uuid.UUID(payload["sub"])
    except (DecodeError, ExpiredSignatureError, KeyError, ValueError):
        raise _credentials_exception

    user = db.get(Usuario, user_id)
    if user is None or user.deleted_at is not None:
        raise _credentials_exception
    if user.estado != EstadoUsuario.activo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario bloqueado o inactivo",
        )
    return user


def require_admin(user: Usuario = Depends(get_current_user)) -> Usuario:
    if user.rol != RolUsuario.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Requiere rol administrador",
        )
    return user
