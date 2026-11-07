"""
repository.py
=============
Interfaces de repositorios del Bounded Context: Diagnóstico Asistido por IA.

Solo define contratos. Las implementaciones van en:
infrastructure/repositories/diagnostico_repo.py
infrastructure/repositories/odontologo_repo.py
"""

from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from app.domain.diagnosticos.entities import Diagnostico, Odontologo
from app.domain.diagnosticos.value_objects import DiagnosticoId
from app.domain.estudios.value_objects import EstudioId
from app.domain.pacientes.value_objects import PacienteId

class IDiagnosticoRepository(ABC):
    """
    Interfaz del repositorio de Diagnósticos.

    Síncrona — usa SQLAlchemy síncrono con FastAPI.
    """

    @abstractmethod
    def save(self, diagnostico: Diagnostico) -> None:
        """
        Persiste un diagnóstico y sus hallazgos (INSERT o UPDATE).

        Parameters
        ----------
        diagnostico : Diagnostico
            Instancia del agregado a persistir.
        """
        ...

    @abstractmethod
    def get_by_id(self, diagnostico_id: DiagnosticoId) -> Optional[Diagnostico]:
        """
        Obtiene un diagnóstico por su ID, incluyendo sus hallazgos.

        Parameters
        ----------
        diagnostico_id : DiagnosticoId
            Identificador único del diagnóstico.

        Returns
        -------
        Optional[Diagnostico]
            El diagnóstico si existe, None si no.
        """
        ...

    @abstractmethod
    def get_by_estudio_id(self, estudio_id: EstudioId) -> list[Diagnostico]:
        """
        Obtiene los diagnósticos asociados a un estudio.

        Parameters
        ----------
        estudio_id : EstudioId
            ID del estudio imagenológico.

        Returns
        -------
        list[Diagnostico]
            Lista de diagnósticos del estudio. Vacía si no tiene ninguno.
        """
        ...

    @abstractmethod
    def get_pendientes_revision(self, limit: int = 20) -> list[Diagnostico]:
        """
        Obtiene diagnósticos en estado SUGERIDO_IA.

        Usado para poblar la cola de revisión.

        Parameters
        ----------
        limit : int
            Máximo de registros a retornar.

        Returns
        -------
        list[Diagnostico]
            Lista de diagnósticos pendientes de revisión.
        """
        ...

    @abstractmethod
    def get_by_paciente_id(
        self,
        paciente_id: PacienteId,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Diagnostico]:
        """
        Obtiene diagnósticos de un paciente ordenados por fecha.

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
        list[Diagnostico]
            Lista de diagnósticos del paciente.
        """
        ...


class IOdontologoRepository(ABC):
    """
    Interfaz del repositorio de Odontólogos.

    Síncrona — usa SQLAlchemy síncrono con FastAPI.
    """

    @abstractmethod
    def get_by_id(self, odontologo_id: UUID) -> Optional[Odontologo]:
        """
        Obtiene un odontólogo por su ID.

        Parameters
        ----------
        odontologo_id : UUID
            Identificador único del odontólogo.

        Returns
        -------
        Optional[Odontologo]
            El odontólogo si existe, None si no.
        """
        ...

    @abstractmethod
    def get_by_colegiatura(self, numero_colegiatura: str) -> Optional[Odontologo]:
        """
        Obtiene un odontólogo por su número de colegiatura.

        Parameters
        ----------
        numero_colegiatura : str
            Número de colegiatura profesional.

        Returns
        -------
        Optional[Odontologo]
            El odontólogo si existe, None si no.
        """
        ...

    @abstractmethod
    def list_autorizados(self) -> list[Odontologo]:
        """
        Lista odontólogos habilitados para validar diagnósticos.

        Returns
        -------
        list[Odontologo]
            Lista de odontólogos con autorizado_validar=True.
        """
        ...