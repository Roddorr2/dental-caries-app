"""
estudio_repo.py
===============
Implementación SQLAlchemy de IEstudioRepository.
"""

from sqlalchemy.orm import Session

from app.domain.estudios.entites import EstudioImagenologico, ImagenIntraoral
from app.domain.estudios.repository import IEstudioRepository
from app.domain.estudios.value_objects import (
    CalidadImagen,
    EstadoProcesamiento,
    EstudioId,
    FormatoImagen,
    HashSHA256,
    ImagenId,
    RutaAlmacenamiento,
    TipoExamen,
    TipoVista,
)
from app.domain.pacientes.value_objects import PacienteId
from app.infrastructure.database.models.estudio_model import EstudioORM, ImagenIntraoralORM


class SQLAlchemyEstudioRepository(IEstudioRepository):
    """
    Repositorio de estudios imagenológicos — SQLAlchemy.
    Gestiona EstudioORM e ImagenIntraoralORM como unidad (cascade).
    """

    def __init__(self, db: Session) -> None:
        self._db = db


    @staticmethod
    def _imagen_to_domain(orm: ImagenIntraoralORM) -> ImagenIntraoral:
        hash_val = (orm.hash_sha256 or "").strip()
        if len(hash_val) != 64 or not all(c in "0123456789abcdefABCDEF" for c in hash_val):
            hash_val = hash_val.ljust(64, "0")[:64]
            if not all(c in "0123456789abcdefABCDEF" for c in hash_val):
                hash_val = "0" * 64

        return ImagenIntraoral(
            id=orm.id,
            estudio_id=orm.estudio_id,
            tipo_vista=TipoVista(value=orm.tipo_vista),
            ruta_almacenamiento=RutaAlmacenamiento(value=orm.ruta_almacenamiento),
            nombre_archivo=orm.ruta_almacenamiento.split("/")[-1],  # derivado de la ruta
            formato=FormatoImagen(value=orm.formato),
            calidad=CalidadImagen(
                suficiente=orm.calidad_suficiente,
                nitidez=orm.nitidez,
                iluminacion=orm.iluminacion,
            ),
            hash_sha256=HashSHA256(value=hash_val),
            created_at=orm.created_at,
        )

    @staticmethod
    def _estudio_to_domain(orm: EstudioORM) -> EstudioImagenologico:
        imagenes = [
            SQLAlchemyEstudioRepository._imagen_to_domain(img)
            for img in orm.imagenes
        ]
        return EstudioImagenologico(
            id=orm.id,
            paciente_id=orm.paciente_id,
            tipo_examen=TipoExamen(value=orm.tipo_examen),
            estado_procesamiento=EstadoProcesamiento(value=orm.estado_procesamiento),
            imagenes=imagenes,
            created_at=orm.created_at,
            updated_at=orm.updated_at,
        )


    @staticmethod
    def _imagen_to_orm(img: ImagenIntraoral) -> ImagenIntraoralORM:
        return ImagenIntraoralORM(
            id=img.id,
            estudio_id=img.estudio_id,
            tipo_vista=img.tipo_vista.value,
            formato=img.formato.value,
            ruta_almacenamiento=img.ruta_almacenamiento.value,
            hash_sha256=img.hash_sha256.value,
            nitidez=img.calidad.nitidez,
            iluminacion=img.calidad.iluminacion,
            calidad_suficiente=img.calidad.suficiente,
            created_at=img.created_at,
        )

    @staticmethod
    def _estudio_to_orm(estudio: EstudioImagenologico) -> EstudioORM:
        orm = EstudioORM(
            id=estudio.id,
            paciente_id=estudio.paciente_id,
            tipo_examen=estudio.tipo_examen.value,
            estado_procesamiento=estudio.estado_procesamiento.value,
            created_at=estudio.created_at,
            updated_at=estudio.updated_at,
        )
        orm.imagenes = [
            SQLAlchemyEstudioRepository._imagen_to_orm(img)
            for img in estudio.imagenes
        ]
        return orm

    def save(self, estudio: EstudioImagenologico) -> None:
        existing = self._db.get(EstudioORM, estudio.id)

        if existing is None:
            self._db.add(self._estudio_to_orm(estudio))
        else:
            existing.estado_procesamiento = estudio.estado_procesamiento.value
            existing.updated_at = estudio.updated_at

            existing_ids = {img.id for img in existing.imagenes}
            for img in estudio.imagenes:
                if img.id not in existing_ids:
                    existing.imagenes.append(self._imagen_to_orm(img))

        self._db.flush()

    def get_by_id(self, estudio_id: EstudioId) -> EstudioImagenologico | None:
        orm = self._db.get(EstudioORM, estudio_id.value)
        return self._estudio_to_domain(orm) if orm else None

    def get_by_paciente_id(
        self,
        paciente_id: PacienteId,
        limit: int = 20,
        offset: int = 0,
    ) -> list[EstudioImagenologico]:
        rows = (
            self._db.query(EstudioORM)
            .filter(EstudioORM.paciente_id == paciente_id.value)
            .order_by(EstudioORM.created_at.desc())
            .limit(limit)
            .offset(offset)
            .all()
        )
        return [self._estudio_to_domain(row) for row in rows]

    def get_pendientes(self, limit: int = 20) -> list[EstudioImagenologico]:
        rows = (
            self._db.query(EstudioORM)
            .filter(EstudioORM.estado_procesamiento == "PENDIENTE")
            .order_by(EstudioORM.created_at.asc())
            .limit(limit)
            .all()
        )
        return [self._estudio_to_domain(row) for row in rows]

    def exists_imagen_by_hash(self, hash_sha256: str) -> bool:
        return (
            self._db.query(ImagenIntraoralORM.id)
            .filter(ImagenIntraoralORM.hash_sha256 == hash_sha256)
            .first()
        ) is not None