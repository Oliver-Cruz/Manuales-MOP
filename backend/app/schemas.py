"""
Esquemas Pydantic: contratos de entrada/salida de la API y de la IA.

- `SectionFeedback` / `AuditResult` definen EXACTAMENTE el JSON que la IA
  debe devolver. Se usan con "structured outputs" de Claude, por lo que la
  respuesta llega ya validada contra este esquema (no hay que limpiar texto).
- `ProcedimientoIn` / `ProcedimientoOut` son lo que intercambia el frontend.
"""
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from .sections import SECTION_KEYS

# ─────────────────────────── Respuesta de la IA ────────────────────────────

EstadoSeccion = Literal["cumple", "parcial", "no_cumple", "vacio"]


class SectionFeedback(BaseModel):
    """Feedback de UNA sección (lo que se pinta en el cuadro derecho)."""

    estado: EstadoSeccion = Field(description="Dictamen de la sección.")
    comentario: str = Field(description="Evaluación: si cumple su función y por qué.")
    faltantes: list[str] = Field(description="Información que hace falta exactamente.")
    inconsistencias: list[str] = Field(description="Contradicciones internas o con otras secciones.")
    sugerencia: str = Field(description="Redacción o acción concreta para corregir la sección.")


class AuditResult(BaseModel):
    """JSON completo: un feedback por cada una de las 9 secciones + resumen."""

    objetivo: SectionFeedback
    descripcion_actividades: SectionFeedback
    diagrama_flujo: SectionFeedback
    mecanismos_control: SectionFeedback
    elementos_entrada_contexto: SectionFeedback
    referencias: SectionFeedback
    politicas_operacion: SectionFeedback
    formatos_procedimientos: SectionFeedback
    medicion_procedimientos: SectionFeedback
    resumen_general: str
    calificacion_global: int = Field(description="Calificación de 0 a 100.")


# Garantiza en tiempo de importación que el esquema y el catálogo coinciden.
assert set(SECTION_KEYS) <= set(AuditResult.model_fields), "AuditResult no cubre todas las secciones"


# ─────────────────────────────── Áreas ─────────────────────────────────────

class AreaIn(BaseModel):
    nombre: str = Field(min_length=2, max_length=120)
    descripcion: str | None = None


class AreaOut(AreaIn):
    model_config = ConfigDict(from_attributes=True)
    id: int


# ─────────────────────────── Procedimientos ────────────────────────────────

class ProcedimientoIn(BaseModel):
    """Lo que envía el formulario (lado izquierdo)."""

    nombre: str = Field(min_length=3, max_length=255)
    codigo: str | None = None
    area_id: int  # obligatorio

    objetivo: str | None = None
    descripcion_actividades: str | None = None
    diagrama_flujo: str | None = None
    mecanismos_control: str | None = None
    elementos_entrada_contexto: str | None = None
    referencias: str | None = None
    politicas_operacion: str | None = None
    formatos_procedimientos: str | None = None
    medicion_procedimientos: str | None = None


class ProcedimientoOut(ProcedimientoIn):
    """Lo que regresa al frontend: captura + feedback por sección (lado derecho)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    area_nombre: str | None = None
    # { "objetivo": {estado, comentario, ...}, "referencias": {...}, ... }
    feedback: dict[str, SectionFeedback | None] = {}
    resumen_general: str | None = None
    calificacion_global: int | None = None
    estado_auditoria: str
    error_auditoria: str | None = None
    auditado_en: datetime | None = None
    actualizado_en: datetime | None = None


class ProcedimientoResumen(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    nombre: str
    codigo: str | None
    area_id: int
    estado_auditoria: str
    calificacion_global: int | None
    actualizado_en: datetime | None
