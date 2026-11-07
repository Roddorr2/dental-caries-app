"""
events.py
=========
Domain Events del Bounded Context: Gestión de Pacientes.
"""

from dataclasses import dataclass
from uuid import UUID

from app.domain.shared.domain_event import DomainEvent

@dataclass
class PacienteRegistrado(DomainEvent):
    """
    Evento emitido cuando un nuevo paciente es registrado en el sistema.

    Attributes
    ----------
    paciente_id : UUID
        ID del paciente recién registrado.
    dni : str
        DNI del paciente.
    nombre_completo : str
        Nombre completo del paciente.
    """
    paciente_id: UUID
    dni: str
    nombre_completo: str
    
    def __init__(self, paciente_id: UUID, dni: str, nombre_completo: str) -> None:
        super().__init__()
        self.paciente_id = paciente_id
        self.dni = dni
        self.nombre_completo = nombre_completo

@dataclass
class PacienteActualizado(DomainEvent):
    """
    Evento emitido cuando los datos de un paciente son actualizados.

    Attributes
    ----------
    paciente_id : UUID
        ID del paciente actualizado.
    campos_actualizados : list[str]
        Lista de nombres de campos que fueron modificados.
    """
    paciente_id: UUID
    campos_actualizados: list
    
    def __init__(self, paciente_id: UUID, campos_actualizados: list) -> None:
        super().__init__()
        self.paciente_id = paciente_id
        self.campos_actualizados = campos_actualizados

@dataclass
class PacienteDesactivado(DomainEvent):
    """
    Evento emitido cuando un paciente es desactivado en el sistema.

    Attributes
    ----------
    paciente_id : UUID
        ID del paciente desactivado.
    """
    paciente_id: UUID
    
    def __init__(self, paciente_id: UUID) -> None:
        super().__init__()
        self.paciente_id = paciente_id
