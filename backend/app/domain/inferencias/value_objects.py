"""
value_objects.py
================
Value Objects del Bounded Context: Gestión de Inferencias IA.
"""

from dataclasses import dataclass
from uuid import UUID

from app.domain.shared.value_object import ValueObject

@dataclass(frozen=True)
class InferenciaId(ValueObject):
    """
    Identificador único de una inferencia IA.

    Attributes
    ----------
    value : UUID
        UUID generado al crear la inferencia.
    """
    value: UUID


@dataclass(frozen=True)
class EstadoInferencia(ValueObject):
    """
    Estado del proceso de inferencia IA.

    Attributes
    ----------
    value : str
        Valor permitido: PENDIENTE | EN_PROCESO | COMPLETADO | FALLIDO.

    Raises
    ------
    ValueError
        Si el valor no está entre los permitidos.
    """
    value: str

    _VALORES_PERMITIDOS = frozenset({"PENDIENTE", "EN_PROCESO", "COMPLETADO", "FALLIDO"})

    def __post_init__(self) -> None:
        if self.value not in self._VALORES_PERMITIDOS:
            raise ValueError(
                f"Estado inválido: '{self.value}'. "
                f"Permitidos: {self._VALORES_PERMITIDOS}"
            )

    def es_pendiente(self) -> bool:
        """Retorna True si la inferencia está pendiente."""
        return self.value == "PENDIENTE"

    def es_en_proceso(self) -> bool:
        """Retorna True si la inferencia está en ejecución."""
        return self.value == "EN_PROCESO"

    def es_completado(self) -> bool:
        """Retorna True si la inferencia terminó exitosamente."""
        return self.value == "COMPLETADO"

    def es_fallido(self) -> bool:
        """Retorna True si la inferencia falló."""
        return self.value == "FALLIDO"


@dataclass(frozen=True)
class WorkerId(ValueObject):
    """
    Identificador del worker que ejecutó la inferencia.

    Attributes
    ----------
    value : str
        Nombre o ID del nodo/proceso worker. Máximo 100 caracteres.

    Raises
    ------
    ValueError
        Si el valor está vacío o supera 100 caracteres.
    """
    value: str

    def __post_init__(self) -> None:
        if not self.value or not self.value.strip():
            raise ValueError("El worker ID no puede estar vacío.")
        if len(self.value) > 100:
            raise ValueError("El worker ID no puede superar 100 caracteres.")


@dataclass(frozen=True)
class TiempoInferencia(ValueObject):
    """
    Tiempo total de ejecución de la inferencia en milisegundos.

    Attributes
    ----------
    valor_ms : float
        Tiempo en milisegundos. Debe ser mayor a 0.

    Raises
    ------
    ValueError
        Si el valor es menor o igual a 0.
    """
    valor_ms: float

    def __post_init__(self) -> None:
        if self.valor_ms <= 0:
            raise ValueError("El tiempo de inferencia debe ser mayor a 0 ms.")

    def en_segundos(self) -> float:
        """Retorna el tiempo convertido a segundos."""
        return self.valor_ms / 1000