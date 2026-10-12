"""
Punto de entrada de la API.

    cd backend
    uvicorn app.main:app --reload

- Crea las tablas al arrancar (para producción usar Alembic).
- Siembra áreas iniciales si la tabla está vacía.
- Sirve el frontend (../frontend/index.html) en http://localhost:8000/
- Documentación interactiva en http://localhost:8000/docs
"""
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy import select

from .database import Base, SessionLocal, engine
from .models import Area
from .routers import areas, procedimientos
from .sections import SECTIONS

FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend"
AREAS_INICIALES = ("Finanzas", "Operaciones", "Recursos Humanos")


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        if not db.scalar(select(Area).limit(1)):
            db.add_all(Area(nombre=n) for n in AREAS_INICIALES)
            db.commit()
    yield


app = FastAPI(title="Auditoría Inteligente de Procedimientos (MOP)", version="1.0.0", lifespan=lifespan)

# Permite abrir el frontend desde otro origen (ej. Live Server en :5500).
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

app.include_router(areas.router)
app.include_router(procedimientos.router)


@app.get("/api/sections", tags=["Catálogo"])
def list_sections():
    """Catálogo de las 9 secciones: el frontend lo usa para pintar las filas Input | Feedback."""
    return [{"key": s.key, "title": s.title, "guide": s.guide} for s in SECTIONS]


@app.get("/", include_in_schema=False)
def frontend():
    return FileResponse(FRONTEND_DIR / "index.html")
