"""
event_bus.py
============
Event Bus del sistema — IEventBus e InMemoryEventBus.

El Event Bus desacopla a los emisores de eventos (agregados)
de los handlers que reaccionan a ellos (read model updaters).

Flujo completo:
    1. Un agregado emite eventos mediante add_event()
    2. El handler de comando llama a event_bus.publish(agregado.events)
    3. El bus despacha cada evento al handler registrado
    4. El handler actualiza el read model correspondiente
    5. El agregado limpia sus eventos con clear_events()

InMemoryEventBus es síncrono — apropiado para la tesis.
En producción con alta carga se reemplazaría por un bus
asíncrono (Redis Streams, RabbitMQ, etc.) sin tocar el dominio.
"""

import logging
from abc import ABC, abstractmethod
from collections import defaultdict
from typing import Callable

from app.domain.shared.domain_event import DomainEvent

logger = logging.getLogger(__name__)

EventHandler = Callable[[DomainEvent], None]

class IEventBus(ABC):
    """
    Interfaz del Event Bus.

    Define el contrato para publicar eventos de dominio
    y registrar handlers. El dominio no importa esta interfaz —
    vive en infraestructura porque el bus es un detalle técnico.
    """

    @abstractmethod
    def subscribe(self, event_type: type, handler: EventHandler) -> None:
        """
        Registra un handler para un tipo de evento.

        Parameters
        ----------
        event_type : type
            Clase del evento de dominio (e.g. DiagnosticoValidado).
        handler : EventHandler
            Función que procesa el evento.
        """
        ...

    @abstractmethod
    def publish(self, events: list[DomainEvent]) -> None:
        """
        Publica una lista de eventos y despacha a los handlers registrados.

        Parameters
        ----------
        events : list[DomainEvent]
            Lista de eventos emitidos por un agregado.
        """
        ...


class InMemoryEventBus(IEventBus):
    """
    Event Bus síncrono en memoria.

    Apropiado para el alcance de la tesis — no requiere
    infraestructura externa (Redis, RabbitMQ).

    Los handlers se ejecutan en el mismo hilo y transacción
    que el comando que los originó. Si un handler falla,
    el caller puede hacer rollback de toda la operación.
    """

    def __init__(self) -> None:
        self._handlers: dict[type, list[EventHandler]] = defaultdict(list)

    def subscribe(self, event_type: type, handler: EventHandler) -> None:
        """
        Registra un handler para un tipo de evento.

        Permite múltiples handlers por tipo de evento.
        El orden de ejecución es el orden de registro.

        Parameters
        ----------
        event_type : type
            Clase del evento de dominio.
        handler : EventHandler
            Función que procesa el evento.
        """
        self._handlers[event_type].append(handler)
        logger.debug(
            "Handler '%s' registrado para evento '%s'.",
            handler.__name__,
            event_type.__name__,
        )

    def publish(self, events: list[DomainEvent]) -> None:
        """
        Despacha cada evento a sus handlers registrados.

        Si un handler lanza una excepción, la propaga al caller
        para que pueda hacer rollback. No silencia errores.

        Parameters
        ----------
        events : list[DomainEvent]
            Lista de eventos a publicar.
        """
        for event in events:
            event_type = type(event)
            handlers = self._handlers.get(event_type, [])

            if not handlers:
                logger.debug(
                    "Evento '%s' publicado sin handlers registrados.",
                    event_type.__name__,
                )
                continue

            for handler in handlers:
                logger.debug(
                    "Despachando evento '%s' a handler '%s'.",
                    event_type.__name__,
                    handler.__name__,
                )
                handler(event)