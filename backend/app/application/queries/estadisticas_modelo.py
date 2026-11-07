"""
estadisticas_modelo.py
======================
Query para obtener estadísticas de rendimiento de modelos ML en producción.
"""

from dataclasses import dataclass
from uuid import UUID

@dataclass(frozen=True)
class ObtenerEstadisticasModeloQuery:
    """
    Intención de lectura: métricas reales de un modelo ML en producción.

    Lee desde rm_estadisticas_modelo (read model CQRS).
    Muestra tasa de validación y segunda opinión calculadas sobre
    diagnósticos reales validados por odontólogos.

    Attributes
    ----------
    modelo_ml_id : UUID | None
        ID del modelo específico. Si None, retorna todos los modelos.
    """
    modelo_ml_id: UUID | None = None