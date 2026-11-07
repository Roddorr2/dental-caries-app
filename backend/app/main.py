"""
main.py
=======
Entry point del backend — dental-app.

Sistema de Apoyo al Diagnóstico Odontológico con ML/DL.

Configura:
- Aplicación FastAPI con metadata
- CORS middleware
- Routers de la API
- Verificación de BD al startup
- Health check endpoint

Autor: Rodrigo
Versión: 1.0 — Abril 2026
"""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import diagnosticos, estudios, inferencias, modelos, pacientes
from app.core.config.settings import Settings

logging.basicConfig(
    level=logging.DEBUG if Settings.DEBUG else logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Dental App — Sistema de Apoyo al Diagnóstico Odontológico",
    description=(
        "API REST con ML/DL para detección de patologías dentales intraorales. "
        "Arquitectura DDD + CQRS. Modelos: YOLOv8n (producción), "
        "SVM/RF con HOG+LBP (comparación)."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    contact={"name": "Rodrigo"},
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=Settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(pacientes.router,    prefix=Settings.API_V1_PREFIX)
app.include_router(estudios.router,     prefix=Settings.API_V1_PREFIX)
app.include_router(diagnosticos.router, prefix=Settings.API_V1_PREFIX)
app.include_router(inferencias.router,  prefix=Settings.API_V1_PREFIX)
app.include_router(modelos.router,      prefix=Settings.API_V1_PREFIX)


@app.on_event("startup")
def on_startup() -> None:
    """
    Ejecutado al arrancar el servidor.

    Verifica la conexión a PostgreSQL y registra
    las URLs disponibles en los logs.
    """
    logger.info("Arrancando dental-app backend v%s...", app.version)

    try:
        from sqlalchemy import text
        from app.infrastructure.database.connection import engine
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Conexión a PostgreSQL: OK")
    except Exception as e:
        logger.error("No se pudo conectar a PostgreSQL: %s", e)
        raise

    logger.info(
        "Endpoints disponibles en: http://localhost:8000%s",
        Settings.API_V1_PREFIX,
    )
    logger.info("Documentación: http://localhost:8000/docs")


@app.on_event("shutdown")
def on_shutdown() -> None:
    """Ejecutado al apagar el servidor."""
    logger.info("Apagando dental-app backend...")


@app.get("/health", tags=["Health"])
def health_check() -> dict:
    """
    Verifica que el servidor está corriendo.

    Returns
    -------
    dict
        Estado del servidor y versión.
    """
    return {
        "status": "ok",
        "version": app.version,
        "debug": Settings.DEBUG,
    }