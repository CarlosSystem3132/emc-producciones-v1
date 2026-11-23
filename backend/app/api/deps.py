"""Dependencias de autenticación y autorización."""
import uuid

from fastapi import Depends, Header, HTTPException, status
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


_oauth2_auto = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login", auto_error=False
)


def require_admin_o_webhook(
    x_webhook_secret: str | None = Header(default=None),
    token: str | None = Depends(_oauth2_auto),
    db: Session = Depends(get_db),
) -> Usuario | None:
    """Acceso para automatizaciones (n8n) o administrador.

    n8n se autentica con el header `X-Webhook-Secret` (mismo secreto que los
    webhooks): evita que los flujos programados dependan de un JWT que expira
    cada hora. También acepta JWT de administrador para uso manual."""
    from app.core.config import settings

    if (
        x_webhook_secret
        and settings.webhook_secret
        and x_webhook_secret == settings.webhook_secret
    ):
        return None

    if token is None:
        raise _credentials_exception
    try:
        payload = decode_access_token(token)
        user_id = uuid.UUID(payload["sub"])
    except (DecodeError, ExpiredSignatureError, KeyError, ValueError):
        raise _credentials_exception

    user = db.get(Usuario, user_id)
    if user is None or user.deleted_at is not None:
        raise _credentials_exception
    if user.rol != RolUsuario.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Requiere rol administrador o secreto de automatización",
        )
    return user
