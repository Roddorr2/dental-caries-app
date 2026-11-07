"""
estudio_schemas.py
==================
DTOs Pydantic para los recursos Estudio e Imagen.

EstudioCreate   → request body POST /estudios
ImagenCreate    → request body POST /estudios/{id}/imagenes
EstudioResponse → response body GET/POST /estudios
ImagenResponse  → response body dentro de EstudioResponse
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class EstudioCreate(BaseModel):
    """
    Request body para crear un nuevo estudio imagenológico.

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
    tipo_examen: str = Field(..., pattern=r"^(FOTOGRAFIA_INTRAORAL|SERIE_COMPLETA|OCLUSAL_MANDIBULAR|OCLUSAL_MAXILAR|FRONTAL_VESTIBULAR|LATERAL_DERECHA|LATERAL_IZQUIERDA)$")
    region_examinada: str | None = Field(default=None, max_length=100)
    observaciones: str | None = None


class ImagenCreate(BaseModel):
    """
    Request body para agregar una imagen a un estudio.

    Attributes
    ----------
    tipo_vista : str
        Vista de la imagen: OCLUSAL_MANDIBULAR | OCLUSAL_MAXILAR |
        FRONTAL_VESTIBULAR | LATERAL_DERECHA | LATERAL_IZQUIERDA.
    formato : str
        Formato del archivo: jpg | jpeg | png.
    ruta_almacenamiento : str
        Ruta donde fue guardado el archivo en storage.
    nombre_archivo : str
        Nombre original del archivo.
    hash_sha256 : str
        Hash SHA-256 del archivo (64 caracteres hex).
    calidad_suficiente : bool
        True si la imagen tiene calidad suficiente para análisis.
    nitidez : float | None
        Puntuación de nitidez (0.0 - 1.0). Opcional.
    iluminacion : float | None
        Puntuación de iluminación (0.0 - 1.0). Opcional.
    """

    tipo_vista: str = Field(..., pattern=r"^(OCLUSAL_MANDIBULAR|OCLUSAL_MAXILAR|FRONTAL_VESTIBULAR|LATERAL_DERECHA|LATERAL_IZQUIERDA)$")
    formato: str = Field(..., pattern=r"^(jpg|jpeg|png|JPG|JPEG|PNG)$")
    ruta_almacenamiento: str = Field(..., max_length=500)
    nombre_archivo: str = Field(..., max_length=255)
    hash_sha256: str = Field(..., min_length=64, max_length=64)
    calidad_suficiente: bool
    nitidez: float | None = Field(default=None, ge=0.0, le=1.0)
    iluminacion: float | None = Field(default=None, ge=0.0, le=1.0)


class ImagenResponse(BaseModel):
    """
    Response body para una imagen intraoral.

    Attributes
    ----------
    id : UUID
        Identificador único de la imagen.
    tipo_vista : str
        Vista de la imagen.
    formato : str
        Formato del archivo.
    nombre_archivo : str
        Nombre original del archivo.
    calidad_suficiente : bool
        True si la imagen tiene calidad suficiente.
    created_at : datetime
        Timestamp de creación.
    """

    id: UUID
    tipo_vista: str
    formato: str
    nombre_archivo: str
    calidad_suficiente: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class EstudioResponse(BaseModel):
    """
    Response body para un estudio imagenológico.

    Attributes
    ----------
    id : UUID
        Identificador único del estudio.
    paciente_id : UUID
        ID del paciente.
    tipo_examen : str
        Tipo de examen.
    estado_procesamiento : str
        Estado actual: PENDIENTE | EN_ANALISIS | PROCESADO.
    imagenes : list[ImagenResponse]
        Imágenes asociadas al estudio.
    created_at : datetime
        Timestamp de creación.
    """

    id: UUID
    paciente_id: UUID
    tipo_examen: str
    estado_procesamiento: str
    imagenes: list[ImagenResponse] = []
    created_at: datetime

    model_config = {"from_attributes": True}


class EstudioListItemResponse(BaseModel):
    """
    Response body para un elemento de la lista clínica de estudios fotográficos.
    """

    id: UUID
    paciente_id: UUID
    paciente_nombre: str | None = None
    paciente_dni: str | None = None
    tipo_examen: str
    estado_procesamiento: str
    total_imagenes: int = 0
    diagnostico_id: UUID | None = None
    created_at: datetime

    model_config = {"from_attributes": True}