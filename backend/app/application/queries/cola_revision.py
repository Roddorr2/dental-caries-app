"""
cola_revision.py
================
Query para consultar la cola de diagnósticos pendientes de revisión.
"""

from dataclasses import dataclass

@dataclass(frozen=True)
class ConsultarColaRevisionQuery:
    """
    Intención de lectura: diagnósticos pendientes de revisión por odontólogo.

    Lee desde rm_cola_revision (read model CQRS).
    Opcionalmente filtra por casos que requieren segunda opinión.

    Attributes
    ----------
    solo_segunda_opinion : bool
        Si True, retorna solo casos con confianza BAJA.
    limit : int
        Máximo de registros a retornar.
    offset : int
        Desplazamiento para paginación.
    """
    solo_segunda_opinion: bool = False
    limit: int = 20
    offset: int = 0