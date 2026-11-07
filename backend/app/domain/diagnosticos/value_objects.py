"""
value_objects.py
================
Value Objects del Bounded Context: Diagnóstico Asistido por IA.
"""

from dataclasses import dataclass, field
from typing import Optional
from uuid import UUID

from app.domain.shared.value_object import ValueObject

@dataclass(frozen=True)
class DiagnosticoId(ValueObject):
    """
    Identificador único del diagnóstico.

    Attributes
    ----------
    value : UUID
        UUID generado al crear el diagnóstico.
    """
    value: UUID


@dataclass(frozen=True)
class EstadoDiagnostico(ValueObject):
    """
    Estado del diagnóstico en su ciclo de vida clínico.

    Attributes
    ----------
    value : str
        Valor permitido: SUGERIDO_IA | EN_REVISION | VALIDADO | RECHAZADO.

    Raises
    ------
    ValueError
        Si el valor no está entre los permitidos.
    """
    value: str

    _VALORES_PERMITIDOS = frozenset({"SUGERIDO_IA", "EN_REVISION", "VALIDADO", "RECHAZADO"})

    def __post_init__(self) -> None:
        if self.value not in self._VALORES_PERMITIDOS:
            raise ValueError(
                f"Estado inválido: '{self.value}'. "
                f"Permitidos: {self._VALORES_PERMITIDOS}"
            )

    def es_sugerido_ia(self) -> bool:
        """Retorna True si el diagnóstico fue generado por IA y aún no revisado."""
        return self.value == "SUGERIDO_IA"

    def es_en_revision(self) -> bool:
        """Retorna True si el diagnóstico está siendo revisado por un odontólogo."""
        return self.value == "EN_REVISION"

    def es_validado(self) -> bool:
        """Retorna True si el diagnóstico fue validado por un odontólogo."""
        return self.value == "VALIDADO"

    def es_rechazado(self) -> bool:
        """Retorna True si el diagnóstico fue rechazado por un odontólogo."""
        return self.value == "RECHAZADO"

    def puede_validarse(self) -> bool:
        """Retorna True si el diagnóstico puede ser validado desde su estado actual."""
        return self.value in {"SUGERIDO_IA", "EN_REVISION"}

    def puede_rechazarse(self) -> bool:
        """Retorna True si el diagnóstico puede ser rechazado desde su estado actual."""
        return self.value in {"SUGERIDO_IA", "EN_REVISION"}


@dataclass(frozen=True)
class TipoPatologia(ValueObject):
    """
    Tipo de patología dental observable en fotografía intraoral.

    Attributes
    ----------
    value : str
        Valor permitido: CARIES | FRACTURA | CALCULO_DENTAL.
        (LESION_PERIAPICAL purgada por ser indetectable en fotografía óptica).

    Raises
    ------
    ValueError
        Si el valor no está entre los permitidos.
    """
    value: str

    _VALORES_PERMITIDOS = frozenset({
        "CARIES",
        "FRACTURA",
        "CALCULO_DENTAL",
    })

    def __post_init__(self) -> None:
        if self.value not in self._VALORES_PERMITIDOS:
            raise ValueError(
                f"Tipo de patología inválido: '{self.value}'. "
                f"Permitidos: {self._VALORES_PERMITIDOS}"
            )


@dataclass(frozen=True)
class Severidad(ValueObject):
    """
    Severidad clínica de un hallazgo.

    Attributes
    ----------
    value : str
        Valor permitido: LEVE | MODERADA | SEVERA.

    Raises
    ------
    ValueError
        Si el valor no está entre los permitidos.
    """
    value: str

    _VALORES_PERMITIDOS = frozenset({"LEVE", "MODERADA", "SEVERA"})

    def __post_init__(self) -> None:
        if self.value not in self._VALORES_PERMITIDOS:
            raise ValueError(
                f"Severidad inválida: '{self.value}'. "
                f"Permitidos: {self._VALORES_PERMITIDOS}"
            )


@dataclass(frozen=True)
class RegionDental(ValueObject):
    """
    Región dental donde se detectó el hallazgo.

    Attributes
    ----------
    diente_numero : int | None
        Número de diente en notación FDI (11-48). Opcional.
    cuadrante : int | None
        Cuadrante dental (1-4). Opcional.
    bbox_x : float | None
        Coordenada X del bounding box YOLO.
    bbox_y : float | None
        Coordenada Y del bounding box YOLO.
    bbox_width : float | None
        Ancho del bounding box YOLO.
    bbox_height : float | None
        Alto del bounding box YOLO.

    Raises
    ------
    ValueError
        Si el número de diente o cuadrante están fuera de rango.
    """
    diente_numero: Optional[int] = None
    cuadrante: Optional[int] = None
    bbox_x: Optional[float] = None
    bbox_y: Optional[float] = None
    bbox_width: Optional[float] = None
    bbox_height: Optional[float] = None

    def __post_init__(self) -> None:
        if self.diente_numero is not None:
            cuadrante = self.diente_numero // 10
            posicion = self.diente_numero % 10
            es_permanente = (1 <= cuadrante <= 4) and (1 <= posicion <= 8)
            es_deciduo = (5 <= cuadrante <= 8) and (1 <= posicion <= 5)
            if not (es_permanente or es_deciduo):
                raise ValueError(
                    f"Número de diente inválido: {self.diente_numero}. "
                    "Debe ser una pieza dental FDI válida (permanente 11-48 o decidua 51-85)."
                )
        if self.cuadrante is not None and self.cuadrante not in {1, 2, 3, 4, 5, 6, 7, 8}:
            raise ValueError(
                f"Cuadrante inválido: {self.cuadrante}. "
                "Debe ser entre 1 y 4 (permanente) o entre 5 y 8 (deciduo/infantil)."
            )

    def tiene_bbox(self) -> bool:
        """Retorna True si tiene coordenadas de bounding box."""
        return all(v is not None for v in [
            self.bbox_x, self.bbox_y, self.bbox_width, self.bbox_height
        ])


