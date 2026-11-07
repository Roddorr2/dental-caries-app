"""
paciente_repo.py
================
Implementación SQLAlchemy de IPacienteRepository.
"""

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.domain.pacientes.entities import Paciente
from app.domain.pacientes.repository import IPacienteRepository
from app.domain.pacientes.value_objects import (
    DNI,
    Email,
    EstadoPaciente,
    NombreCompleto,
    PacienteId,
    Sexo,
    Telefono,
)
from app.infrastructure.database.models.paciente_model import PacienteORM


class SQLAlchemyPacienteRepository(IPacienteRepository):
    """
    Repositorio de pacientes — SQLAlchemy.
    El dominio nunca ve PacienteORM. La infra nunca ejecuta lógica de negocio.
    """

    def __init__(self, db: Session) -> None:
        self._db = db

    @staticmethod
    def _to_domain(orm: PacienteORM) -> Paciente:
        sexo_val = orm.sexo
        if sexo_val == "MASCULINO":
            sexo_domain = "M"
        elif sexo_val == "FEMENINO":
            sexo_domain = "F"
        else:
            sexo_domain = sexo_val

        return Paciente(
            id=orm.id,
            dni=DNI(value=orm.dni),
            nombre=NombreCompleto(nombres=orm.nombres, apellidos=orm.apellidos),
            fecha_nacimiento=orm.fecha_nacimiento.date() if isinstance(orm.fecha_nacimiento, datetime) else orm.fecha_nacimiento,
            sexo=Sexo(value=sexo_domain),
            telefono=Telefono(value=orm.telefono),
            email=Email(value=orm.email),
            estado=EstadoPaciente(value=orm.estado),
            created_at=orm.created_at,
            updated_at=orm.updated_at,
        )

    @staticmethod
    def _to_orm(paciente: Paciente) -> PacienteORM:
        sexo_val = paciente.sexo.value
        if sexo_val == "M":
            sexo_orm = "MASCULINO"
        elif sexo_val == "F":
            sexo_orm = "FEMENINO"
        else:
            sexo_orm = sexo_val

        return PacienteORM(
            id=paciente.id,
            dni=paciente.dni.value,
            nombres=paciente.nombre.nombres,
            apellidos=paciente.nombre.apellidos,
            fecha_nacimiento=datetime(
                paciente.fecha_nacimiento.year,
                paciente.fecha_nacimiento.month,
                paciente.fecha_nacimiento.day,
                tzinfo=timezone.utc,
            ),
            sexo=sexo_orm,
            telefono=paciente.telefono.value,
            email=paciente.email.value,
            estado=paciente.estado.value,
            created_at=paciente.created_at,
            updated_at=paciente.updated_at,
        )

    def save(self, paciente: Paciente) -> None:
        existing = self._db.get(PacienteORM, paciente.id)

        if existing is None:
            self._db.add(self._to_orm(paciente))
        else:
            existing.nombres = paciente.nombre.nombres
            existing.apellidos = paciente.nombre.apellidos
            existing.telefono = paciente.telefono.value
            existing.email = paciente.email.value
            existing.estado = paciente.estado.value
            existing.updated_at = paciente.updated_at

        self._db.flush()

    def get_by_id(self, paciente_id: PacienteId) -> Paciente | None:
        orm = self._db.get(PacienteORM, paciente_id.value)
        return self._to_domain(orm) if orm else None

    def get_by_dni(self, dni: DNI) -> Paciente | None:
        orm = (
            self._db.query(PacienteORM)
            .filter(PacienteORM.dni == dni.value)
            .first()
        )
        return self._to_domain(orm) if orm else None

    def exists_by_dni(self, dni: DNI) -> bool:
        return (
            self._db.query(PacienteORM.id)
            .filter(PacienteORM.dni == dni.value)
            .first()
        ) is not None

    def list_activos(self, limit: int = 50, offset: int = 0) -> list[Paciente]:
        rows = (
            self._db.query(PacienteORM)
            .filter(PacienteORM.estado == "ACTIVO")
            .order_by(PacienteORM.apellidos)
            .limit(limit)
            .offset(offset)
            .all()
        )
        return [self._to_domain(row) for row in rows]