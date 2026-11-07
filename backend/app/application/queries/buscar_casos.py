"""
buscar_casos.py
===============
Query para buscar casos similares en el historial clínico.
"""

from dataclasses import dataclass

@dataclass(frozen=True)
class BuscarCasosSimilaresQuery:
    """
    Intención de lectura: casos con características clínicas similares.

    Útil para que el odontólogo compare con diagnósticos anteriores
    validados antes de tomar una decisión.

    Filtros opcionales — al menos uno debe estar presente.

    Attributes
    ----------
    tipo_patologia : str | None
        Filtrar por tipo: CARIES | FRACTURA | CALCULO_DENTAL.
    severidad : str | None
        Filtrar por severidad: LEVE | MODERADA | SEVERA.
    solo_validados : bool
        Si True, retorna solo diagnósticos validados por odontólogo.
    limit : int
        Máximo de registros a retornar.
    offset : int
        Desplazamiento para paginación.
    """
    tipo_patologia: str | None = None
    severidad: str | None = None
    solo_validados: bool = True
    limit: int = 20
    offset: int = 0