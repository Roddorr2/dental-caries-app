"""
registrar_paciente.py
=====================
Command para registrar un nuevo paciente en el sistema.
"""

from dataclasses import dataclass
from datetime import date

@dataclass(frozen=True)
class RegistrarPacienteCommand:
    """
    Intención de escritura: registrar un nuevo paciente.

    Inmutable — no contiene lógica, solo datos de entrada validados por Pydantic
    en la capa API antes de llegar aquí.

    Attributes
    ----------
    dni : str
        Documento de identidad (8 dígitos).
    nombres : str
        Nombres del paciente.
    apellidos : str
        Apellidos del paciente.
    fecha_nacimiento : date
        Fecha de nacimiento.
    sexo : str
        'M', 'F' u 'OTRO'.
    telefono : str
        Teléfono de contacto.
    email : str
        Correo electrónico.
    """
    dni: str
    nombres: str
    apellidos: str
    fecha_nacimiento: date
    sexo: str
    telefono: str
    email: str