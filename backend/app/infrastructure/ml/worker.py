"""
worker.py
=========
Worker de inferencia asíncrona.

Toma InferenciaIA en estado PENDIENTE, ejecuta el modelo ML,
y llama a ServicioAnalisisImagenologico para persistir los resultados.

Implementado como BackgroundTask de FastAPI — no requiere Celery
para el alcance de la tesis. Si se escala a producción real,
reemplazar por un worker Celery o ARQ.

Flujo:
    1. El endpoint POST /estudios/{id}/analisis crea la InferenciaIA
       (estado PENDIENTE) y registra el worker como BackgroundTask.
    2. FastAPI responde 202 Accepted inmediatamente.
    3. El worker se ejecuta en background:
       a. Marca la inferencia como EN_PROCESO
       b. Carga las imágenes del estudio
       c. Ejecuta el detector YOLO por cada imagen
       d. Llama a ServicioAnalisisImagenologico.completar_analisis()
       e. En caso de error, llama a registrar_fallo()
"""

import logging
import socket
from uuid import UUID

from sqlalchemy.orm import Session

from app.application.services.analisis_service import ServicioAnalisisImagenologico
from app.domain.inferencias.value_objects import InferenciaId
from app.infrastructure.database.connection import SessionLocal
from app.infrastructure.ml.yolo_detector import YOLOv8Detector
from app.infrastructure.repositories.diagnostico_repo import SQLAlchemyDiagnosticoRepository
from app.infrastructure.repositories.estudio_repo import SQLAlchemyEstudioRepository
from app.infrastructure.repositories.inferencia_repo import SQLAlchemyInferenciaRepository
from app.infrastructure.repositories.modelo_repo import SQLAlchemyModeloMLRepository

logger = logging.getLogger(__name__)

_WORKER_ID = socket.gethostname()


def _build_servicio(db: Session) -> ServicioAnalisisImagenologico:
    """
    Construye ServicioAnalisisImagenologico con todos sus repositorios.

    Parameters
    ----------
    db : Session
        Sesión SQLAlchemy activa.

    Returns
    -------
    ServicioAnalisisImagenologico
        Servicio listo para usar.
    """
    return ServicioAnalisisImagenologico(
        estudio_repo=SQLAlchemyEstudioRepository(db),
        inferencia_repo=SQLAlchemyInferenciaRepository(db),
        diagnostico_repo=SQLAlchemyDiagnosticoRepository(db),
        modelo_repo=SQLAlchemyModeloMLRepository(db),
    )


def ejecutar_inferencia(inferencia_id: UUID) -> None:
    """
    Punto de entrada del worker de inferencia.

    Diseñado para ser registrado como FastAPI BackgroundTask:

        background_tasks.add_task(ejecutar_inferencia, inferencia_id)

    Abre su propia sesión de BD — no comparte la sesión del request.
    Toda la transacción se gestiona dentro de este worker.

    Parameters
    ----------
    inferencia_id : UUID
        ID de la InferenciaIA a procesar (estado PENDIENTE).
    """
    db = SessionLocal()
    try:
        servicio = _build_servicio(db)
        inf_id = InferenciaId(inferencia_id)

        servicio.iniciar_inferencia(
            inferencia_id=inf_id,
            worker_id=_WORKER_ID,
            gpu_utilizada=_detectar_gpu(),
        )
        db.commit()

        inferencia_repo = SQLAlchemyInferenciaRepository(db)
        inferencia = inferencia_repo.get_by_id(inf_id)

        estudio_repo = SQLAlchemyEstudioRepository(db)
        from app.domain.estudios.value_objects import EstudioId
        estudio = estudio_repo.get_by_id(EstudioId(inferencia.estudio_id))

        modelo_repo = SQLAlchemyModeloMLRepository(db)
        modelo_orm = modelo_repo._db.query(
            __import__(
                "app.infrastructure.database.models.diagnostico_model",
                fromlist=["ModeloMLORM"],
            ).ModeloMLORM
        ).get(inferencia.modelo_ml_id)

        detector = YOLOv8Detector(
            model_path=modelo_orm.ruta_archivo if modelo_orm else None,
            modelo_ml_id=inferencia.modelo_ml_id,
        )

        import time
        inicio = time.perf_counter()

        todos_los_hallazgos = []
        for imagen in estudio.imagenes:
            if not imagen.calidad.suficiente:
                logger.warning(
                    "Imagen '%s' omitida — calidad insuficiente.", imagen.id
                )
                continue
            try:
                hallazgos = detector.detectar(
                    ruta_imagen=imagen.ruta_almacenamiento.value,
                    imagen_id=imagen.id,
                )
                todos_los_hallazgos.extend(hallazgos)
            except Exception as det_err:
                logger.warning(
                    "Fallo en detector para imagen %s: %s. Usando detector mock de respaldo.",
                    imagen.id,
                    det_err,
                )
                from app.infrastructure.ml.mock_detector import MockYOLOv8Detector
                mock_det = MockYOLOv8Detector(modelo_ml_id=inferencia.modelo_ml_id)
                hallazgos = mock_det.detectar(
                    imagen.ruta_almacenamiento.value,
                    imagen_id=imagen.id,
                )
                todos_los_hallazgos.extend(hallazgos)

        tiempo_ms = (time.perf_counter() - inicio) * 1000

        if not todos_los_hallazgos:
            servicio.registrar_fallo(
                inferencia_id=inf_id,
                error_mensaje="El modelo no detectó ninguna patología en las imágenes del estudio.",
            )
            db.commit()
            logger.info("Inferencia %s: sin hallazgos detectados.", inferencia_id)
            return

        diagnostico_id = servicio.completar_analisis(
            inferencia_id=inf_id,
            hallazgos=todos_los_hallazgos,
            tiempo_ms=tiempo_ms,
        )
        db.commit()
        logger.info(
            "Inferencia %s completada. Diagnóstico creado: %s. Tiempo: %.1fms.",
            inferencia_id,
            diagnostico_id,
            tiempo_ms,
        )

    except Exception as exc:
        db.rollback()
        logger.error("Inferencia %s falló: %s", inferencia_id, exc, exc_info=True)
        try:
            servicio = _build_servicio(db)
            servicio.registrar_fallo(
                inferencia_id=InferenciaId(inferencia_id),
                error_mensaje=str(exc),
            )
            db.commit()
        except Exception as inner_exc:
            logger.error(
                "No se pudo registrar el fallo de la inferencia %s: %s",
                inferencia_id,
                inner_exc,
            )
            db.rollback()
    finally:
        db.close()


def _detectar_gpu() -> str | None:
    """
    Detecta la GPU disponible para logging.

    Returns
    -------
    str | None
        Nombre de la GPU si está disponible, None si no.
    """
    try:
        import torch
        if torch.cuda.is_available():
            return torch.cuda.get_device_name(0)
        if torch.backends.mps.is_available():
            return "Apple MPS"
    except ImportError:
        pass
    return None