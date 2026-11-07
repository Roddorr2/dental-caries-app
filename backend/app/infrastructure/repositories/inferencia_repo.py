"""
inferencia_repo.py
==================
Implementación SQLAlchemy de IInferenciaRepository.

Autor: Rodrigo
Versión: 2.0 — Abril 2026
"""

from sqlalchemy.orm import Session

from app.domain.inferencias.entities import InferenciaIA
from app.domain.inferencias.repository import IInferenciaRepository
from app.domain.inferencias.value_objects import (
    EstadoInferencia,
    InferenciaId,
    TiempoInferencia,
    WorkerId,
)
from app.domain.estudios.value_objects import EstudioId
from app.infrastructure.database.models.inferencia_model import InferenciaIAORM


class SQLAlchemyInferenciaRepository(IInferenciaRepository):
    """
    Repositorio de inferencias IA — SQLAlchemy.
    Traduce TiempoInferencia.valor_ms ↔ InferenciaIAORM.tiempo_ms.
    """

    def __init__(self, db: Session) -> None:
        self._db = db

    @staticmethod
    def _to_domain(orm: InferenciaIAORM) -> InferenciaIA:
        return InferenciaIA(
            id=orm.id,
            estudio_id=orm.estudio_id,
            modelo_ml_id=orm.modelo_ml_id,
            estado=EstadoInferencia(value=orm.estado),
            created_at=orm.created_at,
            worker_id=WorkerId(value=orm.worker_id) if orm.worker_id else None,
            tiempo_inferencia=TiempoInferencia(valor_ms=orm.tiempo_ms) if orm.tiempo_ms else None,
            gpu_utilizada=orm.gpu_utilizada,
            error_mensaje=orm.error_mensaje,
            completed_at=orm.completed_at,
        )

    @staticmethod
    def _to_orm(inferencia: InferenciaIA) -> InferenciaIAORM:
        return InferenciaIAORM(
            id=inferencia.id,
            estudio_id=inferencia.estudio_id,
            modelo_ml_id=inferencia.modelo_ml_id,
            estado=inferencia.estado.value,
            worker_id=inferencia.worker_id.value if inferencia.worker_id else None,
            gpu_utilizada=inferencia.gpu_utilizada,
            tiempo_ms=inferencia.tiempo_inferencia.valor_ms if inferencia.tiempo_inferencia else None,
            error_mensaje=inferencia.error_mensaje,
            created_at=inferencia.created_at,
            completed_at=inferencia.completed_at,
        )


    def save(self, inferencia: InferenciaIA) -> None:
        existing = self._db.get(InferenciaIAORM, inferencia.id)

        if existing is None:
            self._db.add(self._to_orm(inferencia))
        else:
            existing.estado = inferencia.estado.value
            existing.worker_id = inferencia.worker_id.value if inferencia.worker_id else None
            existing.gpu_utilizada = inferencia.gpu_utilizada
            existing.tiempo_ms = inferencia.tiempo_inferencia.valor_ms if inferencia.tiempo_inferencia else None
            existing.error_mensaje = inferencia.error_mensaje
            existing.completed_at = inferencia.completed_at

        self._db.flush()

    def get_by_id(self, inferencia_id: InferenciaId) -> InferenciaIA | None:
        orm = self._db.get(InferenciaIAORM, inferencia_id.value)
        return self._to_domain(orm) if orm else None

    def get_by_estudio_id(self, estudio_id: EstudioId) -> list[InferenciaIA]:
        rows = (
            self._db.query(InferenciaIAORM)
            .filter(InferenciaIAORM.estudio_id == estudio_id.value)
            .order_by(InferenciaIAORM.created_at.desc())
            .all()
        )
        return [self._to_domain(row) for row in rows]

    def get_pendientes(self, limit: int = 10) -> list[InferenciaIA]:
        rows = (
            self._db.query(InferenciaIAORM)
            .filter(InferenciaIAORM.estado == "PENDIENTE")
            .order_by(InferenciaIAORM.created_at.asc())
            .limit(limit)
            .all()
        )
        return [self._to_domain(row) for row in rows]