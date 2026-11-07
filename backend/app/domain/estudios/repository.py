"""
repository.py
=============
Interfaz del repositorio del Bounded Context: Adquisición Imagenológica.

Solo define el contrato. La implementación real va en:
infrastructure/repositories/estudio_repo.py
"""

from abc import ABC, abstractmethod
from typing import Optional

from app.domain.estudios.entites import EstudioImagenologico
from app.domain.estudios.value_objects import EstudioId
from app.domain.pacientes.value_objects import PacienteId

class IEstudioRepository(ABC):
    """
    Interfaz del repositorio de Estudios Imagenológicos.

    Define el contrato que debe cumplir cualquier implementación
    de persistencia para el agregado EstudioImagenologico.
    Síncrona — usa SQLAlchemy síncrono con FastAPI.
    """

    @abstractmethod
    def save(self, estudio: EstudioImagenologico) -> None:
        """
        Persiste un estudio y sus imágenes (INSERT o UPDATE).

        Parameters
        ----------
        estudio : EstudioImagenologico
            Instancia del agregado a persistir.
        """
        ...

    @abstractmethod
    def get_by_id(self, estudio_id: EstudioId) -> Optional[EstudioImagenologico]:
        """
        Obtiene un estudio por su ID, incluyendo sus imágenes.

        Parameters
        ----------
        estudio_id : EstudioId
            Identificador único del estudio.

        Returns
        -------
        Optional[EstudioImagenologico]
            El estudio si existe, None si no.
        """
        ...

    @abstractmethod
    def get_by_paciente_id(
        self,
        paciente_id: PacienteId,
        limit: int = 20,
        offset: int = 0,
    ) -> list[EstudioImagenologico]:
        """
        Obtiene todos los estudios de un paciente.

        Parameters
        ----------
        paciente_id : PacienteId
            ID del paciente.
        limit : int
            Máximo de registros a retornar.
        offset : int
            Desplazamiento para paginación.

        Returns
        -------
        list[EstudioImagenologico]
            Lista de estudios del paciente. Vacía si no tiene ninguno.
        """
        ...

    @abstractmethod
    def get_pendientes(self, limit: int = 20) -> list[EstudioImagenologico]:
        """
        Obtiene estudios en estado PENDIENTE ordenados por fecha de creación.

        Parameters
        ----------
        limit : int
            Máximo de registros a retornar.

        Returns
        -------
        list[EstudioImagenologico]
            Lista de estudios pendientes.
        """
        ...

    @abstractmethod
    def exists_imagen_by_hash(self, hash_sha256: str) -> bool:
        """
        Verifica si ya existe una imagen con ese hash SHA-256.

        Usado para evitar duplicados en el dataset.

        Parameters
        ----------
        hash_sha256 : str
            Hash SHA-256 de la imagen a verificar.

        Returns
        -------
        bool
            True si ya existe una imagen con ese hash.
        """
        ...