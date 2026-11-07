"""
entity.py
=========
Entidad base para el dominio
"""

from typing import Any
from uuid import UUID

class Entity:
    """
    Entidad base: Igualdad por ID
    
    Attributes
    ----------
    id: UUID
        Identificador único de la entidad
    """
    
    def __init__(self, id: UUID) -> None:
        self.id = id
    
    def __eq__(self, other: object) -> bool:
        """Compara por ID"""
        if not isinstance(other, Entity):
            return False
        return self.id == other.id
    
    def __hash__(self) -> int:
        return hash(self.id)
