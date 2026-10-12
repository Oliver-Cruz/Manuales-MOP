"""
Configuración central de la aplicación.

Los valores se leen de variables de entorno (o de un archivo `.env` en la
carpeta `backend/`). Así el mismo código corre en local con SQLite y en
producción con PostgreSQL sin tocar una sola línea.
"""
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Base de datos: SQLite por defecto, PostgreSQL vía DATABASE_URL.
    database_url: str = "sqlite:///./manuales_mop.db"

    # IA (Anthropic Claude). La API key se lee de ANTHROPIC_API_KEY
    # directamente por el SDK; aquí sólo configuramos modelo y esfuerzo.
    ai_model: str = "claude-opus-5-5"
    # Profundidad de análisis: low | medium | high | xhigh | max
    ai_effort: str = "high"

    # Carpeta donde se guarda cada procedimiento empaquetado como .md
    # (queda como evidencia de lo que se envió a la IA en cada auditoría).
    markdown_dir: Path = Path("./data/markdown")


@lru_cache
def get_settings() -> Settings:
    return Settings()
