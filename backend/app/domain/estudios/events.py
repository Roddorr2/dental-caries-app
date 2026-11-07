"""
events.py
=========
Domain Events del Bounded Context: Adquisición Imagenológica.
"""

from dataclasses import dataclass
from  uuid import UUID

from app.domain.shared.domain_event import DomainEvent

@dataclass
class EstudioCreado(DomainEvent):
    """
    Evento emitido cuando se crea un nuevo estudio imagenológico.

    Attributes
    ----------
    estudio_id : UUID
        ID del estudio creado.
    paciente_id : UUID
        ID del paciente asociado.
    tipo_examen : str
        Tipo de examen clínico.
    """
    estudio_id: UUID
    paciente_id: UUID
    tipo_examen: str

    def __init__(self, estudio_id: UUID, paciente_id: UUID, tipo_examen: str) -> None:
        super().__init__()
        self.estudio_id = estudio_id
        self.paciente_id = paciente_id
        self.tipo_examen = tipo_examen

@dataclass
class ImagenAgregada(DomainEvent):
    """
    Evento emitido cuando se agrega una imagen válida al estudio.

    Attributes
    ----------
    estudio_id : UUID
        ID del estudio al que se agregó la imagen.
    imagen_id : UUID
        ID de la imagen agregada.
    tipo_vista : str
        Ángulo de la imagen agregada.
    """
    estudio_id: UUID
    imagen_id: UUID
    tipo_vista: str

    def __init__(self, estudio_id: UUID, imagen_id: UUID, tipo_vista: str) -> None:
        super().__init__()
        self.estudio_id = estudio_id
        self.imagen_id = imagen_id
        self.tipo_vista = tipo_vista

@dataclass
class AnalisisIASolicitado(DomainEvent):
    """
    Evento emitido cuando se solicita análisis IA sobre un estudio.

    Attributes
    ----------
    estudio_id : UUID
        ID del estudio a analizar.
    paciente_id : UUID
        ID del paciente asociado.
    total_imagenes : int
        Número de imágenes que serán analizadas.
    """
    estudio_id: UUID
    paciente_id: UUID
    total_imagenes: int

    def __init__(self, estudio_id: UUID, paciente_id: UUID, total_imagenes: int) -> None:
        super().__init__()
        self.estudio_id = estudio_id
        self.paciente_id = paciente_id
        self.total_imagenes = total_imagenes

@dataclass
class EstudioProcesado(DomainEvent):
    """
    Evento emitido cuando el estudio completa su análisis IA.

    Attributes
    ----------
    estudio_id : UUID
        ID del estudio procesado.
    paciente_id : UUID
        ID del paciente asociado.
    """
    estudio_id: UUID
    paciente_id: UUID

    def __init__(self, estudio_id: UUID, paciente_id: UUID) -> None:
        super().__init__()
        self.estudio_id = estudio_id
        self.paciente_id = paciente_id