"""Autenticación: login y perfil propio."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.security import create_access_token, verify_password
from app.db.session import get_db
from app.models.common import EstadoUsuario
from app.models.user import Usuario
from app.schemas.auth import LoginRequest, Token
from app.schemas.user import UserOut

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=Token)
def login(credentials: LoginRequest, db: Session = Depends(get_db)) -> Token:
    user = db.scalar(select(Usuario).where(Usuario.email == credentials.email))
    if user is None or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos",
        )
    if user.estado != EstadoUsuario.activo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario bloqueado o inactivo",
        )
    token = create_access_token(subject=str(user.id), rol=user.rol.value)
    return Token(access_token=token)


@router.get("/me", response_model=UserOut)
def me(user: Usuario = Depends(get_current_user)) -> Usuario:
    return user
