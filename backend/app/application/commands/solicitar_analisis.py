"""
solicitar_analisis.py
=====================
Command para solicitar análisis IA sobre un estudio imagenológico.
"""

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class SolicitarAnalisisIACommand:
    """
    Intención de escritura: iniciar el análisis IA de un estudio.

    Dispara el pipeline: estudio → inferencia → diagnóstico sugerido.

    Attributes
    ----------
    estudio_id : UUID
        ID del estudio a analizar.
    modelo_ml_id : UUID
        ID del modelo ML que ejecutará la inferencia.
    """
    estudio_id: UUID
    modelo_ml_id: UUID