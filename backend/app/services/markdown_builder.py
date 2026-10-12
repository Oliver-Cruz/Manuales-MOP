"""
Empaqueta el lado izquierdo del procedimiento en un documento Markdown (.md).

Estructura generada (equivalente al ".docx → .json" del pizarrón, pero en
Markdown porque es el formato que mejor interpreta un LLM):

    # Procedimiento: <nombre>
    - Código / Área / Fecha
    ## 1. Objetivo
    <!-- seccion: objetivo -->
    <texto capturado o "_(Sección vacía)_">
    ## 2. Descripción de actividades
    ...

El comentario `<!-- seccion: clave -->` ancla cada bloque con la llave que
la IA debe usar en su JSON, evitando que confunda secciones.
"""
from datetime import datetime, timezone
from pathlib import Path

from ..models import Procedimiento
from ..sections import SECTIONS

EMPTY_MARK = "_(Sección vacía: el usuario no capturó información)_"


def build_markdown(proc: Procedimiento, area_nombre: str) -> str:
    """Convierte un Procedimiento en un string Markdown listo para la IA."""
    lines: list[str] = [
        f"# Procedimiento: {proc.nombre}",
        "",
        f"- **Código:** {proc.codigo or 'Sin código'}",
        f"- **Área responsable:** {area_nombre}",
        f"- **Fecha de envío a auditoría:** {datetime.now(timezone.utc):%Y-%m-%d %H:%M} UTC",
        "",
        "---",
        "",
    ]
    for i, section in enumerate(SECTIONS, start=1):
        content = (getattr(proc, section.key) or "").strip()
        lines += [
            f"## {i}. {section.title}",
            f"<!-- seccion: {section.key} -->",
            "",
            content or EMPTY_MARK,
            "",
        ]
    return "\n".join(lines)


def save_markdown(markdown: str, proc_id: int, directory: Path) -> Path:
    """Guarda el .md en disco (evidencia de lo enviado) y devuelve la ruta."""
    directory.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%f")
    path = directory / f"procedimiento_{proc_id}_{stamp}.md"
    path.write_text(markdown, encoding="utf-8")
    return path
