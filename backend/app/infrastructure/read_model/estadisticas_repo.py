"""
estadisticas_repo.py
====================
Repositorio de lectura para rm_estadisticas_modelo.

Solo lectura — los writes los hacen los event handlers
al recibir DiagnosticoValidado y DiagnosticoRechazado.
"""

from uuid import UUID

from sqlalchemy.orm import Session

from app.infrastructure.database.models.read_models.rm_estadisticas import (
    RMEstadisticasModeloORM,
)

class RMEstadisticasModeloRepository:
    """
    Repositorio de lectura para estadísticas de modelos ML en producción.

    Lee desde rm_estadisticas_modelo — tabla que acumula métricas
    reales calculadas sobre diagnósticos validados por odontólogos.
    Complementa las métricas de entrenamiento (f1, precision, recall)
    con métricas de uso real en producción.
    """

    def __init__(self, db: Session) -> None:
        self._db = db

    def get_by_modelo_id(
        self,
        modelo_ml_id: UUID,
    ) -> RMEstadisticasModeloORM | None:
        """
        Retorna las estadísticas de producción de un modelo específico.

        Parameters
        ----------
        modelo_ml_id : UUID
            ID del modelo en la tabla modelos_ml.

        Returns
        -------
        RMEstadisticasModeloORM | None
            Estadísticas del modelo si existen, None si el modelo
            no ha generado diagnósticos aún.
        """
        return (
            self._db.query(RMEstadisticasModeloORM)
            .filter(RMEstadisticasModeloORM.modelo_ml_id == modelo_ml_id)
            .first()
        )

    def get_all(self) -> list[RMEstadisticasModeloORM]:
        """
        Retorna las estadísticas de producción de todos los modelos.

        Ordenadas por nombre de modelo para consistencia en la UI.

        Returns
        -------
        list[RMEstadisticasModeloORM]
            Lista de estadísticas por modelo.
        """
        return (
            self._db.query(RMEstadisticasModeloORM)
            .order_by(RMEstadisticasModeloORM.nombre_modelo)
            .all()
        )

    def get_mejor_modelo(self) -> RMEstadisticasModeloORM | None:
        """
        Retorna el modelo con mayor tasa de validación en producción.

        Útil para el dashboard — muestra qué modelo están validando
        más los odontólogos en la práctica clínica real.

        Returns
        -------
        RMEstadisticasModeloORM | None
            El modelo con mayor tasa_validacion, None si no hay datos.
        """
        return (
            self._db.query(RMEstadisticasModeloORM)
            .filter(RMEstadisticasModeloORM.total_diagnosticos > 0)
            .order_by(RMEstadisticasModeloORM.tasa_validacion.desc())
            .first()
        )