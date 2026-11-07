"""
value_object.py
===============
ValueObject base para el dominio
"""

from dataclasses import dataclass

@dataclass(frozen=True)
class ValueObject:
    """
    Objecto de valor base
    
    Inmutable y con compraración por contenido
    
    Notes
    -----
    Toda subclase DEBE declarar @dataclass(frozen=True) para
    garantizar inmutabilidad. Sin el decorador, el objeto no
    será inmutable aunque herede de ValueObject.
    """
    pass