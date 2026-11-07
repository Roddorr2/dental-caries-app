"""
modelo_schemas.py
=================
DTOs Pydantic para el recurso Modelo ML.

ModeloResponse       → response body GET /modelos
EstadisticasResponse → response body GET /modelos/{id}/estadisticas
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

class ModeloResponse(BaseModel):
    """
    Response body para un modelo ML registrado.

    Attributes
    ----------
    id : UUID
        Identificador único del modelo.
    nombre : str
        Nombre del modelo.
    version : str
        Versión del modelo.
    tipo : str
        Tipo: YOLO | SVM | RANDOM_FOREST | MOBILENET | EFFICIENTNET.
    f1_score : float
        F1-Score en el set de validación.
    precision_score : float
        Precision en el set de validación.
    recall_score : float
        Recall en el set de validación.
    aprobado_produccion : bool
        True si está habilitado para producción (f1 >= 0.85).
    created_at : datetime
        Timestamp de registro.
    """

    id: UUID
    nombre: str
    version: str
    tipo: str
    f1_score: float
    precision_score: float
    recall_score: float
    aprobado_produccion: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class EstadisticasResponse(BaseModel):
    """
    Response body para estadísticas de un modelo ML en producción.

    Calculadas sobre diagnósticos reales validados por odontólogos.

    Attributes
    ----------
    modelo_ml_id : UUID
        ID del modelo.
    nombre_modelo : str
        Nombre del modelo.
    version : str
        Versión del modelo.
    total_diagnosticos : int
        Total de diagnósticos generados.
    total_validados : int
        Total de diagnósticos validados por odontólogos.
    total_rechazados : int
        Total de diagnósticos rechazados.
    tasa_validacion : float
        Tasa de validación (validados / total).
    tasa_segunda_opinion : float
        Tasa de casos con confianza BAJA que requirieron segunda opinión.
    """

    modelo_ml_id: UUID
    nombre_modelo: str
    version: str
    total_diagnosticos: int
    total_validados: int
    total_rechazados: int
    tasa_validacion: float
    tasa_segunda_opinion: float

    model_config = {"from_attributes": True}