"""
Catálogo único de las 9 secciones de un procedimiento.

Es la "fuente de verdad" que comparten:
  - el modelo de base de datos (columna de contenido + columna de feedback),
  - el generador de Markdown que se envía a la IA,
  - el esquema JSON que la IA debe devolver,
  - el frontend (vía GET /api/sections) para pintar las filas
    Izquierda: Input  |  Derecha: Feedback.

Para agregar o renombrar una sección basta con editar esta lista
(y crear la migración de columnas correspondiente).
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Section:
    key: str          # nombre técnico (columna en BD y llave en el JSON)
    title: str        # título que ve el usuario
    guide: str        # qué se espera en la sección (ayuda al usuario y a la IA)


SECTIONS: tuple[Section, ...] = (
    Section(
        "objetivo",
        "Objetivo",
        "Propósito del procedimiento: qué se logra, para quién y por qué. Debe ser medible y "
        "empezar con un verbo en infinitivo.",
    ),
    Section(
        "descripcion_actividades",
        "Descripción de actividades",
        "Secuencia numerada de actividades con responsable (puesto), acción, insumo/producto y "
        "puntos de decisión.",
    ),
    Section(
        "diagrama_flujo",
        "Diagrama de flujo",
        "Representación del flujo (descripción textual, notación Mermaid o enlace). Debe coincidir "
        "1:1 con las actividades: inicio, fin, decisiones y carriles por responsable.",
    ),
    Section(
        "mecanismos_control",
        "Mecanismos de control",
        "Puntos de control, validaciones, autorizaciones y evidencias que aseguran que el proceso "
        "se ejecuta correctamente.",
    ),
    Section(
        "elementos_entrada_contexto",
        "Elementos de entrada y contexto",
        "Insumos, disparadores, proveedores, alcance (dónde inicia y termina) y contexto "
        "organizacional.",
    ),
    Section(
        "referencias",
        "Referencias",
        "Normativa, leyes, reglamentos, manuales y documentos relacionados con su clave/versión.",
    ),
    Section(
        "politicas_operacion",
        "Políticas de operación",
        "Reglas obligatorias que delimitan la ejecución: plazos, responsabilidades, restricciones "
        "y excepciones.",
    ),
    Section(
        "formatos_procedimientos",
        "Formatos de procedimientos",
        "Formatos, plantillas y registros utilizados, con clave, nombre y en qué actividad se usan.",
    ),
    Section(
        "medicion_procedimientos",
        "Medición de procedimientos",
        "Indicadores (KPI) con fórmula, meta, frecuencia, fuente de datos y responsable de medir.",
    ),
)

SECTION_KEYS: tuple[str, ...] = tuple(s.key for s in SECTIONS)
