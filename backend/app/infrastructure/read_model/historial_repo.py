"""
historial_repo.py
=================
Repositorio de lectura para rm_historial_paciente.

Este repositorio es solo lectura — los writes los hacen
los event handlers en application/handlers/event_handlers.py.
La separación es intencional: write side usa el dominio,
read side usa el ORM directamente sin pasar por entidades.
"""

from uuid import UUID

from sqlalchemy.orm import Session

from app.infrastructure.database.models.read_models.rm_historial import (
    RMHistorialPacienteORM,
)

class RMHistorialPacienteRepository:
    """
    Repositorio de lectura para el historial clínico de pacientes.

    Lee exclusivamente desde rm_historial_paciente — tabla desnormalizada
    que evita JOINs complejos en las consultas frecuentes.
    """

    def __init__(self, db: Session) -> None:
        self._db = db

    def get_by_paciente_id(
        self,
        paciente_id: UUID,
        limit: int = 20,
        offset: int = 0,
    ) -> list[RMHistorialPacienteORM]:
        """
        Retorna el historial clínico de un paciente ordenado por fecha.

        Parameters
        ----------
        paciente_id : UUID
            ID del paciente.
        limit : int
            Máximo de registros a retornar.
        offset : int
            Desplazamiento para paginación.

        Returns
        -------
        list[RMHistorialPacienteORM]
            Lista de entradas del historial, más recientes primero.
        """
        return (
            self._db.query(RMHistorialPacienteORM)
            .filter(RMHistorialPacienteORM.paciente_id == paciente_id)
            .order_by(RMHistorialPacienteORM.fecha_estudio.desc())
            .limit(limit)
            .offset(offset)
            .all()
        )

    def get_by_diagnostico_id(
        self,
        diagnostico_id: UUID,
    ) -> RMHistorialPacienteORM | None:
        """
        Retorna la entrada del historial para un diagnóstico específico.

        Parameters
        ----------
        diagnostico_id : UUID
            ID del diagnóstico.

        Returns
        -------
        RMHistorialPacienteORM | None
            Entrada del historial si existe, None si no.
        """
        return (
            self._db.query(RMHistorialPacienteORM)
            .filter(RMHistorialPacienteORM.diagnostico_id == diagnostico_id)
            .first()
        )

    def count_by_paciente_id(self, paciente_id: UUID) -> int:
        """
        Cuenta el total de entradas del historial de un paciente.

        Útil para calcular el total de páginas en la paginación.

        Parameters
        ----------
        paciente_id : UUID
            ID del paciente.

        Returns
        -------
        int
            Total de entradas del historial.
        """
        return (
            self._db.query(RMHistorialPacienteORM)
            .filter(RMHistorialPacienteORM.paciente_id == paciente_id)
            .count()
        )