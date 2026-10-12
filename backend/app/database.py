"""
Conexión a la base de datos con SQLAlchemy 2.x.

- `engine`: conexión física (SQLite o PostgreSQL según DATABASE_URL).
- `SessionLocal`: fábrica de sesiones; cada request obtiene la suya.
- `get_db`: dependencia de FastAPI que abre y cierra la sesión.
"""
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from .config import get_settings

settings = get_settings()

# SQLite necesita este flag para usarse desde los hilos de FastAPI.
connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}

engine = create_engine(settings.database_url, connect_args=connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    """Clase base de todos los modelos ORM."""


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
