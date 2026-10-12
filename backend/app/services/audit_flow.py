"""
Orquestación del flujo completo de auditoría de un procedimiento:

    1. Construir el Markdown con las 9 secciones (lado izquierdo).
    2. Guardarlo como archivo .md (evidencia).
    3. Enviarlo a la IA y recibir el JSON por sección.
    4. Escribir cada feedback en su columna espejo `feedback_<seccion>`.
    5. Registrar la auditoría en el historial (éxito o error).

Se mantiene separado de los routers para poder reutilizarlo desde una
tarea en segundo plano, un worker o un script por lotes.
"""
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from ..config import get_settings
from ..models import Auditoria, EstadoAuditoria, Procedimiento
from ..schemas import ProcedimientoOut, SectionFeedback
from ..sections import SECTION_KEYS
from .ai_auditor import AIAuditError, audit_procedure_markdown
from .markdown_builder import build_markdown, save_markdown


def run_audit(db: Session, proc: Procedimiento) -> Procedimiento:
    """Ejecuta la auditoría con IA y persiste el resultado. Nunca lanza AIAuditError:
    el fallo queda guardado en `estado_auditoria` / `error_auditoria`."""
    settings = get_settings()

    # Marcar como "procesando" para que otras pantallas lo vean en curso.
    proc.estado_auditoria = EstadoAuditoria.PROCESANDO.value
    proc.error_auditoria = None
    db.commit()

    markdown = build_markdown(proc, proc.area.nombre)
    md_path = save_markdown(markdown, proc.id, settings.markdown_dir)
    registro = Auditoria(procedimiento_id=proc.id, markdown_enviado=markdown, ruta_markdown=str(md_path))

    try:
        ai = audit_procedure_markdown(markdown)
    except AIAuditError as exc:
        proc.estado_auditoria = EstadoAuditoria.ERROR.value
        proc.error_auditoria = str(exc)
        registro.error = str(exc)
        db.add(registro)
        db.commit()
        return proc

    # Mapear cada sección del JSON a su columna feedback_<clave>.
    for key in SECTION_KEYS:
        section_fb: SectionFeedback = getattr(ai.result, key)
        setattr(proc, f"feedback_{key}", section_fb.model_dump())

    proc.resumen_general = ai.result.resumen_general
    proc.calificacion_global = max(0, min(100, ai.result.calificacion_global))
    proc.estado_auditoria = EstadoAuditoria.COMPLETADA.value
    proc.auditado_en = datetime.now(timezone.utc)

    registro.respuesta_json = ai.raw_json
    registro.modelo = ai.model
    registro.tokens_entrada = ai.input_tokens
    registro.tokens_salida = ai.output_tokens
    registro.exitosa = True
    db.add(registro)
    db.commit()
    db.refresh(proc)
    return proc


def to_out(proc: Procedimiento) -> ProcedimientoOut:
    """Serializa un Procedimiento agrupando los 9 feedbacks en un dict por sección."""
    data = {c.name: getattr(proc, c.name) for c in proc.__table__.columns}
    data["area_nombre"] = proc.area.nombre if proc.area else None
    data["feedback"] = {key: getattr(proc, f"feedback_{key}") for key in SECTION_KEYS}
    return ProcedimientoOut.model_validate(data)
