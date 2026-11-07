"""
repository.py
=============
Interfaz del repositorio del Bounded Context: Gestión de Pacientes.

Solo define el contrato. La implementación real va en:
infrastructure/repositories/paciente_repo.py
"""

from abc import ABC, abstractmethod
from typing import Optional

from app.domain.pacientes.entities import Paciente
from app.domain.pacientes.value_objects import DNI, PacienteId


class IPacienteRepository(ABC):
    """
    Interfaz del repositorio de Pacientes.

    Define el contrato que debe cumplir cualquier implementación
    de persistencia para el agregado Paciente.
    Síncrona — usa SQLAlchemy síncrono con FastAPI.
    """

    @abstractmethod
    def save(self, paciente: Paciente) -> None:
        """
        Persiste un paciente (INSERT o UPDATE).

        Parameters
        ----------
        paciente : Paciente
            Instancia del agregado a persistir.
        """
        ...

    @abstractmethod
    def get_by_id(self, paciente_id: PacienteId) -> Optional[Paciente]:
        """
        Obtiene un paciente por su ID.

        Parameters
        ----------
        paciente_id : PacienteId
            Identificador único del paciente.

        Returns
        -------
        Optional[Paciente]
            El paciente si existe, None si no.
        """
        ...

    @abstractmethod
    def get_by_dni(self, dni: DNI) -> Optional[Paciente]:
        """
        Obtiene un paciente por su DNI.

        Parameters
        ----------
        dni : DNI
            Value Object DNI del paciente.

        Returns
        -------
        Optional[Paciente]
            El paciente si existe, None si no.
        """
        ...

    @abstractmethod
    def exists_by_dni(self, dni: DNI) -> bool:
        """
        Verifica si ya existe un paciente con ese DNI.

        Parameters
        ----------
        dni : DNI
            Value Object DNI a verificar.

        Returns
        -------
        bool
            True si el DNI ya está registrado.
        """
        ...

    @abstractmethod
    def list_activos(self, limit: int = 50, offset: int = 0) -> list[Paciente]:
        """
        Lista pacientes en estado ACTIVO ordenados por apellido.

        Parameters
        ----------
        limit : int
            Máximo de registros a retornar.
        offset : int
            Desplazamiento para paginación.

        Returns
        -------
        list[Paciente]
            Lista de pacientes activos.
        """
        ...