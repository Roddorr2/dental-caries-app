"""
odontologo_repo.py
==================
Implementación SQLAlchemy de IOdontologoRepository.
"""

from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.domain.diagnosticos.entities import Odontologo
from app.domain.diagnosticos.repository import IOdontologoRepository
from app.infrastructure.database.models.diagnostico_model import OdontologoORM

class SQLAlchemyOdontologoRepository(IOdontologoRepository):
    """
    Repositorio de odontólogos — SQLAlchemy.
    Odontologo es entidad de dominio (actor clínico), no usuario del sistema.
    """

    def __init__(self, db: Session) -> None:
        self._db = db

    @staticmethod
    def _to_domain(orm: OdontologoORM) -> Odontologo:
        return Odontologo(
            id=orm.id,
            nombres=orm.nombres,
            apellidos=orm.apellidos,
            numero_colegiatura=orm.numero_colegiatura,
            autorizado_validar=orm.autorizado_validar,
        )

    def get_by_id(self, odontologo_id: UUID) -> Optional[Odontologo]:
        orm: OdontologoORM | None = self._db.get(OdontologoORM, odontologo_id)
        return self._to_domain(orm) if orm else None

    def get_by_colegiatura(self, numero_colegiatura: str) -> Optional[Odontologo]:
        orm = (
            self._db.query(OdontologoORM)
            .filter(OdontologoORM.numero_colegiatura == numero_colegiatura)
            .first()
        )
        return self._to_domain(orm) if orm else None

    def list_autorizados(self) -> list[Odontologo]:
        rows = (
            self._db.query(OdontologoORM)
            .filter(OdontologoORM.autorizado_validar == True)
            .order_by(OdontologoORM.apellidos)
            .all()
        )
        return [self._to_domain(row) for row in rows]