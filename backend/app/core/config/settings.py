"""
settings.py
===========
Variables de entorno del proyecto cargadas con Pydantic Settings.

Lee desde un archivo .env en la raíz del backend.
Falla explícitamente si faltan variables obligatorias.

Variables requeridas en .env:
    DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/dental_db
    SECRET_KEY=tu_clave_secreta_aqui
    MODEL_PATH=ml/models/best.pt

Variables opcionales (tienen defaults):
    DEBUG=False
    APP_NAME=Dental Diagnostic API
    API_V1_PREFIX=/api/v1
    ALLOWED_ORIGINS=http://localhost:3000
    MODEL_CONFIDENCE_THRESHOLD=0.25
    MAX_IMAGES_PER_STUDY=10
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    APP_NAME: str = Field(default="Dental Diagnostic API")
    DEBUG: bool = Field(default=False)
    API_V1_PREFIX: str = Field(default="/api/v1")

    DATABASE_URL: str = Field(
        ...,
        description="PostgreSQL connection string. Ejemplo: postgresql=psycopg2://user:pass@localhost:5321/dental_db",
    )

    SECRET_KEY: str = Field(
        ...,
        description="Clave secreta para JWT y operaciones criptográficas",
    )

    MODEL_PATH: str = Field(
        ...,
        description="Ruta relativa al modelo YOLO entrenado. Ejemplo ml/models/best.pt",
    )

    MODEL_CONFIDENCE_THRESHOLD: float = Field(
        default=0.40,
        ge=0.0,
        le=1.0,
        description="Umbral mínimo de confianza para aceptar una detección.",
    )

    ALLOWED_ORIGINS: str = Field(
        default="http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173",
        description="Orígenes permitidos para CORS, separados por comas",
    )
    
    @property
    def allowed_origins_list(self) -> list[str]:
        """Convierte la string de orígenes a lista para FastAPI CORSMiddleware"""
        origins = [
            origin.strip().rstrip("/")
            for origin in self.ALLOWED_ORIGINS.split(",")
            if origin.strip()
        ]
        if "*" in origins:
            raise ValueError(
                "ALLOWED_ORIGINS debe enumerar orígenes explícitos; "
                "no se permite '*' con credenciales habilitadas."
            )
        return origins

    MAX_IMAGES_PER_STUDY: int = Field(
        default=10,
        description="Máximo de imágenes permitidos por estudio imagenológico."
    )

SettingsClass = Settings
settings = Settings()
Settings = settings
