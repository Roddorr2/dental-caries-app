"""
paciente_schemas.py
===================
DTOs Pydantic para el recurso Paciente.

PacienteCreate  → request body POST /pacientes
PacienteResponse → response body GET/POST /pacientes
"""

from datetime import date
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class PacienteCreate(BaseModel):
    """
    Request body para registrar un nuevo paciente.

    Attributes
    ----------
    dni : str
        Documento de identidad peruano. Exactamente 8 dígitos.
    nombres : str
        Nombres del paciente.
    apellidos : str
        Apellidos del paciente.
    fecha_nacimiento : date
        Fecha de nacimiento.
    sexo : str
        'M', 'F' u 'OTRO'.
    telefono : str
        Teléfono en formato peruano (9XXXXXXXX) o internacional (+X...).
    email : EmailStr
        Correo electrónico válido.
    """

    dni: str = Field(..., min_length=8, max_length=8, pattern=r"^\d{8}$")
    nombres: str = Field(..., min_length=1, max_length=100)
    apellidos: str = Field(..., min_length=1, max_length=100)
    fecha_nacimiento: date
    sexo: str = Field(..., pattern=r"^(M|F|OTRO)$")
    telefono: str = Field(..., max_length=20)
    email: EmailStr


class PacienteResponse(BaseModel):
    """
    Response body para datos de un paciente.

    Attributes
    ----------
    id : UUID
        Identificador único.
    dni : str
        Documento de identidad.
    nombres : str
        Nombres del paciente.
    apellidos : str
        Apellidos del paciente.
    fecha_nacimiento : date
        Fecha de nacimiento.
    sexo : str
        Sexo del paciente.
    telefono : str
        Teléfono de contacto.
    email : str
        Correo electrónico.
    estado : str
        'ACTIVO' o 'INACTIVO'.
    """

    id: UUID
    dni: str
    nombres: str
    apellidos: str
    fecha_nacimiento: date
    sexo: str
    telefono: str
    email: str
    estado: str

    model_config = {"from_attributes": True}