"""
modelo_repo.py
==============
Implementación SQLAlchemy de IModeloMLRepository.
"""

from uuid import UUID

from sqlalchemy.orm import Session

from app.domain.diagnosticos.value_objects import RegistroModeloML
from app.infrastructure.database.models.diagnostico_model import ModeloMLORM


class SQLAlchemyModeloMLRepository:
    """
    Repositorio de modelos ML.

    RegistroModeloML (dominio) tiene 4 campos: modelo_ml_id, nombre_modelo,
    version, f1_score. ModeloMLORM (infraestructura) tiene más datos técnicos.
    El mapeo es deliberadamente parcial — el dominio solo necesita lo que
    usa para sus reglas de negocio.
    """

    def __init__(self, db: Session) -> None:
        self._db = db

    @staticmethod
    def _to_vo(orm: ModeloMLORM) -> RegistroModeloML:
        return RegistroModeloML(
            modelo_ml_id=orm.id,
            nombre_modelo=orm.nombre,
            version=orm.version,
            f1_score=orm.f1_score,
        )

    def get_by_id(self, modelo_id: UUID) -> RegistroModeloML | None:
        orm = self._db.get(ModeloMLORM, modelo_id)
        return self._to_vo(orm) if orm else None

    def get_aprobado_produccion(self, tipo: str) -> RegistroModeloML | None:
        """
        Devuelve el modelo aprobado para producción de un tipo dado.
        El dominio define 'aprobado' como f1_score >= 0.85.
        La tabla guarda el flag aprobado_produccion para no recalcular.
        """
        orm = (
            self._db.query(ModeloMLORM)
            .filter(
                ModeloMLORM.tipo == tipo,
                ModeloMLORM.aprobado_produccion == True,
            )
            .order_by(ModeloMLORM.created_at.desc())
            .first()
        )
        return self._to_vo(orm) if orm else None

    def list_all(self) -> list[RegistroModeloML]:
        rows = (
            self._db.query(ModeloMLORM)
            .order_by(ModeloMLORM.tipo, ModeloMLORM.created_at.desc())
            .all()
        )
        return [self._to_vo(row) for row in rows]

    def save(self, orm_data: ModeloMLORM) -> None:
        """
        Persiste un ModeloMLORM directamente.
        Se usa desde seeders o desde el panel de administración,
        no desde handlers de dominio.
        """
        existing = self._db.get(ModeloMLORM, orm_data.id)
        if existing is None:
            self._db.add(orm_data)
        else:
            existing.aprobado_produccion = orm_data.aprobado_produccion
            existing.f1_score = orm_data.f1_score
            existing.precision_score = orm_data.precision_score
            existing.recall_score = orm_data.recall_score
        self._db.flush()