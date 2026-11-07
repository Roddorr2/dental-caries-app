"""
domain_event.py
===============
Evento de dominio base para todo el sistema.
"""

from datetime import datetime, timezone
import uuid

class DomainEvent:
    """
    Evento de dominio base
    
    Attributes
    ----------
    event_id : str
        Identificador del evento de dominio
    occured_on : datetime
        Fecha y hora en la que ocurrió el evento de dominio    
    """
    
    def __init__(self) -> None:
        self.event_id: str = str(uuid.uuid4())
        self.occurred_on: datetime = datetime.now(tz=timezone.utc)

    @property
    def ocurred_on(self) -> datetime:
        """Alias para retrocompatibilidad."""
        return self.occurred_on