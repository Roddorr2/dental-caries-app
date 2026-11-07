"""
diagnostico_repo.py
===================
Implementación SQLAlchemy de IDiagnosticoRepository.

Autor: Rodrigo
Versión: 2.0 — Abril 2026
"""

from sqlalchemy.orm import Session

from app.domain.diagnosticos.entities import Diagnostico
from app.domain.diagnosticos.repository import IDiagnosticoRepository
from app.domain.diagnosticos.value_objects import (
    DiagnosticoId,
    EstadoDiagnostico,
    Hallazgo,
    NivelConfianza,
    RegionDental,
    RegistroModeloML,
    Severidad,
    TipoPatologia,
)
from app.domain.estudios.value_objects import EstudioId
from app.domain.pacientes.value_objects import PacienteId
from app.infrastructure.database.models.diagnostico_model import DiagnosticoORM, HallazgoORM


class SQLAlchemyDiagnosticoRepository(IDiagnosticoRepository):
    """
   Repositorio de diagnósticos — SQLAlchemy.
   Mapea Diagnostico (aggregate root) + Hallazgo (VO) ↔ ORM.
   """

    def __init__(self, db: Session) -> None:
        self._db = db

    @staticmethod
    def _hallazgo_to_domain(orm: HallazgoORM) -> Hallazgo:
        return Hallazgo(
            imagen_id=orm.imagen_id,
            tipo_patologia=TipoPatologia(value=orm.tipo_patologia),
            severidad=Severidad(value=orm.severidad),
            confianza=orm.confianza,
            region=RegionDental(
                diente_numero=orm.diente_numero,
                cuadrante=orm.cuadrante,
                bbox_x=orm.bbox_x,
                bbox_y=orm.bbox_y,
                bbox_width=orm.bbox_width,
                bbox_height=orm.bbox_height,
            ),
            descripcion_clinica=orm.descripcion_clinica,
        )

    @staticmethod
    def _to_domain(orm: DiagnosticoORM) -> Diagnostico:
        hallazgos = [
            SQLAlchemyDiagnosticoRepository._hallazgo_to_domain(h)
            for h in orm.hallazgos
        ]
        modelo = RegistroModeloML(
            modelo_ml_id=orm.modelo_ml_id,
            nombre_modelo=orm.modelo_ml.nombre if orm.modelo_ml else "",
            version=orm.modelo_ml.version if orm.modelo_ml else "",
            f1_score=orm.modelo_ml.f1_score if orm.modelo_ml else 0.0,
        )
        return Diagnostico(
            id=orm.id,
            estudio_id=orm.estudio_id,
            paciente_id=orm.paciente_id,
            modelo=modelo,
            hallazgos=hallazgos,
            nivel_confianza=NivelConfianza.desde_valor(orm.confianza_global),
            estado=EstadoDiagnostico(value=orm.estado),
            fecha_generacion=orm.fecha_generacion,
            created_at=orm.created_at,
            updated_at=orm.updated_at,
            inferencia_id=orm.inferencia_id,
            tiempo_inferencia_ms=orm.tiempo_inferencia_ms,
            fecha_validacion=orm.fecha_validacion,
            notas_validacion=orm.notas_validacion,
            motivo_rechazo=orm.motivo_rechazo,
        )

    @staticmethod
    def _hallazgo_to_orm(h: Hallazgo, diagnostico_id) -> HallazgoORM:
        return HallazgoORM(
            diagnostico_id=diagnostico_id,
            imagen_id=h.imagen_id,
            tipo_patologia=h.tipo_patologia.value,
            severidad=h.severidad.value,
            confianza=h.confianza,
            diente_numero=h.region.diente_numero,
            cuadrante=h.region.cuadrante,
            bbox_x=h.region.bbox_x,
            bbox_y=h.region.bbox_y,
            bbox_width=h.region.bbox_width,
            bbox_height=h.region.bbox_height,
            descripcion_clinica=h.descripcion_clinica,
        )

    @staticmethod
    def _to_orm(diagnostico: Diagnostico) -> DiagnosticoORM:
        orm = DiagnosticoORM(
            id=diagnostico.id,
            estudio_id=diagnostico.estudio_id,
            paciente_id=diagnostico.paciente_id,
            inferencia_id=diagnostico.inferencia_id,
            modelo_ml_id=diagnostico.modelo.modelo_ml_id,
            odontologo_id=diagnostico.odontologo.id if diagnostico.odontologo else None,
            estado=diagnostico.estado.value,
            confianza_global=diagnostico.nivel_confianza.valor,
            categoria_confianza=diagnostico.nivel_confianza.categoria,
            tiempo_inferencia_ms=diagnostico.tiempo_inferencia_ms,
            fecha_generacion=diagnostico.fecha_generacion,
            fecha_validacion=diagnostico.fecha_validacion,
            notas_validacion=diagnostico.notas_validacion,
            motivo_rechazo=diagnostico.motivo_rechazo,
            created_at=diagnostico.created_at,
            updated_at=diagnostico.updated_at,
        )
        orm.hallazgos = [
            SQLAlchemyDiagnosticoRepository._hallazgo_to_orm(h, diagnostico.id)
            for h in diagnostico.hallazgos
        ]
        return orm

    def save(self, diagnostico: Diagnostico) -> None:
        existing = self._db.get(DiagnosticoORM, diagnostico.id)

        if existing is None:
            self._db.add(self._to_orm(diagnostico))
        else:
            existing.estado = diagnostico.estado.value
            existing.odontologo_id = diagnostico.odontologo.id if diagnostico.odontologo else None
            existing.fecha_validacion = diagnostico.fecha_validacion
            existing.notas_validacion = diagnostico.notas_validacion
            existing.motivo_rechazo = diagnostico.motivo_rechazo
            existing.updated_at = diagnostico.updated_at

        self._db.flush()

    def get_by_id(self, diagnostico_id: DiagnosticoId) -> Diagnostico | None:
        orm = self._db.get(DiagnosticoORM, diagnostico_id.value)
        return self._to_domain(orm) if orm else None

    def get_by_estudio_id(self, estudio_id: EstudioId) -> list[Diagnostico]:
        rows = (
            self._db.query(DiagnosticoORM)
            .filter(DiagnosticoORM.estudio_id == estudio_id.value)
            .order_by(DiagnosticoORM.created_at.desc())
            .all()
        )
        return [self._to_domain(row) for row in rows]

    def get_pendientes_revision(self, limit: int = 20) -> list[Diagnostico]:
        rows = (
            self._db.query(DiagnosticoORM)
            .filter(DiagnosticoORM.estado == "SUGERIDO_IA")
            .order_by(DiagnosticoORM.fecha_generacion.asc())
            .limit(limit)
            .all()
        )
        return [self._to_domain(row) for row in rows]

    def get_by_paciente_id(
        self,
        paciente_id: PacienteId,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Diagnostico]:
        rows = (
            self._db.query(DiagnosticoORM)
            .filter(DiagnosticoORM.paciente_id == paciente_id.value)
            .order_by(DiagnosticoORM.created_at.desc())
            .limit(limit)
            .offset(offset)
            .all()
        )
        return [self._to_domain(row) for row in rows]