"""
event_handlers.py
=================
Handlers de eventos de dominio que actualizan los read models CQRS.

Se ejecutan después de que un comando persiste cambios en el write model.
Mantienen sincronizados rm_cola_revision, rm_historial_paciente
y rm_estadisticas_modelo.
"""

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.domain.diagnosticos.events import (
    DiagnosticoRechazado,
    DiagnosticoSugeridoPorIA,
    DiagnosticoValidado,
    SegundaOpinionSolicitada,
)
from app.infrastructure.database.models.read_models.rm_cola import RMColaRevisionORM
from app.infrastructure.database.models.read_models.rm_estadisticas import RMEstadisticasModeloORM
from app.infrastructure.database.models.read_models.rm_historial import RMHistorialPacienteORM


class ActualizarColaRevision:
    """
    Mantiene rm_cola_revision sincronizado.

    - DiagnosticoSugeridoPorIA  → INSERT en la cola
    - SegundaOpinionSolicitada  → marca segunda_opinion=True
    - DiagnosticoValidado       → DELETE de la cola
    - DiagnosticoRechazado      → DELETE de la cola
    """

    def __init__(self, db: Session) -> None:
        self._db = db

    def on_diagnostico_sugerido(
        self,
        event: DiagnosticoSugeridoPorIA,
        paciente_nombre: str,
        tipo_examen: str,
    ) -> None:
        entrada = RMColaRevisionORM(
            diagnostico_id=event.diagnostico_id,
            paciente_id=event.paciente_id,
            estudio_id=event.estudio_id,
            paciente_nombre=paciente_nombre,
            tipo_examen=tipo_examen,
            confianza_global=event.confianza_global,
            categoria_confianza=event.categoria_confianza,
            segunda_opinion=False,
            fecha_generacion=datetime.now(tz=timezone.utc),
        )
        self._db.add(entrada)
        self._db.flush()

    def on_segunda_opinion_solicitada(self, event: SegundaOpinionSolicitada) -> None:
        entrada = (
            self._db.query(RMColaRevisionORM)
            .filter(RMColaRevisionORM.diagnostico_id == event.diagnostico_id)
            .first()
        )
        if entrada:
            entrada.segunda_opinion = True
            self._db.flush()

    def on_diagnostico_validado(self, event: DiagnosticoValidado) -> None:
        self._db.query(RMColaRevisionORM).filter(
            RMColaRevisionORM.diagnostico_id == event.diagnostico_id
        ).delete()
        self._db.flush()

    def on_diagnostico_rechazado(self, event: DiagnosticoRechazado) -> None:
        self._db.query(RMColaRevisionORM).filter(
            RMColaRevisionORM.diagnostico_id == event.diagnostico_id
        ).delete()
        self._db.flush()


class ActualizarHistorial:
    """
    Mantiene rm_historial_paciente sincronizado.

    - DiagnosticoSugeridoPorIA → INSERT con estado SUGERIDO_IA
    - DiagnosticoValidado      → UPDATE estado + fecha_validacion + odontologo
    - DiagnosticoRechazado     → UPDATE estado
    """

    def __init__(self, db: Session) -> None:
        self._db = db

    def on_diagnostico_sugerido(
        self,
        event: DiagnosticoSugeridoPorIA,
        tipo_examen: str,
        fecha_estudio: datetime,
    ) -> None:
        entrada = RMHistorialPacienteORM(
            paciente_id=event.paciente_id,
            estudio_id=event.estudio_id,
            diagnostico_id=event.diagnostico_id,
            fecha_estudio=fecha_estudio,
            tipo_examen=tipo_examen,
            estado_diagnostico="SUGERIDO_IA",
            total_hallazgos=event.total_hallazgos,
            confianza_global=event.confianza_global,
            updated_at=datetime.now(tz=timezone.utc),
        )
        self._db.add(entrada)
        self._db.flush()

    def on_diagnostico_validado(
        self,
        event: DiagnosticoValidado,
        odontologo_nombre: str,
    ) -> None:
        entrada = (
            self._db.query(RMHistorialPacienteORM)
            .filter(RMHistorialPacienteORM.diagnostico_id == event.diagnostico_id)
            .first()
        )
        if entrada:
            entrada.estado_diagnostico = "VALIDADO"
            entrada.odontologo_nombre = odontologo_nombre
            entrada.fecha_validacion = datetime.now(tz=timezone.utc)
            entrada.updated_at = datetime.now(tz=timezone.utc)
            self._db.flush()

    def on_diagnostico_rechazado(self, event: DiagnosticoRechazado) -> None:
        entrada = (
            self._db.query(RMHistorialPacienteORM)
            .filter(RMHistorialPacienteORM.diagnostico_id == event.diagnostico_id)
            .first()
        )
        if entrada:
            entrada.estado_diagnostico = "RECHAZADO"
            entrada.updated_at = datetime.now(tz=timezone.utc)
            self._db.flush()


class ActualizarEstadisticas:
    """
    Mantiene rm_estadisticas_modelo sincronizado.

    - DiagnosticoValidado  → incrementa total_diagnosticos + total_validados
    - DiagnosticoRechazado → incrementa total_diagnosticos + total_rechazados
    Recalcula tasa_validacion y tasa_segunda_opinion tras cada cambio.
    """

    def __init__(self, db: Session) -> None:
        self._db = db

    def _get_or_create(self, modelo_ml_id, nombre_modelo: str, version: str) -> RMEstadisticasModeloORM:
        stats = (
            self._db.query(RMEstadisticasModeloORM)
            .filter(RMEstadisticasModeloORM.modelo_ml_id == modelo_ml_id)
            .first()
        )
        if stats is None:
            stats = RMEstadisticasModeloORM(
                modelo_ml_id=modelo_ml_id,
                nombre_modelo=nombre_modelo,
                version=version,
            )
            self._db.add(stats)
            self._db.flush()
        return stats

    def on_diagnostico_validado(
        self,
        evento: DiagnosticoValidado,
        modelo_ml_id,
        nombre_modelo: str,
        version: str,
        fue_segunda_opinion: bool,
    ) -> None:
        stats = self._get_or_create(modelo_ml_id, nombre_modelo, version)
        stats.total_diagnosticos += 1
        stats.total_validados += 1
        if fue_segunda_opinion:
            stats.tasa_segunda_opinion = (
                stats.tasa_segunda_opinion * (stats.total_diagnosticos - 1) + 1
            ) / stats.total_diagnosticos
        stats.tasa_validacion = stats.total_validados / stats.total_diagnosticos
        self._db.flush()

    def on_diagnostico_rechazado(
        self,
        evento: DiagnosticoRechazado,
        modelo_ml_id,
        nombre_modelo: str,
        version: str,
    ) -> None:
        stats = self._get_or_create(modelo_ml_id, nombre_modelo, version)
        stats.total_diagnosticos += 1
        stats.total_rechazados += 1
        stats.tasa_validacion = stats.total_validados / stats.total_diagnosticos
        self._db.flush()