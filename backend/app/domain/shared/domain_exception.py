"""
domain_exception.py
===================
Excepción base del dominio
"""

class DomainException(Exception):
    """
    Excepción base para violaciones de regla de negocio.
    
    Lanzada por entidades y agregados cuando se viola una invariante o regla de dominio.
    """
    pass
