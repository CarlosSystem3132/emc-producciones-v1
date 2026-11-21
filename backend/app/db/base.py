"""Base declarativa y engine de SQLAlchemy 2.0."""
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


class Base(DeclarativeBase):
    pass


engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    future=True,
    connect_args={"check_same_thread": False} if settings.database_url.startswith("sqlite") else {},
)
