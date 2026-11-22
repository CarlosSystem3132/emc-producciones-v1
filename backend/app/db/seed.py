"""Seed: crea el usuario administrador inicial si no existe ninguno."""
from sqlalchemy import select

from app.core.config import settings
from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.common import EstadoUsuario, RolUsuario
from app.models.user import Usuario


def seed_initial_admin() -> None:
    db = SessionLocal()
    try:
        exists = db.scalar(
            select(Usuario).where(Usuario.rol == RolUsuario.admin, Usuario.deleted_at.is_(None))
        )
        if exists:
            return
        admin = Usuario(
            nombre_completo="Administrador",
            email=settings.seed_admin_email,
            hashed_password=hash_password(settings.seed_admin_password),
            rol=RolUsuario.admin,
            estado=EstadoUsuario.activo,
        )
        db.add(admin)
        db.commit()
        print(f"[seed] Administrador inicial creado: {settings.seed_admin_email}")
    finally:
        db.close()
