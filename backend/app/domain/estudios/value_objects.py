"""
value_objects.py
================
Value Objects del Bounded Context: Adquisición Imagenológica.
"""

from dataclasses import dataclass
from uuid import UUID

from app.domain.shared.value_object import ValueObject

@dataclass(frozen=True)
class EstudioId(ValueObject):
    """
    Identificador único del estudio imagenológico.

    Attributes
    ----------
    value : UUID
        UUID generado al crear el estudio.
    """
    value: UUID

@dataclass(frozen=True)
class ImagenId(ValueObject):
    """
    Identificador único de una imagen intraoral.

    Attributes
    ----------
    value : UUID
        UUID generado al agregar la imagen.
    """
    value: UUID

@dataclass(frozen=True)
class TipoExamen(ValueObject):
    """
    Tipo de examen clínico o protocolo fotográfico del estudio intraoral.

    Attributes
    ----------
    value : str
        Valores permitidos: FOTOGRAFIA_INTRAORAL | SERIE_COMPLETA | OCLUSAL_MANDIBULAR |
        OCLUSAL_MAXILAR | FRONTAL_VESTIBULAR | LATERAL_DERECHA | LATERAL_IZQUIERDA.

    Raises
    ------
    ValueError
        Si el valor no está entre los permitidos.
    """
    value : str

    _VALORES_PERMITIDOS = frozenset({
        "FOTOGRAFIA_INTRAORAL",
        "SERIE_COMPLETA",
        "OCLUSAL_MANDIBULAR",
        "OCLUSAL_MAXILAR",
        "FRONTAL_VESTIBULAR",
        "LATERAL_DERECHA",
        "LATERAL_IZQUIERDA",
    })

    def __post_init__(self) -> None:
        if self.value not in self._VALORES_PERMITIDOS:
            raise ValueError(f"Tipo de examen inválido: {self.value}. Valores permitidos: {self._VALORES_PERMITIDOS}")

@dataclass(frozen=True)
class TipoVista(ValueObject):
    """
    Ángulo o vista fotográfica anatómica de la imagen intraoral.

    Attributes
    ----------
    value : str
        Valores permitidos: OCLUSAL_MANDIBULAR | OCLUSAL_MAXILAR |
        FRONTAL_VESTIBULAR | LATERAL_DERECHA | LATERAL_IZQUIERDA.

    Raises
    ------
    ValueError
        Si el valor no está entre los permitidos.
    """
    value : str

    _VALORES_PERMITIDOS = frozenset({
        "OCLUSAL_MANDIBULAR",
        "OCLUSAL_MAXILAR",
        "FRONTAL_VESTIBULAR",
        "LATERAL_DERECHA",
        "LATERAL_IZQUIERDA",
    })

    def __post_init__(self) -> None:
        if self.value not in self._VALORES_PERMITIDOS:
            raise ValueError(f"Tipo de vista inválida: {self.value}. Valores permitidos: {self._VALORES_PERMITIDOS}")

@dataclass(frozen=True)
class EstadoProcesamiento(ValueObject):
    """
    Estado de procesamiento del estudio imagenológico.

    Attributes
    ----------
    value : str
        Valor permitido: PENDIENTE | EN_ANALISIS | PROCESADO.

    Raises
    ------
    ValueError
        Si el valor no está entre los permitidos.
    """
    value: str

    _VALORES_PERMITIDOS = frozenset({"PENDIENTE", "EN_ANALISIS", "PROCESADO"})

    def __post_init__(self) -> None:
        if self.value not in self._VALORES_PERMITIDOS:
            raise ValueError(f"Estado inválido: {self.value}. Permitidos: {self._VALORES_PERMITIDOS}")

    def es_pendiente(self) -> bool:
        """Retorna True si el estudio está pendiente de análisis."""
        return self.value == "PENDIENTE"

    def es_en_analisis(self) -> bool:
        """Retorna True si el estudio está siendo analizado."""
        return self.value == "EN_ANALISIS"

    def es_procesado(self) -> bool:
        """Retorna True si el estudio ya fue procesado."""
        return self.value == "PROCESADO"

@dataclass(frozen=True)
class FormatoImagen(ValueObject):
    """
    Formato del archivo de imagen intraoral.

    Attributes
    ----------
    value : str
        Valor permitido: jpg | jpeg | png (insensible a mayúsculas).

    Raises
    ------
    ValueError
        Si el formato no está entre los permitidos (DCM/DICOM explícitamente excluido).
    """
    value : str

    _VALORES_PERMITIDOS = frozenset({"jpg", "jpeg", "png", "JPG", "JPEG", "PNG"})

    def __post_init__(self) -> None:
        if self.value not in self._VALORES_PERMITIDOS:
            raise ValueError(f"Formato inválido: {self.value}. Permitidos: {self._VALORES_PERMITIDOS}")

@dataclass(frozen=True)
class CalidadImagen(ValueObject):
    """
    Métricas de calidad de una imagen intraoral.

    Campos opcionales — pueden ser None si no fueron calculados.

    Attributes
    ----------
    nitidez : float | None
        Puntuación de nitidez entre 0.0 y 1.0.
    iluminacion : float | None
        Puntuación de iluminación entre 0.0 y 1.0.
    suficiente : bool
        True si la calidad es suficiente para ser procesada.

    Raises
    ------
    ValueError
        Si nitidez o iluminación están fuera del rango [0.0, 1.0].
    """
    suficiente: bool
    nitidez: float | None = None
    iluminacion: float | None = None

    def __post_init__(self) -> None:
        if self.nitidez is not None and not (0.0 <= self.nitidez <= 1.0):
            raise ValueError("La nitidez debe estar entre 0.0 y 1.0.")
        if self.iluminacion is not None and not (0.0 <= self.iluminacion <= 1.0):
            raise ValueError("La iluminación debe estar entre 0.0 y 1.0.")

@dataclass(frozen=True)
class RutaAlmacenamiento(ValueObject):
    """
    Ruta de almacenamiento del archivo de imagen.

    Attributes
    ----------
    value : str
        Ruta al archivo. Máximo 500 caracteres.

    Raises
    ------
    ValueError
        Si la ruta está vacía o supera 500 caracteres.
    """
    value: str

    def __post_init__(self) -> None:
        if not self.value or not self.value.strip():
            raise ValueError("La ruta de almacenamiento no puede estar vacía.")
        if len(self.value) > 500:
            raise ValueError("La ruta no puede superar 500 caracteres.")

@dataclass(frozen=True)
class HashSHA256(ValueObject):
    """
    Hash SHA-256 del archivo de imagen.

    Usado para evitar duplicados en el dataset.

    Attributes
    ----------
    value : str
        Hash SHA-256 en formato hexadecimal (64 caracteres).

    Raises
    ------
    ValueError
        Si el hash no tiene exactamente 64 caracteres hexadecimales.
    """
    value: str

    def __post_init__(self) -> None:
        if len(self.value) != 64:
            raise ValueError("El hash SHA-256 debe tener exactamente 64 caracteres.")
        if not all(c in '0123456789abcdefABCDEF' for c in self.value):
            raise ValueError("El hash SHA-256 debe ser hexadecimal")