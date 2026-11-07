"""
events.py
=========
Domain Events del Bounded Context: Gestión de Inferencias IA.
"""

from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from app.domain.shared.domain_event import DomainEvent

@dataclass
class InferenciaIniciada(DomainEvent):
    """
    Evento emitido cuando el worker comienza a procesar la inferencia.

    Attributes
    ----------
    inferencia_id : UUID
        ID de la inferencia iniciada.
    estudio_id : UUID
        ID del estudio que se está analizando.
    modelo_ml_id : UUID
        ID del modelo ML que ejecuta la inferencia.
    worker_id : str
        Identificador del worker que tomó la tarea.
    """
    inferencia_id: UUID
    estudio_id: UUID
    modelo_ml_id: UUID
    worker_id: str

    def __init__(
        self,
        inferencia_id: UUID,
        estudio_id: UUID,
        modelo_ml_id: UUID,
        worker_id: str,
    ) -> None:
        super().__init__()
        self.inferencia_id = inferencia_id
        self.estudio_id = estudio_id
        self.modelo_ml_id = modelo_ml_id
        self.worker_id = worker_id


@dataclass
class InferenciaCompletada(DomainEvent):
    """
    Evento emitido cuando la inferencia termina exitosamente.

    Attributes
    ----------
    inferencia_id : UUID
        ID de la inferencia completada.
    estudio_id : UUID
        ID del estudio analizado.
    modelo_ml_id : UUID
        ID del modelo ML usado.
    tiempo_ms : float
        Tiempo total de inferencia en milisegundos.
    """
    inferencia_id: UUID
    estudio_id: UUID
    modelo_ml_id: UUID
    tiempo_ms: float

    def __init__(
        self,
        inferencia_id: UUID,
        estudio_id: UUID,
        modelo_ml_id: UUID,
        tiempo_ms: float,
    ) -> None:
        super().__init__()
        self.inferencia_id = inferencia_id
        self.estudio_id = estudio_id
        self.modelo_ml_id = modelo_ml_id
        self.tiempo_ms = tiempo_ms


@dataclass
class InferenciaFallida(DomainEvent):
    """
    Evento emitido cuando la inferencia falla durante su ejecución.

    Attributes
    ----------
    inferencia_id : UUID
        ID de la inferencia fallida.
    estudio_id : UUID
        ID del estudio que no pudo ser analizado.
    modelo_ml_id : UUID
        ID del modelo ML que falló.
    error_mensaje : str
        Descripción del error ocurrido.
    """
    inferencia_id: UUID
    estudio_id: UUID
    modelo_ml_id: UUID
    error_mensaje: str

    def __init__(
        self,
        inferencia_id: UUID,
        estudio_id: UUID,
        modelo_ml_id: UUID,
        error_mensaje: str,
    ) -> None:
        super().__init__()
        self.inferencia_id = inferencia_id
        self.estudio_id = estudio_id
        self.modelo_ml_id = modelo_ml_id
        self.error_mensaje = error_mensaje