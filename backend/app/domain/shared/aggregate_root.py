"""
aggregate_root.py
==================
Clase base AggregateRoot.
Gestiona los eventos de dominio de los agregados
"""

from typing import List, Any
from .domain_event import DomainEvent
from .entity import Entity

class AggregateRoot(Entity):
    """
    Raíz de agregado base para todos los agregados del dominio.
    
    Hereda de Entity: Igualdad por ID, tipado UUID.
    Gestiona el ciclo de vida de los eventos de dominio.
    
    Atributes
    ----------
    _events : List[DomainEvent]
        Lista de eventos de dominio pendientes.
    """

    def __init__(self, id: Any) -> None:
        super().__init__(id)
        self._events: List[DomainEvent] = []

    @property
    def events(self) -> List[DomainEvent]:
        """Devuelve los eventos pendientes del agregado"""
        return self._events
    
    def add_event(self, event: DomainEvent) -> None:
        """
        Añade un evento al agregado
        
        Parameters
        ----------
        event : DomainEvent
            Evento de dominio que ocurrión en el agregado
        """
        self._events.append(event)
    
    def clear_events(self) -> None:
        """Limpia los eventos pendientes tras su publicación"""
        self._events.clear()