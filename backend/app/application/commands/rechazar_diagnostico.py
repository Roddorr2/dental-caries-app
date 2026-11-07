"""
rechazar_diagnostico.py
=======================
Command para rechazar un diagnóstico sugerido por IA.
"""

from dataclasses import dataclass
from uuid import UUID

@dataclass(frozen=True)
class RechazarDiagnosticoCommand:
    """
    Intención de escritura: rechazar un diagnóstico sugerido por IA.

    El odontólogo determina que el diagnóstico no es clínicamente correcto.

    Attributes
    ----------
    diagnostico_id : UUID
        ID del diagnóstico a rechazar.
    odontologo_id : UUID
        ID del odontólogo que rechaza.
    motivo : str
        Motivo obligatorio del rechazo.
    """
    diagnostico_id: UUID
    odontologo_id: UUID
    motivo: str