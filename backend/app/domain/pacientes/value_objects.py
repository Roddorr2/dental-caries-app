"""
value_objects.py
================
Value objects del Bounded Context: Gestión de pacientes.
"""

import re
from dataclasses import dataclass
from uuid import UUID

from app.domain.shared.value_object import ValueObject

@dataclass(frozen=True)
class PacienteId(ValueObject):
    """
    Identificador único del paciente.
    
    Attributes
    ---------
    value : UUID
        UUID generado al registrar el paciente.
    """
    value: UUID

@dataclass(frozen=True)    
class DNI(ValueObject):
    """
    Documento de identidad del paciente.
    
    Attributes
    ----------
    value : str
        Número de DNI. Máximo 8 dígitos.
    
    Raises
    ------
    ValueError
        Si el valor está vacío o supera 8 dígitos. 
    """
    value: str
    
    def __post_init__(self) -> None:
        if not self.value or not self.value.strip():
            raise ValueError("El DNI no puede estar vacío.")
        if not self.value.isdigit():
            raise ValueError("El DNI debe contener solo dígitos.")
        if len(self.value) > 8:
            raise ValueError("El DNI no puede superar 8 dígitos.")

@dataclass(frozen=True)
class NombreCompleto(ValueObject):
    """
    Nombre completo del paciente separado entre nombres y apellidos.
    
    Attributes
    ----------
    nombres : str
        Nombres del paciente.
    apellidos : str
        Apellidos del paciente.
    
    Raises
    ------
    ValueError
        Si los nombres o apellidos están vacíos.
    """
    nombres: str
    apellidos: str
    def __post_init__(self) -> None:
        if not self.nombres or not self.nombres.strip():
            raise ValueError("Los nombres no pueden estar vacíos.")
        if not self.apellidos or not self.apellidos.strip():
            raise ValueError("Los apellidos no pueden estar vacíos.")
    
    def completo(self) -> str:
        """Retorna nombres y apellidos concatenados."""
        return f"{self.nombres} {self.apellidos}"
    

@dataclass(frozen=True)
class Sexo(ValueObject):
    """
    Sexo biológico del paciente.
    
    Attributes
    ----------
    value : str
        Valor permitiro: 'M', 'F' u 'OTRO'
        
    Raises
    ------
    ValueError
        Si el valor no está entre los permitidos.
    """
    value: str
    
    _VALORES_PERMITIDOS = frozenset({"M", "F", "OTRO"})
    
    def __post_init__(self) -> None:
        if self.value == "MASCULINO":
            object.__setattr__(self, "value", "M")
        elif self.value == "FEMENINO":
            object.__setattr__(self, "value", "F")
        elif self.value not in self._VALORES_PERMITIDOS:
            raise ValueError(f"Sexo inválido: '{self.value}'. Permitidos: {set(self._VALORES_PERMITIDOS)}")

@dataclass(frozen=True)
class Telefono(ValueObject):
    """
    Número de teléfono del paciente.
    
    Acepta formato peruano o internacional con prefijo '+'.
    
    Attributes
    ----------
    value : str
        Número de teléfono.
    
    Raises
    ------
    ValueError
        Si el formato no es válido.
    """
    value: str
    
    _PATRON = re.compile(r"^(\+\d{7,15}|9\d{8})$")
    
    def __post_init__(self) -> None:
        if not self.value or not self.value.strip():
            raise ValueError("El teléfono no puede estar vacío.")
        if not self._PATRON.match(self.value):
            raise ValueError("Formato de teléfono inválido.")

@dataclass(frozen=True)        
class Email(ValueObject):
    """
    Correo electrónico del paciente.
    
    Attributes
    ----------
    value : str
        Dirección de correo electrónico.
    
    Raises
    ------
    ValueError
        Si el formato no es válido o supera 150 caracteres
    """
    value : str
    
    _PATRON = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
    
    def __post_init__(self) -> None:
        if not self.value or not self.value.strip():
            raise ValueError("El correo no puede estar vacío.")
        if len(self.value) > 150:
            raise ValueError("El correo no puede superar los 150 caracteres")
        if not self._PATRON.match(self.value):
            raise ValueError(f"Correo inválido: '{self.value}'")

@dataclass(frozen=True)
class EstadoPaciente(ValueObject):
    """
    Estado del paciente en el sistema.
    
    Attributes
    ----------
    value : str
        Valor permitido: 'ACTIVO' o 'INACTIVO'.
    
    Raises
    ------
    ValueError
        Si el valor no está entre los permitidos.
    """
    value: str
    
    _VALORES_PERMITIDOS = frozenset({"ACTIVO", "INACTIVO"})
    
    def __post_init__(self) -> None:
        if self.value not in self._VALORES_PERMITIDOS:
            raise ValueError(f"Estado inválido: '{self.value}'. Permitidos: {self._VALORES_PERMITIDOS}")
    
    def es_activo(self) -> bool:
        """Retorna True si el paciente está activo."""
        return self.value == "ACTIVO"