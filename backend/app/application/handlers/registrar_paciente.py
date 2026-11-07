"""
registrar_paciente.py
=====================
Handler para el comando RegistrarPacienteCommand.
"""

from uuid import UUID

from app.application.commands.registrar_paciente import RegistrarPacienteCommand
from app.domain.pacientes.entities import Paciente
from app.domain.pacientes.repository import IPacienteRepository
from app.domain.pacientes.value_objects import (
    DNI,
    Email,
    NombreCompleto,
    Sexo,
    Telefono,
)
from app.domain.shared.domain_exception import DomainException

class RegistrarPacienteHandler:
    """
    Caso de uso: registrar un nuevo paciente.

    Orquesta:
    1. Validar que el DNI no exista
    2. Construir VOs de dominio
    3. Crear entidad Paciente via factory method
    4. Persistir
    """

    def __init__(self, repo: IPacienteRepository) -> None:
        self._repo = repo

    def handle(self, cmd: RegistrarPacienteCommand) -> UUID:
        """
        Ejecuta el comando.

        Returns
        -------
        UUID
            ID del paciente registrado.

        Raises
        ------
        DomainException
            Si el DNI ya está registrado.
        ValueError
            Si algún VO no supera su propia validación.
        """
        dni = DNI(cmd.dni)

        if self._repo.exists_by_dni(dni):
            raise DomainException(
                f"Ya existe un paciente registrado con el DNI '{cmd.dni}'."
            )

        paciente = Paciente.registrar(
            dni=dni,
            nombre=NombreCompleto(nombres=cmd.nombres, apellidos=cmd.apellidos),
            fecha_nacimiento=cmd.fecha_nacimiento,
            sexo=Sexo(cmd.sexo),
            telefono=Telefono(cmd.telefono),
            email=Email(cmd.email),
        )

        self._repo.save(paciente)
        return paciente.id