@dataclass(frozen=True)
class Hallazgo(ValueObject):
    """
    Patología detectada por el modelo ML en una imagen.

    Una fila en la tabla hallazgos = un Hallazgo.

    Attributes
    ----------
    imagen_id : UUID
        ID de la imagen donde se detectó el hallazgo.
    tipo_patologia : TipoPatologia
        Tipo de patología detectada.
    severidad : Severidad
        Severidad clínica del hallazgo.
    confianza : float
        Nivel de confianza del modelo (0.0 - 1.0).
    region : RegionDental
        Región dental con bounding box y referencia de diente.
    descripcion_clinica : str | None
        Descripción clínica opcional del hallazgo.

    Raises
    ------
    ValueError
        Si la confianza está fuera del rango [0.0, 1.0].
    """
    imagen_id: UUID
    tipo_patologia: TipoPatologia
    severidad: Severidad
    confianza: float
    region: RegionDental
    descripcion_clinica: Optional[str] = None

    def __post_init__(self) -> None:
        if not (0.0 <= self.confianza <= 1.0):
            raise ValueError(
                f"La confianza debe estar entre 0.0 y 1.0. Valor recibido: {self.confianza}"
            )


@dataclass(frozen=True)
class NivelConfianza(ValueObject):
    """
    Nivel de confianza global del diagnóstico completo.

    Calculado como promedio ponderado de los hallazgos.

    Attributes
    ----------
    valor : float
        Valor entre 0.0 y 1.0.
    categoria : str
        BAJA (< 0.5) | MEDIA (0.5 - 0.8) | ALTA (> 0.8).

    Raises
    ------
    ValueError
        Si el valor está fuera del rango [0.0, 1.0].
    """
    valor: float
    categoria: str

    _CATEGORIAS_PERMITIDAS = frozenset({"BAJA", "MEDIA", "ALTA"})

    def __post_init__(self) -> None:
        if not (0.0 <= self.valor <= 1.0):
            raise ValueError(
                f"El valor de confianza debe estar entre 0.0 y 1.0. "
                f"Valor recibido: {self.valor}"
            )
        if self.categoria not in self._CATEGORIAS_PERMITIDAS:
            raise ValueError(
                f"Categoría inválida: '{self.categoria}'. "
                f"Permitidas: {self._CATEGORIAS_PERMITIDAS}"
            )

    @staticmethod
    def desde_valor(valor: float) -> "NivelConfianza":
        """
        Crea un NivelConfianza calculando la categoría automáticamente.

        Parameters
        ----------
        valor : float
            Valor de confianza entre 0.0 y 1.0.

        Returns
        -------
        NivelConfianza
            Instancia con categoría calculada.
        """
        if valor < 0.5:
            categoria = "BAJA"
        elif valor <= 0.8:
            categoria = "MEDIA"
        else:
            categoria = "ALTA"
        return NivelConfianza(valor=valor, categoria=categoria)

    def requiere_revision_prioritaria(self) -> bool:
        """Retorna True si la confianza es BAJA y requiere segunda opinión."""
        return self.categoria == "BAJA"


@dataclass(frozen=True)
class RegistroModeloML(ValueObject):
    """
    Metadata del modelo ML que generó el diagnóstico.

    No es el modelo en sí (.pt) — es el registro de qué versión
    fue usada para garantizar trazabilidad clínica.

    Attributes
    ----------
    modelo_ml_id : UUID
        ID del modelo en la tabla modelos_ml.
    nombre_modelo : str
        Nombre del modelo.
    version : str
        Versión del modelo.
    f1_score : float
        F1-Score del modelo en validación.

    Raises
    ------
    ValueError
        Si f1_score está fuera del rango [0.0, 1.0].
    """
    modelo_ml_id: UUID
    nombre_modelo: str
    version: str
    f1_score: float

    def __post_init__(self) -> None:
        if not (0.0 <= self.f1_score <= 1.0):
            raise ValueError(
                f"F1-Score inválido: {self.f1_score}. Debe estar entre 0.0 y 1.0."
            )

    def es_aprobado_para_produccion(self) -> bool:
        """
        Verifica si el modelo cumple el umbral mínimo para producción.

        Returns
        -------
        bool
            True si f1_score >= 0.85.
        """
        return self.f1_score >= 0.85