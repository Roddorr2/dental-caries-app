"""
obtener_historial.py
====================
Query para obtener el historial clínico de un paciente.
"""

from dataclasses import dataclass
from uuid import UUID

@dataclass(frozen=True)
class ObtenerHistorialPacienteQuery:
    """
    Intención de lectura: historial de diagnósticos de un paciente.

    Lee desde rm_historial_paciente (read model CQRS) — sin JOINs.

    Attributes
    ----------
    paciente_id : UUID
        ID del paciente.
    limit : int
        Máximo de registros a retornar.
    offset : int
        Desplazamiento para paginación.
    """
    paciente_id: UUID
    limit: int = 20
    offset: int = 0