"""
inferencias.py
==============
Router FastAPI para el recurso Inferencia.

Endpoints:
    GET /inferencias/{id} → estado de una inferencia
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.schemas.inferencia_schemas import InferenciaResponse
from app.core.config.dependencies import get_inferencia_repository
from app.domain.inferencias.value_objects import InferenciaId
from app.infrastructure.repositories.inferencia_repo import SQLAlchemyInferenciaRepository

router = APIRouter(prefix="/inferencias", tags=["Inferencias"])


@router.get(
    "/{inferencia_id}",
    response_model=InferenciaResponse,
    summary="Obtener estado de una inferencia",
)
def obtener_inferencia(
    inferencia_id: UUID,
    repo: SQLAlchemyInferenciaRepository = Depends(get_inferencia_repository),
):
    """
    Retorna el estado actual de una inferencia IA.

    Útil para que el frontend haga polling del estado del pipeline
    mientras el worker procesa la tarea.

    Parameters
    ----------
    inferencia_id : UUID
        ID de la inferencia.

    Returns
    -------
    InferenciaResponse
        Estado actual de la inferencia.

    Raises
    ------
    HTTPException 404
        Si la inferencia no existe.
    """
    inferencia = repo.get_by_id(InferenciaId(inferencia_id))
    if inferencia is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inferencia con ID '{inferencia_id}' no encontrada.",
        )
    return InferenciaResponse(
        id=inferencia.id,
        estudio_id=inferencia.estudio_id,
        modelo_ml_id=inferencia.modelo_ml_id,
        estado=inferencia.estado.value,
        worker_id=inferencia.worker_id.value if inferencia.worker_id else None,
        gpu_utilizada=inferencia.gpu_utilizada,
        tiempo_ms=inferencia.tiempo_inferencia.valor_ms if inferencia.tiempo_inferencia else None,
        error_mensaje=inferencia.error_mensaje,
        created_at=inferencia.created_at,
        completed_at=inferencia.completed_at,
    )