"""
events.py
=========
Domain Events del Bounded Context: Diagnóstico Asistido por IA.
"""

from dataclasses import dataclass
from uuid import UUID

from app.domain.shared.domain_event import DomainEvent


@dataclass
class DiagnosticoSugeridoPorIA(DomainEvent):
    """
    Evento emitido cuando la IA genera un diagnóstico sugerido.

    Dispara: INSERT en rm_cola_revision.

    Attributes
    ----------
    diagnostico_id : UUID
    estudio_id : UUID
    paciente_id : UUID
    modelo_ml_id : UUID
    confianza_global : float
    categoria_confianza : str
    total_hallazgos : int
    """
    diagnostico_id: UUID
    estudio_id: UUID
    paciente_id: UUID
    modelo_ml_id: UUID
    confianza_global: float
    categoria_confianza: str
    total_hallazgos: int

    def __init__(
        self,
        diagnostico_id: UUID,
        estudio_id: UUID,
        paciente_id: UUID,
        modelo_ml_id: UUID,
        confianza_global: float,
        categoria_confianza: str,
        total_hallazgos: int,
    ) -> None:
        super().__init__()
        self.diagnostico_id = diagnostico_id
        self.estudio_id = estudio_id
        self.paciente_id = paciente_id
        self.modelo_ml_id = modelo_ml_id
        self.confianza_global = confianza_global
        self.categoria_confianza = categoria_confianza
        self.total_hallazgos = total_hallazgos


@dataclass
class DiagnosticoEnRevision(DomainEvent):
    """
    Evento emitido cuando un odontólogo inicia la revisión del diagnóstico.

    Attributes
    ----------
    diagnostico_id : UUID
    odontologo_id : UUID
    """
    diagnostico_id: UUID
    odontologo_id: UUID

    def __init__(self, diagnostico_id: UUID, odontologo_id: UUID) -> None:
        super().__init__()
        self.diagnostico_id = diagnostico_id
        self.odontologo_id = odontologo_id


@dataclass
class DiagnosticoValidado(DomainEvent):
    """
    Evento emitido cuando un odontólogo valida el diagnóstico.

    Dispara: DELETE en rm_cola_revision + INSERT en rm_historial_paciente
             + UPDATE en rm_estadisticas_modelo.

    Attributes
    ----------
    diagnostico_id : UUID
    estudio_id : UUID
    paciente_id : UUID
    odontologo_id : UUID
    """
    diagnostico_id: UUID
    estudio_id: UUID
    paciente_id: UUID
    odontologo_id: UUID

    def __init__(
        self,
        diagnostico_id: UUID,
        estudio_id: UUID,
        paciente_id: UUID,
        odontologo_id: UUID,
    ) -> None:
        super().__init__()
        self.diagnostico_id = diagnostico_id
        self.estudio_id = estudio_id
        self.paciente_id = paciente_id
        self.odontologo_id = odontologo_id


@dataclass
class DiagnosticoRechazado(DomainEvent):
    """
    Evento emitido cuando un odontólogo rechaza el diagnóstico.

    Dispara: DELETE en rm_cola_revision + INSERT en rm_historial_paciente
             + UPDATE en rm_estadisticas_modelo.

    Attributes
    ----------
    diagnostico_id : UUID
    estudio_id : UUID
    paciente_id : UUID
    odontologo_id : UUID
    motivo : str
    """
    diagnostico_id: UUID
    estudio_id: UUID
    paciente_id: UUID
    odontologo_id: UUID
    motivo: str

    def __init__(
        self,
        diagnostico_id: UUID,
        estudio_id: UUID,
        paciente_id: UUID,
        odontologo_id: UUID,
        motivo: str,
    ) -> None:
        super().__init__()
        self.diagnostico_id = diagnostico_id
        self.estudio_id = estudio_id
        self.paciente_id = paciente_id
        self.odontologo_id = odontologo_id
        self.motivo = motivo


@dataclass
class SegundaOpinionSolicitada(DomainEvent):
    """
    Evento emitido cuando se detecta confianza BAJA y se solicita segunda opinión.

    Attributes
    ----------
    diagnostico_id : UUID
    paciente_id : UUID
    confianza_global : float
    """
    diagnostico_id: UUID
    paciente_id: UUID
    confianza_global: float

    def __init__(
        self,
        diagnostico_id: UUID,
        paciente_id: UUID,
        confianza_global: float,
    ) -> None:
        super().__init__()
        self.diagnostico_id = diagnostico_id
        self.paciente_id = paciente_id
        self.confianza_global = confianza_global