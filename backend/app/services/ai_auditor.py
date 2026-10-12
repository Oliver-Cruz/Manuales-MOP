"""
Servicio de integración con la IA (Anthropic Claude).

Flujo:
    Markdown (.md) ──► Claude (system prompt de auditor) ──► JSON validado
                                                            (AuditResult)

Decisiones de diseño:
- **Structured outputs** (`output_format=AuditResult`): la API restringe la
  respuesta al esquema Pydantic, así que el JSON siempre trae las 9 secciones
  con los campos esperados. No hay que "limpiar" bloques ```json``` ni
  adivinar llaves.
- **Thinking adaptativo + effort**: el modelo decide cuánto razonar; `effort`
  (config `AI_EFFORT`) controla profundidad vs. costo.
- **Fallback de seguridad** (`fallbacks="default"`): si los clasificadores de
  seguridad rechazan la petición, la API reintenta automáticamente con otro
  modelo dentro de la misma llamada.
- Los errores se traducen a `AIAuditError` para que el endpoint responda con
  un mensaje claro y guarde el fallo en la BD.
"""
from dataclasses import dataclass

import anthropic

from ..config import get_settings
from ..schemas import AuditResult
from ..sections import SECTIONS

# ───────────────────────────── System prompt ───────────────────────────────

_SECTION_GUIDE = "\n".join(f"- `{s.key}` — **{s.title}**: {s.guide}" for s in SECTIONS)

SYSTEM_PROMPT = f"""Eres un auditor senior de procesos y manuales de operación (MOP) en una organización \
mexicana. Tu trabajo es revisar procedimientos antes de que se publiquen, para que el área \
responsable los corrija.

Analiza minuciosamente cada sección del procedimiento adjunto en Markdown. Para cada una evalúa:
1. Si cumple su función dentro del procedimiento.
2. Qué inconsistencias tiene, tanto internas como contra las otras secciones (por ejemplo, \
actividades que no aparecen en el diagrama, formatos mencionados que no están listados, \
indicadores que no miden el objetivo, controles sin responsable).
3. Qué información le hace falta exactamente: sé específico y accionable ("falta el puesto \
responsable de la actividad 4"), nunca genérico ("agregar más detalle").

Lo que se espera de cada sección (las llaves del JSON van entre comillas invertidas):
{_SECTION_GUIDE}

Reglas de dictamen (`estado`):
- "cumple": la sección cumple su función; puede tener sugerencias menores.
- "parcial": existe pero le faltan elementos o tiene inconsistencias relevantes.
- "no_cumple": el contenido no corresponde a la sección o es insuficiente para operar.
- "vacio": la sección viene marcada como vacía.

En `sugerencia` propone una redacción corregida o la acción concreta que debe realizar el usuario. \
`calificacion_global` es una calificación de 0 a 100 de todo el procedimiento y `resumen_general` \
explica en 2-4 frases los problemas principales. Responde todo en español, en tono profesional y \
constructivo. Devuelve el feedback individual de cada una de las 9 secciones usando exactamente sus \
llaves."""


# ───────────────────────────── Cliente / errores ───────────────────────────

class AIAuditError(Exception):
    """Error controlado del servicio de IA (mensaje apto para mostrar al usuario)."""


@dataclass
class AIAuditResponse:
    result: AuditResult
    raw_json: dict
    model: str
    input_tokens: int
    output_tokens: int


_client: anthropic.Anthropic | None = None


def _get_client() -> anthropic.Anthropic:
    """Cliente perezoso y reutilizable (lee ANTHROPIC_API_KEY del entorno)."""
    global _client
    if _client is None:
        _client = anthropic.Anthropic(timeout=600.0, max_retries=2)
    return _client


# ───────────────────────────── Función principal ───────────────────────────

def audit_procedure_markdown(markdown: str) -> AIAuditResponse:
    """
    Envía el Markdown del procedimiento a Claude y devuelve el feedback
    estructurado por sección.

    Lanza `AIAuditError` si la API falla, rechaza la petición o la
    respuesta no se puede validar.
    """
    settings = get_settings()

    try:
        response = _get_client().beta.messages.parse(
            model=settings.ai_model,
            max_tokens=16000,
            system=SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": (
                        "Audita el siguiente procedimiento (archivo procedimiento.md):\n\n"
                        f"<procedimiento_md>\n{markdown}\n</procedimiento_md>"
                    ),
                }
            ],
            thinking={"type": "adaptive"},
            output_config={"effort": settings.ai_effort},
            output_format=AuditResult,
            # Si un clasificador de seguridad rechaza la petición, la API la
            # re-ejecuta en un modelo de respaldo dentro de la misma llamada.
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
        )
    except anthropic.AuthenticationError as exc:
        raise AIAuditError("API key de Anthropic inválida o ausente (ANTHROPIC_API_KEY).") from exc
    except anthropic.RateLimitError as exc:
        raise AIAuditError("Límite de peticiones a la IA alcanzado; intenta de nuevo en un momento.") from exc
    except anthropic.BadRequestError as exc:
        raise AIAuditError(f"Petición rechazada por la IA: {exc.message}") from exc
    except anthropic.APIStatusError as exc:
        raise AIAuditError(f"Error del servicio de IA ({exc.status_code}).") from exc
    except anthropic.APIConnectionError as exc:
        raise AIAuditError("No fue posible conectar con el servicio de IA.") from exc
    except TypeError as exc:  # el SDK lo lanza cuando no encuentra ninguna credencial
        raise AIAuditError(f"No hay credenciales de Anthropic configuradas (ANTHROPIC_API_KEY): {exc}") from exc
    except ValueError as exc:  # JSON que no valida contra AuditResult
        raise AIAuditError(f"La IA devolvió un JSON inválido: {exc}") from exc

    # Revisar el motivo de paro ANTES de leer el contenido.
    if response.stop_reason == "refusal":
        raise AIAuditError("La IA declinó analizar este contenido.")
    if response.stop_reason == "max_tokens":
        raise AIAuditError("La respuesta de la IA se cortó por longitud; reduce el texto o reintenta.")

    result = response.parsed_output
    if result is None:
        raise AIAuditError("La IA no devolvió un JSON interpretable.")

    return AIAuditResponse(
        result=result,
        raw_json=result.model_dump(),
        model=response.model,
        input_tokens=response.usage.input_tokens,
        output_tokens=response.usage.output_tokens,
    )
