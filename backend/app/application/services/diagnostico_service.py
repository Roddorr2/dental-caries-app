"""
diagnostico_service.py
======================
Servicio de aplicación: Diagnóstico.

Orquesta reglas de negocio que involucran múltiples BCs
en el flujo de revisión y validación clínica.

Casos de uso cubiertos:
- Consultar cola de revisión (read model CQRS)
- Consultar historial de un paciente (read model CQRS)
- Buscar casos similares para apoyo clínico

Nota: validar/rechazar son handlers simples (un solo agregado).
Este servicio existe para consultas que cruzan múltiples read models
o requieren enriquecer la respuesta con datos de varios BCs.
"""

from uuid import UUID

from sqlalchemy.orm import Session

from app.application.queries.buscar_casos import BuscarCasosSimilaresQuery
from app.application.queries.cola_revision import ConsultarColaRevisionQuery
from app.application.queries.estadisticas_modelo import ObtenerEstadisticasModeloQuery
from app.application.queries.obtener_historial import ObtenerHistorialPacienteQuery
from app.infrastructure.database.models.diagnostico_model import DiagnosticoORM, HallazgoORM
from app.infrastructure.database.models.read_models.rm_cola import RMColaRevisionORM
from app.infrastructure.database.models.read_models.rm_estadisticas import RMEstadisticasModeloORM
from app.infrastructure.database.models.read_models.rm_historial import RMHistorialPacienteORM

class ServicioDiagnostico:
    """
    Servicio de aplicación para consultas del ciclo de vida diagnóstico.

    Lee exclusivamente desde read models CQRS — nunca desde
    las tablas write. Esto garantiza queries rápidas sin JOINs complejos.
    """

    def __init__(self, db: Session) -> None:
        self._db = db

    def consultar_cola_revision(self, query: ConsultarColaRevisionQuery) -> list[dict]:
        """
        Retorna la cola de diagnósticos pendientes de revisión.

        Lee desde rm_cola_revision. Opcionalmente filtra por casos
        que requieren segunda opinión (confianza BAJA).

        Parameters
        ----------
        query : ConsultarColaRevisionQuery
            Parámetros de consulta: solo_segunda_opinion, limit, offset.

        Returns
        -------
        list[dict]
            Lista de entradas de la cola con datos desnormalizados.
        """
        q = self._db.query(RMColaRevisionORM)

        if query.solo_segunda_opinion:
            q = q.filter(RMColaRevisionORM.segunda_opinion == True)

        rows = (
            q.order_by(RMColaRevisionORM.fecha_generacion.asc())
            .limit(query.limit)
            .offset(query.offset)
            .all()
        )

        return [
            {
                "diagnostico_id": str(r.diagnostico_id),
                "paciente_id": str(r.paciente_id),
                "paciente_nombre": r.paciente_nombre,
                "estudio_id": str(r.estudio_id),
                "tipo_examen": r.tipo_examen,
                "confianza_global": r.confianza_global,
                "categoria_confianza": r.categoria_confianza,
                "segunda_opinion": r.segunda_opinion,
                "fecha_generacion": r.fecha_generacion.isoformat(),
            }
            for r in rows
        ]

    def obtener_historial_paciente(self, query: ObtenerHistorialPacienteQuery) -> list[dict]:
        """
        Retorna el historial clínico de un paciente.

        Lee desde rm_historial_paciente — sin JOINs.

        Parameters
        ----------
        query : ObtenerHistorialPacienteQuery
            Parámetros: paciente_id, limit, offset.

        Returns
        -------
        list[dict]
            Lista de entradas del historial con datos desnormalizados.
        """
        rows = (
            self._db.query(RMHistorialPacienteORM)
            .filter(RMHistorialPacienteORM.paciente_id == query.paciente_id)
            .order_by(RMHistorialPacienteORM.fecha_estudio.desc())
            .limit(query.limit)
            .offset(query.offset)
            .all()
        )

        return [
            {
                "estudio_id": str(r.estudio_id),
                "diagnostico_id": str(r.diagnostico_id),
                "fecha_estudio": r.fecha_estudio.isoformat(),
                "tipo_examen": r.tipo_examen,
                "estado_diagnostico": r.estado_diagnostico,
                "total_hallazgos": r.total_hallazgos,
                "confianza_global": r.confianza_global,
                "odontologo_nombre": r.odontologo_nombre,
                "fecha_validacion": r.fecha_validacion.isoformat() if r.fecha_validacion else None,
            }
            for r in rows
        ]

    def obtener_estadisticas_modelo(self, query: ObtenerEstadisticasModeloQuery) -> list[dict]:
        """
        Retorna métricas de rendimiento de modelos ML en producción.

        Lee desde rm_estadisticas_modelo.

        Parameters
        ----------
        query : ObtenerEstadisticasModeloQuery
            Parámetros: modelo_ml_id (None = todos los modelos).

        Returns
        -------
        list[dict]
            Lista de estadísticas por modelo.
        """
        q = self._db.query(RMEstadisticasModeloORM)

        if query.modelo_ml_id is not None:
            q = q.filter(
                RMEstadisticasModeloORM.modelo_ml_id == query.modelo_ml_id
            )

        rows = q.order_by(RMEstadisticasModeloORM.nombre_modelo).all()

        return [
            {
                "modelo_ml_id": str(r.modelo_ml_id),
                "nombre_modelo": r.nombre_modelo,
                "version": r.version,
                "total_diagnosticos": r.total_diagnosticos,
                "total_validados": r.total_validados,
                "total_rechazados": r.total_rechazados,
                "tasa_validacion": r.tasa_validacion,
                "tasa_segunda_opinion": r.tasa_segunda_opinion,
            }
            for r in rows
        ]

    def buscar_casos_similares(self, query: BuscarCasosSimilaresQuery) -> list[dict]:
        """
        Busca diagnósticos con características clínicas similares.

        Útil para que el odontólogo compare con casos anteriores
        antes de validar o rechazar un diagnóstico nuevo.
        Lee directamente desde la tabla write de hallazgos
        — los read models no cubren este caso de uso.

        Parameters
        ----------
        query : BuscarCasosSimilaresQuery
            Filtros: tipo_patologia, severidad, solo_validados, limit, offset.

        Returns
        -------
        list[dict]
            Lista de hallazgos con contexto de diagnóstico.
        """
        q = (
            self._db.query(HallazgoORM, DiagnosticoORM)
            .join(DiagnosticoORM, HallazgoORM.diagnostico_id == DiagnosticoORM.id)
        )

        if query.tipo_patologia:
            q = q.filter(HallazgoORM.tipo_patologia == query.tipo_patologia)

        if query.severidad:
            q = q.filter(HallazgoORM.severidad == query.severidad)

        if query.solo_validados:
            q = q.filter(DiagnosticoORM.estado == "VALIDADO")

        rows = (
            q.order_by(DiagnosticoORM.fecha_generacion.desc())
            .limit(query.limit)
            .offset(query.offset)
            .all()
        )

        return [
            {
                "hallazgo_id": str(h.id),
                "diagnostico_id": str(d.id),
                "tipo_patologia": h.tipo_patologia,
                "severidad": h.severidad,
                "confianza": h.confianza,
                "estado_diagnostico": d.estado,
                "fecha_diagnostico": d.fecha_generacion.isoformat(),
            }
            for h, d in rows
        ]