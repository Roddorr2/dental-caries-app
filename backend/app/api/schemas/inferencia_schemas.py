"""
inferencia_schemas.py
=====================
DTOs Pydantic para el recurso Inferencia.

InferenciaResponse       → response body GET /inferencias/{id}
SolicitarAnalisisRequest → request body POST /estudios/{id}/analisis
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

class InferenciaResponse(BaseModel):
    """
    Response body para el estado de una inferencia IA.

    Attributes
    ----------
    id : UUID
        Identificador único de la inferencia.
    estudio_id : UUID
        ID del estudio analizado.
    modelo_ml_id : UUID
        ID del modelo ML que ejecutó la inferencia.
    estado : str
        Estado: PENDIENTE | EN_PROCESO | COMPLETADO | FALLIDO.
    worker_id : str | None
        Worker que ejecutó la inferencia. None si aún no inició.
    gpu_utilizada : str | None
        GPU usada. None si no aplica.
    tiempo_ms : float | None
        Tiempo de ejecución en milisegundos. None hasta completar.
    error_mensaje : str | None
        Mensaje de error. None si no falló.
    created_at : datetime
        Timestamp de creación.
    completed_at : datetime | None
        Timestamp de finalización. None hasta completar o fallar.
    """

    id: UUID
    estudio_id: UUID
    modelo_ml_id: UUID
    estado: str
    worker_id: str | None = None
    gpu_utilizada: str | None = None
    tiempo_ms: float | None = None
    error_mensaje: str | None = None
    created_at: datetime
    completed_at: datetime | None = None

    model_config = {"from_attributes": True}


class SolicitarAnalisisRequest(BaseModel):
    """
    Request body para solicitar análisis IA sobre un estudio.

    Attributes
    ----------
    modelo_ml_id : UUID | None
        ID del modelo ML que ejecutará la inferencia. Si no se especifica,
        el CDSS utiliza automáticamente el modelo detector aprobado para producción.
    """

    modelo_ml_id: UUID | None = None