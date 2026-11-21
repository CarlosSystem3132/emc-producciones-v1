"""Sesión de base de datos para inyección de dependencias."""
from collections.abc import Generator

from sqlalchemy.orm import Session, sessionmaker

from app.db.base import engine

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
