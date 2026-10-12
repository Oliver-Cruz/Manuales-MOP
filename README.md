# Manuales-MOP

Sistema inteligente de auditoría de procedimientos para apoyar a las distintas áreas con sus manuales de operación.

Pantalla tipo "pizarrón": **izquierda** el usuario captura las 9 secciones del procedimiento, **derecha** la IA devuelve un feedback espejo por sección (qué cumple, qué falta, inconsistencias y redacción sugerida).

## Flujo

```
Frontend (index.html)                    Backend (FastAPI)                         IA (Claude)
─────────────────────                    ─────────────────                         ───────────
Captura 9 secciones + Área ──POST/PUT──► Guarda en BD (procedimientos.area_id NOT NULL)
                                         Empaqueta lado izquierdo en procedimiento_N.md
                                         Envía el .md + system prompt de auditor ───► Analiza sección por sección
                                         Valida JSON (9 secciones)  ◄───────────────── JSON estructurado
                                         Escribe feedback_<sección> + historial
Pinta feedback por sección ◄── JSON ──── Responde ProcedimientoOut
(colorea el input: cumple/parcial/no cumple/vacía; botón "Usar sugerencia en el texto")
```

## Estructura

```
backend/
  app/
    config.py                 # variables de entorno (.env)
    database.py               # engine / sesión SQLAlchemy
    sections.py               # catálogo único de las 9 secciones
    models.py                 # Area, Procedimiento (9 inputs + 9 feedbacks), Auditoria (historial)
    schemas.py                # Pydantic: API + esquema JSON que devuelve la IA
    services/
      markdown_builder.py     # Procedimiento → .md
      ai_auditor.py           # .md → Claude → AuditResult (JSON validado)
      audit_flow.py           # orquesta: md → IA → BD
    routers/
      areas.py
      procedimientos.py       # POST /api/procedimientos (dispara todo el flujo)
    main.py
  requirements.txt
  .env.example
frontend/
  index.html                  # HTML + Tailwind + JS vanilla
```

## Ejecutar

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # coloca tu ANTHROPIC_API_KEY
uvicorn app.main:app --reload
```

- Pantalla: http://localhost:8000/
- API interactiva: http://localhost:8000/docs

Para PostgreSQL instala `psycopg[binary]` y define `DATABASE_URL=postgresql+psycopg://usuario:pass@host:5432/manuales_mop`.

## Endpoints

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/api/sections` | Catálogo de las 9 secciones (el frontend arma las filas con él) |
| GET/POST | `/api/areas` | Listar / crear áreas |
| GET | `/api/procedimientos?area_id=` | Listado |
| GET | `/api/procedimientos/{id}` | Captura + feedback |
| **POST** | `/api/procedimientos` | **Guarda y dispara la auditoría con IA** (`?auditar=false` para sólo guardar) |
| PUT | `/api/procedimientos/{id}` | Guarda correcciones y re-audita |
| POST | `/api/procedimientos/{id}/auditar` | Re-audita sin cambios |

Si la IA falla, el procedimiento **sí** se guarda; la respuesta trae `estado_auditoria: "error"` y `error_auditoria`.

## JSON que devuelve la IA (por sección)

```json
{
  "objetivo": {
    "estado": "parcial",
    "comentario": "El objetivo describe la actividad pero no el resultado esperado.",
    "faltantes": ["Indicar a quién beneficia", "Hacerlo medible"],
    "inconsistencias": ["Menciona 'conciliación' pero ninguna actividad la realiza"],
    "sugerencia": "Pagar en tiempo y forma a los proveedores ..."
  },
  "descripcion_actividades": { "...": "..." },
  "resumen_general": "…",
  "calificacion_global": 62
}
```

Se usa *structured outputs* del SDK de Anthropic (`output_format=AuditResult`), así que la respuesta llega ya validada contra el esquema Pydantic.

## Guía del frontend: Input frente a Feedback

1. Cada sección es **una fila** (`<article class="grid lg:grid-cols-2">`) con dos hijos: el input (izquierda) y el feedback (derecha). Al estar en la misma fila del grid, siempre quedan alineados aunque un feedback sea más largo; en móvil se apilan.
2. Las filas se generan desde `GET /api/sections` con un `<template>`; agregar una sección en `sections.py` la agrega a la pantalla.
3. `rowsByKey[key]` guarda las referencias `{input, feedback, card}` para que `renderFeedback(key, fb)` pinte cada respuesta en su cuadro espejo.
4. El dictamen colorea también el borde del input (verde/ámbar/rojo) para señalar al usuario qué corregir; el botón **"Usar sugerencia en el texto"** regresa la redacción de la IA al cuadro de captura.
5. Al guardar se muestra un spinner en las 9 tarjetas derechas hasta que llega la respuesta.
