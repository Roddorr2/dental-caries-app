"""
repository.py
=============
Interfaz del repositorio del Bounded Context: Gestión de Inferencias IA.

Solo define el contrato. La implementación real va en:
infrastructure/repositories/inferencia_repo.py
"""

from abc import ABC, abstractmethod
from typing import Optional

from app.domain.inferencias.entities import InferenciaIA
from app.domain.inferencias.value_objects import InferenciaId
from app.domain.estudios.value_objects import EstudioId


class IInferenciaRepository(ABC):
    """
    Interfaz del repositorio de Inferencias IA.

    Define el contrato que debe cumplir cualquier implementación
    de persistencia para la entidad InferenciaIA.
    Síncrona — usa SQLAlchemy síncrono con FastAPI.
    """

    @abstractmethod
    def save(self, inferencia: InferenciaIA) -> None:
        """
        Persiste una inferencia (INSERT o UPDATE).

        Parameters
        ----------
        inferencia : InferenciaIA
            Instancia de la entidad a persistir.
        """
        ...

    @abstractmethod
    def get_by_id(self, inferencia_id: InferenciaId) -> Optional[InferenciaIA]:
        """
        Obtiene una inferencia por su ID.

        Parameters
        ----------
        inferencia_id : InferenciaId
            Identificador único de la inferencia.

        Returns
        -------
        Optional[InferenciaIA]
            La inferencia si existe, None si no.
        """
        ...

    @abstractmethod
    def get_by_estudio_id(self, estudio_id: EstudioId) -> list[InferenciaIA]:
        """
        Obtiene todas las inferencias de un estudio.

        Parameters
        ----------
        estudio_id : EstudioId
            ID del estudio asociado.

        Returns
        -------
        list[InferenciaIA]
            Lista de inferencias del estudio. Vacía si no tiene ninguna.
        """
        ...

    @abstractmethod
    def get_pendientes(self, limit: int = 10) -> list[InferenciaIA]:
        """
        Obtiene inferencias en estado PENDIENTE.

        Usado por el worker para tomar tareas de la cola.

        Parameters
        ----------
        limit : int
            Máximo de registros a retornar.

        Returns
        -------
        list[InferenciaIA]
            Lista de inferencias pendientes.
        """
        ...