"""
cola_repo.py
============
Repositorio de lectura para rm_cola_revision.

Solo lectura — los writes y deletes los hacen
los event handlers al recibir DiagnosticoSugeridoPorIA,
DiagnosticoValidado y DiagnosticoRechazado.
"""

from uuid import UUID

from sqlalchemy.orm import Session

from app.infrastructure.database.models.read_models.rm_cola import (
    RMColaRevisionORM,
)

class RMColaRevisionRepository:
    """
    Repositorio de lectura para la cola de diagnósticos pendientes.

    Lee desde rm_cola_revision — tabla que contiene exactamente
    los diagnósticos que un odontólogo debe revisar.
    Se inserta al crear un diagnóstico y se borra al validar/rechazar.
    """

    def __init__(self, db: Session) -> None:
        self._db = db

    def get_pendientes(
        self,
        solo_segunda_opinion: bool = False,
        limit: int = 20,
        offset: int = 0,
    ) -> list[RMColaRevisionORM]:
        """
        Retorna los diagnósticos pendientes de revisión.

        Parameters
        ----------
        solo_segunda_opinion : bool
            Si True, filtra solo casos con segunda_opinion=True
            (confianza BAJA — requieren atención prioritaria).
        limit : int
            Máximo de registros a retornar.
        offset : int
            Desplazamiento para paginación.

        Returns
        -------
        list[RMColaRevisionORM]
            Lista de entradas de la cola, más antiguas primero
            (orden de llegada — FIFO).
        """
        q = self._db.query(RMColaRevisionORM)

        if solo_segunda_opinion:
            q = q.filter(RMColaRevisionORM.segunda_opinion == True)

        return (
            q.order_by(RMColaRevisionORM.fecha_generacion.asc())
            .limit(limit)
            .offset(offset)
            .all()
        )

    def get_by_diagnostico_id(
        self,
        diagnostico_id: UUID,
    ) -> RMColaRevisionORM | None:
        """
        Retorna la entrada de la cola para un diagnóstico específico.

        Parameters
        ----------
        diagnostico_id : UUID
            ID del diagnóstico.

        Returns
        -------
        RMColaRevisionORM | None
            Entrada de la cola si existe, None si ya fue procesado.
        """
        return (
            self._db.query(RMColaRevisionORM)
            .filter(RMColaRevisionORM.diagnostico_id == diagnostico_id)
            .first()
        )

    def count_pendientes(self, solo_segunda_opinion: bool = False) -> int:
        """
        Cuenta el total de diagnósticos pendientes en la cola.

        Parameters
        ----------
        solo_segunda_opinion : bool
            Si True, cuenta solo los casos prioritarios.

        Returns
        -------
        int
            Total de diagnósticos pendientes.
        """
        q = self._db.query(RMColaRevisionORM)
        if solo_segunda_opinion:
            q = q.filter(RMColaRevisionORM.segunda_opinion == True)
        return q.count()

    def get_por_paciente(
        self,
        paciente_id: UUID,
    ) -> list[RMColaRevisionORM]:
        """
        Retorna las entradas de la cola para un paciente específico.

        Útil para verificar si un paciente ya tiene diagnósticos pendientes
        antes de crear nuevos estudios.

        Parameters
        ----------
        paciente_id : UUID
            ID del paciente.

        Returns
        -------
        list[RMColaRevisionORM]
            Lista de entradas de la cola del paciente.
        """
        return (
            self._db.query(RMColaRevisionORM)
            .filter(RMColaRevisionORM.paciente_id == paciente_id)
            .order_by(RMColaRevisionORM.fecha_generacion.asc())
            .all()
        )