"""
entities.py
===========
Entidades del Bounded Context: Gestión de Pacientes.
"""

from datetime import date, datetime, timezone
from uuid import UUID, uuid4

from app.domain.shared.aggregate_root import AggregateRoot
from app.domain.shared.domain_exception import DomainException
from app.domain.pacientes.value_objects import (
    DNI,
    Email,
    EstadoPaciente,
    NombreCompleto,
    Sexo,
    Telefono,
)
from app.domain.pacientes.events import PacienteDesactivado, PacienteRegistrado, PacienteActualizado

class Paciente(AggregateRoot):
    """
    Aggregate Root del BC: Gestión de pacientes.
    
    Attributes
    ----------
    id : UUID
        Identificador único del paciente.
    dni : DNI
        Documento de identidad peruano (8 dígitos).
    nombre : NombreCompleto
        Nombres y apellidos del paciente.
    fecha_nacimiento : date
        Fecha de nacimiento del paciente.
    estado : EstadoPaciente
        Estado actual en el sistema (ACTIVO o INACTIVO).
    sexo : Sexo
        Sexo del Paciente.
    telefono : Telefono
        Teléfono de contacto.
    email : Email
        Correo electrónico.
    created_at : datetime
        Timestamp UTC de creación.
    updated_at : datetime
        Timestamp UTC de actualización.
    """
    
    def __init__(self, id: UUID, dni: DNI, nombre: NombreCompleto, fecha_nacimiento: date, sexo: Sexo, telefono: Telefono, email: Email, estado: EstadoPaciente, created_at: datetime, updated_at: datetime) -> None:
        super().__init__(id)
        self.dni = dni
        self.nombre = nombre
        self.fecha_nacimiento = fecha_nacimiento
        self.sexo = sexo
        self.telefono = telefono
        self.email = email
        self.estado = estado
        self.created_at = created_at
        self.updated_at = updated_at
    
    @staticmethod
    def registrar(dni: DNI, nombre: NombreCompleto, fecha_nacimiento: date, sexo: Sexo, telefono: Telefono, email: Email) -> "Paciente":
        """
        Crea y registra un nuevo paciente en el sistema.

        Parameters
        ----------
        dni : DNI
            Documento de identidad del paciente.
        nombre : NombreCompleto
            Nombres y apellidos.
        fecha_nacimiento : date
            Fecha de nacimiento.
        sexo : Sexo
            Sexo del paciente.
        telefono : Telefono
            Teléfono de contacto.
        email : Email
            Correo electrónico.

        Returns
        -------
        Paciente
            Nueva instancia con estado ACTIVO y evento PacienteRegistrado emitido.
        """
        ahora = datetime.now(tz=timezone.utc)
        paciente = Paciente(
            id=uuid4(),
            dni=dni,
            nombre=nombre,
            fecha_nacimiento=fecha_nacimiento,
            sexo=sexo,
            telefono=telefono,
            email=email,
            estado=EstadoPaciente(value="ACTIVO"),
            created_at=ahora,
            updated_at=ahora,
        )
        paciente.add_event(
            PacienteRegistrado(
                paciente_id=paciente.id,
                dni=dni.value,
                nombre_completo=nombre.completo(),
            )
        )
        return paciente
    
    def puede_recibir_nuevo_estudio(self) -> bool:
        """
        Verifica si el paciente puede recibir un nuevo estudio imagenológico
        
        Returns
        -------
        bool
            True si el paciente está ACTIVO
        """
        return self.estado.es_activo()

    def actualizar_contacto(self, telefono: Telefono, email: Email) -> None:
        """
        Actualiza los datos de contacto del paciente.
        
        Parameters
        ----------
        telefono : Telefono
            Nuevo teléfono de contacto.
        email : Email
            Nuevo correo electrónico.
        """
        if not self.estado.es_activo():
            raise DomainException("No se puede actualizar un paciente inactivo.")
        
        self.telefono = telefono
        self.email = email
        self.updated_at = datetime.now(tz=timezone.utc)
        self.add_event(
            PacienteActualizado(
                paciente_id=self.id,
                campos_actualizados=["telefono", "email"],
            )
        )
    
    def desactivar(self) -> None:
        """
        Desactiva al paciente en el sistema.

        Raises
        ------
        DomainException
            Si el paciente ya está inactivo.
        """
        if not self.estado.es_activo():
            raise DomainException("El paciente ya se encuentra inactivo.")
        
        self.estado = EstadoPaciente(value="INACTIVO")
        self.updated_at = datetime.now(tz=timezone.utc)
        self.add_event(PacienteDesactivado(paciente_id=self.id))
