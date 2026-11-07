"""
diagnostico_schemas.py
======================
DTOs Pydantic para el recurso Diagnóstico.

DiagnosticoResponse → response body GET /diagnosticos
ValidarRequest      → request body POST /diagnosticos/{id}/validar
RechazarRequest     → request body POST /diagnosticos/{id}/rechazar
HallazgoResponse    → response body anidado en DiagnosticoResponse
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class HallazgoResponse(BaseModel):
    """
    Response body para un hallazgo clínico detectado por IA.

    Attributes
    ----------
    id : UUID
        Identificador único del hallazgo.
    imagen_id : UUID
        ID de la imagen donde se detectó.
    tipo_patologia : str
        Tipo de patología: CARIES | FRACTURA | CALCULO_DENTAL.
    severidad : str
        Severidad: LEVE | MODERADA | SEVERA.
    confianza : float
        Confianza del modelo (0.0 - 1.0).
    diente_numero : int | None
        Número de diente en notación FDI (11-48). Opcional.
    cuadrante : int | None
        Cuadrante dental (1-4). Opcional.
    bbox_x : float | None
        Coordenada X del bounding box. Opcional.
    bbox_y : float | None
        Coordenada Y del bounding box. Opcional.
    bbox_width : float | None
        Ancho del bounding box. Opcional.
    bbox_height : float | None
        Alto del bounding box. Opcional.
    descripcion_clinica : str | None
        Descripción clínica. Opcional.
    """

    id: UUID
    imagen_id: UUID
    tipo_patologia: str
    severidad: str
    confianza: float
    diente_numero: int | None = None
    cuadrante: int | None = None
    bbox_x: float | None = None
    bbox_y: float | None = None
    bbox_width: float | None = None
    bbox_height: float | None = None
    descripcion_clinica: str | None = None

    model_config = {"from_attributes": True}


class DiagnosticoResponse(BaseModel):
    """
    Response body para un diagnóstico asistido por IA.

    Attributes
    ----------
    id : UUID
        Identificador único del diagnóstico.
    estudio_id : UUID
        ID del estudio analizado.
    paciente_id : UUID
        ID del paciente.
    estado : str
        Estado: SUGERIDO_IA | EN_REVISION | VALIDADO | RECHAZADO.
    confianza_global : float
        Confianza global del diagnóstico (0.0 - 1.0).
    categoria_confianza : str
        Categoría: BAJA | MEDIA | ALTA.
    hallazgos : list[HallazgoResponse]
        Patologías detectadas.
    fecha_generacion : datetime
        Timestamp de generación por IA.
    fecha_validacion : datetime | None
        Timestamp de validación. None si no ha sido validado.
    notas_validacion : str | None
        Notas del odontólogo al validar. None si no aplica.
    motivo_rechazo : str | None
        Motivo del rechazo. None si no aplica.
    """

    id: UUID
    estudio_id: UUID
    paciente_id: UUID
    estado: str
    confianza_global: float
    categoria_confianza: str
    hallazgos: list[HallazgoResponse] = []
    fecha_generacion: datetime
    fecha_validacion: datetime | None = None
    notas_validacion: str | None = None
    motivo_rechazo: str | None = None

    model_config = {"from_attributes": True}


class ValidarRequest(BaseModel):
    """
    Request body para validar un diagnóstico sugerido por IA.

    Attributes
    ----------
    odontologo_id : UUID
        ID del odontólogo que valida.
    notas : str
        Notas clínicas obligatorias de la validación.
    """

    odontologo_id: UUID
    notas: str = Field(..., min_length=1)


class RechazarRequest(BaseModel):
    """
    Request body para rechazar un diagnóstico sugerido por IA.

    Attributes
    ----------
    odontologo_id : UUID
        ID del odontólogo que rechaza.
    motivo : str
        Motivo obligatorio del rechazo.
    """

    odontologo_id: UUID
    motivo: str = Field(..., min_length=1)