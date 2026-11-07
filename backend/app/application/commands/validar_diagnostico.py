"""
validar_diagnostico.py
======================
Command para validar un diagnóstico sugerido por IA.
"""

from dataclasses import dataclass
from uuid import UUID

@dataclass(frozen=True)
class ValidarDiagnosticoCommand:
    """
    Intención de escritura: validar un diagnóstico sugerido por IA.

    El odontólogo confirma que el diagnóstico es clínicamente correcto.

    Attributes
    ----------
    diagnostico_id : UUID
        ID del diagnóstico a validar.
    odontologo_id : UUID
        ID del odontólogo que valida.
    notas : str
        Notas clínicas obligatorias de la validación.
    """
    diagnostico_id: UUID
    odontologo_id: UUID
    notas: str