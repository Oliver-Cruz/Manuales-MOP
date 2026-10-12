"""
Modelos de base de datos (SQLAlchemy 2.x, compatibles con SQLite y PostgreSQL).

    Area 1 ──── N Procedimiento 1 ──── N Auditoria
     (Finanzas,     (9 campos de captura     (historial de cada envío a la IA:
      RRHH, ...)     + 9 campos de feedback)   Markdown enviado + JSON recibido)

- Todo procedimiento pertenece OBLIGATORIAMENTE a un área (FK NOT NULL).
- Los 9 campos de la izquierda son texto libre.
- Los 9 campos de la derecha guardan el feedback de la IA como JSON
  (estado, comentario, faltantes, inconsistencias, sugerencia), lo que
  permite pintarlo con formato en el frontend sin volver a parsear texto.
"""
from datetime import datetime
from enum import Enum

from sqlalchemy import JSON, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class EstadoAuditoria(str, Enum):
    PENDIENTE = "pendiente"      # guardado, aún sin enviar a la IA
    PROCESANDO = "procesando"    # la IA está analizando
    COMPLETADA = "completada"    # feedback disponible
    ERROR = "error"              # falló la llamada o el parseo


class Area(Base):
    __tablename__ = "areas"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    procedimientos: Mapped[list["Procedimiento"]] = relationship(back_populates="area")


class Procedimiento(Base):
    __tablename__ = "procedimientos"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(255), nullable=False)
    codigo: Mapped[str | None] = mapped_column(String(50))  # ej. "FIN-PR-001"

    # Relación obligatoria con el área (no se puede guardar sin área).
    area_id: Mapped[int] = mapped_column(ForeignKey("areas.id", ondelete="RESTRICT"), nullable=False, index=True)
    area: Mapped[Area] = relationship(back_populates="procedimientos")

    # ── LADO IZQUIERDO: captura del usuario (9 secciones) ──────────────────
    objetivo: Mapped[str | None] = mapped_column(Text)
    descripcion_actividades: Mapped[str | None] = mapped_column(Text)
    diagrama_flujo: Mapped[str | None] = mapped_column(Text)
    mecanismos_control: Mapped[str | None] = mapped_column(Text)
    elementos_entrada_contexto: Mapped[str | None] = mapped_column(Text)
    referencias: Mapped[str | None] = mapped_column(Text)
    politicas_operacion: Mapped[str | None] = mapped_column(Text)
    formatos_procedimientos: Mapped[str | None] = mapped_column(Text)
    medicion_procedimientos: Mapped[str | None] = mapped_column(Text)

    # ── LADO DERECHO: feedback de la IA (9 secciones espejo) ───────────────
    # Cada columna guarda un dict: {estado, comentario, faltantes[], inconsistencias[], sugerencia}
    feedback_objetivo: Mapped[dict | None] = mapped_column(JSON)
    feedback_descripcion_actividades: Mapped[dict | None] = mapped_column(JSON)
    feedback_diagrama_flujo: Mapped[dict | None] = mapped_column(JSON)
    feedback_mecanismos_control: Mapped[dict | None] = mapped_column(JSON)
    feedback_elementos_entrada_contexto: Mapped[dict | None] = mapped_column(JSON)
    feedback_referencias: Mapped[dict | None] = mapped_column(JSON)
    feedback_politicas_operacion: Mapped[dict | None] = mapped_column(JSON)
    feedback_formatos_procedimientos: Mapped[dict | None] = mapped_column(JSON)
    feedback_medicion_procedimientos: Mapped[dict | None] = mapped_column(JSON)

    # ── Metadatos de la auditoría ──────────────────────────────────────────
    resumen_general: Mapped[str | None] = mapped_column(Text)
    calificacion_global: Mapped[int | None] = mapped_column()  # 0-100
    estado_auditoria: Mapped[str] = mapped_column(String(20), default=EstadoAuditoria.PENDIENTE.value)
    error_auditoria: Mapped[str | None] = mapped_column(Text)
    auditado_en: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    actualizado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    auditorias: Mapped[list["Auditoria"]] = relationship(
        back_populates="procedimiento", cascade="all, delete-orphan", order_by="Auditoria.id.desc()"
    )


class Auditoria(Base):
    """Historial: cada vez que se dispara la IA queda registro de qué se envió y qué respondió."""

    __tablename__ = "auditorias"

    id: Mapped[int] = mapped_column(primary_key=True)
    procedimiento_id: Mapped[int] = mapped_column(ForeignKey("procedimientos.id", ondelete="CASCADE"), index=True)
    procedimiento: Mapped[Procedimiento] = relationship(back_populates="auditorias")

    markdown_enviado: Mapped[str] = mapped_column(Text, nullable=False)
    ruta_markdown: Mapped[str | None] = mapped_column(String(500))
    respuesta_json: Mapped[dict | None] = mapped_column(JSON)
    modelo: Mapped[str | None] = mapped_column(String(80))
    tokens_entrada: Mapped[int | None] = mapped_column()
    tokens_salida: Mapped[int | None] = mapped_column()
    exitosa: Mapped[bool] = mapped_column(default=False)
    error: Mapped[str | None] = mapped_column(Text)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
