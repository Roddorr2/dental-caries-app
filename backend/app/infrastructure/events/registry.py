"""
registry.py
===========
Registro de handlers de eventos de dominio.

Conecta cada tipo de evento con su handler correspondiente.
Este es el único lugar del sistema donde se declara
qué handler reacciona a qué evento.

Uso:
    En main.py al arrancar la aplicación:

        from app.infrastructure.events.registry import registrar_handlers

        db = SessionLocal()
        bus = InMemoryEventBus()
        registrar_handlers(bus, db)
"""

import logging

from sqlalchemy.orm import Session

from app.application.handlers.event_handlers import (
    ActualizarColaRevision,
    ActualizarEstadisticas,
    ActualizarHistorial,
)
from app.domain.diagnosticos.events import (
    DiagnosticoRechazado,
    DiagnosticoSugeridoPorIA,
    DiagnosticoValidado,
    SegundaOpinionSolicitada,
)
from app.infrastructure.events.event_bus import InMemoryEventBus

logger = logging.getLogger(__name__)


def registrar_handlers(bus: InMemoryEventBus, db: Session) -> None:
    """
    Registra todos los handlers de eventos en el bus.

    Conecta cada evento de dominio con el handler que actualiza
    el read model CQRS correspondiente.

    Mapa de eventos → read models afectados:

    DiagnosticoSugeridoPorIA:
        → rm_cola_revision     (INSERT entrada nueva)
        → rm_historial_paciente (INSERT con estado SUGERIDO_IA)

    SegundaOpinionSolicitada:
        → rm_cola_revision     (UPDATE segunda_opinion=True)

    DiagnosticoValidado:
        → rm_cola_revision     (DELETE — sale de la cola)
        → rm_historial_paciente (UPDATE estado + odontologo)
        → rm_estadisticas_modelo (UPDATE contadores)

    DiagnosticoRechazado:
        → rm_cola_revision     (DELETE — sale de la cola)
        → rm_historial_paciente (UPDATE estado)
        → rm_estadisticas_modelo (UPDATE contadores)

    Parameters
    ----------
    bus : InMemoryEventBus
        Instancia del bus de eventos.
    db : Session
        Sesión SQLAlchemy compartida con la transacción activa.
    """
    cola    = ActualizarColaRevision(db)
    historial = ActualizarHistorial(db)
    stats   = ActualizarEstadisticas(db)

    def _on_sugerido(event: DiagnosticoSugeridoPorIA) -> None:
        """
        Necesita datos desnormalizados (nombre del paciente, tipo_examen)
        que no vienen en el evento — los resuelve con una query puntual.
        """
        from app.infrastructure.database.models.paciente_model import PacienteORM
        from app.infrastructure.database.models.estudio_model import EstudioORM

        paciente = db.get(PacienteORM, event.paciente_id)
        estudio  = db.get(EstudioORM, event.estudio_id)

        paciente_nombre = (
            f"{paciente.nombres} {paciente.apellidos}"
            if paciente else "Desconocido"
        )
        tipo_examen = estudio.tipo_examen if estudio else "DESCONOCIDO"
        fecha_estudio = estudio.created_at if estudio else event.occurred_on

        cola.on_diagnostico_sugerido(event, paciente_nombre, tipo_examen)
        historial.on_diagnostico_sugerido(event, tipo_examen, fecha_estudio)

    bus.subscribe(DiagnosticoSugeridoPorIA, _on_sugerido)

    bus.subscribe(
        SegundaOpinionSolicitada,
        cola.on_segunda_opinion_solicitada,
    )

    def _on_validado(event: DiagnosticoValidado) -> None:
        """
        Resuelve nombre del odontólogo y metadata del modelo
        para desnormalizar en los read models.
        """
        from app.infrastructure.database.models.diagnostico_model import (
            DiagnosticoORM,
            ModeloMLORM,
            OdontologoORM,
        )

        odontologo = db.get(OdontologoORM, event.odontologo_id)
        odontologo_nombre = (
            f"{odontologo.nombres} {odontologo.apellidos}"
            if odontologo else "Desconocido"
        )

        diagnostico = db.get(DiagnosticoORM, event.diagnostico_id)
        modelo_ml_id = diagnostico.modelo_ml_id if diagnostico else None
        modelo = db.get(ModeloMLORM, modelo_ml_id) if modelo_ml_id else None
        nombre_modelo = modelo.nombre if modelo else "Desconocido"
        version       = modelo.version if modelo else "0.0"

        fue_segunda_opinion = (
            diagnostico.categoria_confianza == "BAJA"
            if diagnostico else False
        )

        cola.on_diagnostico_validado(event)
        historial.on_diagnostico_validado(event, odontologo_nombre)
        stats.on_diagnostico_validado(
            event,
            modelo_ml_id=modelo_ml_id,
            nombre_modelo=nombre_modelo,
            version=version,
            fue_segunda_opinion=fue_segunda_opinion,
        )

    bus.subscribe(DiagnosticoValidado, _on_validado)

    def _on_rechazado(event: DiagnosticoRechazado) -> None:
        from app.infrastructure.database.models.diagnostico_model import (
            DiagnosticoORM,
            ModeloMLORM,
        )

        diagnostico = db.get(DiagnosticoORM, event.diagnostico_id)
        modelo_ml_id = diagnostico.modelo_ml_id if diagnostico else None
        modelo = db.get(ModeloMLORM, modelo_ml_id) if modelo_ml_id else None
        nombre_modelo = modelo.nombre if modelo else "Desconocido"
        version       = modelo.version if modelo else "0.0"

        cola.on_diagnostico_rechazado(event)
        historial.on_diagnostico_rechazado(event)
        stats.on_diagnostico_rechazado(
            event,
            modelo_ml_id=modelo_ml_id,
            nombre_modelo=nombre_modelo,
            version=version,
        )

    bus.subscribe(DiagnosticoRechazado, _on_rechazado)

    logger.info("Event handlers registrados correctamente.")