"""
cargar_estudio.py
=================
Commands para cargar un estudio imagenológico y agregar imágenes.
"""

from dataclasses import dataclass
from uuid import UUID

@dataclass(frozen=True)
class CargarEstudioCommand:
    """
    Intención de escritura: crear un nuevo estudio imagenológico para un paciente.

    Attributes
    ----------
    paciente_id : UUID
        ID del paciente que recibe el estudio.
    tipo_examen : str
        Tipo de examen: FOTOGRAFIA_INTRAORAL | SERIE_COMPLETA | OCLUSAL_MANDIBULAR |
        OCLUSAL_MAXILAR | FRONTAL_VESTIBULAR | LATERAL_DERECHA | LATERAL_IZQUIERDA.
    region_examinada : str | None
        Región clínica examinada. Opcional.
    observaciones : str | None
        Notas clínicas adicionales. Opcional.
    """
    paciente_id: UUID
    tipo_examen: str
    region_examinada: str | None = None
    observaciones: str | None = None

@dataclass(frozen=True)
class AgregarImagenCommand:
    """
    Intención de escritura: agregar una imagen a un estudio existente.

    Attributes
    ----------
    estudio_id : UUID
        ID del estudio al que se agrega la imagen.
    tipo_vista : str
        Vista de la imagen: OCLUSAL_MANDIBULAR | OCLUSAL_MAXILAR |
        FRONTAL_VESTIBULAR | LATERAL_DERECHA | LATERAL_IZQUIERDA.
    formato : str
        Formato del archivo: jpg | jpeg | png.
    ruta_almacenamiento : str
        Ruta donde fue guardado el archivo.
    nombre_archivo : str
        Nombre original del archivo.
    hash_sha256 : str
        Hash del archivo para deduplicación.
    nitidez : float | None
        Puntuación de nitidez (0.0 - 1.0). Opcional.
    iluminacion : float | None
        Puntuación de iluminación (0.0 - 1.0). Opcional.
    calidad_suficiente : bool
        True si la imagen tiene calidad suficiente para análisis.
    """
    estudio_id: UUID
    tipo_vista: str
    formato: str
    ruta_almacenamiento: str
    nombre_archivo: str
    hash_sha256: str
    calidad_suficiente: bool
    nitidez: float | None = None
    iluminacion: float | None = None