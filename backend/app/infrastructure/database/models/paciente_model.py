"""
paciente_model.py
=================
ORM model para la tabla `pacientes`.

NO es la entidad de dominio Paciente.
Es la representación de la tabla relacional en SQLAlchemy.
"""

from datetime import datetime
from uuid import UUID
import uuid

from sqlalchemy import String, DateTime, Boolean, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from app.infrastructure.database.base import Base

class PacienteORM(Base):
    """
    Tabla: pacientes

    Columns
    -------
    id : UUID (PK)
    dni : VARCHAR(8) — único, exactamente 8 dígitos
    nombres : VARCHAR(100)
    apellidos : VARCHAR(100)
    fecha_nacimiento : DATE
    sexo : ENUM('MASCULINO', 'FEMENINO', 'OTRO')
    telefono : VARCHAR(20)
    email : VARCHAR(150)
    estado : ENUM('ACTIVO', 'INACTIVO')
    created_at : TIMESTAMP WITH TIME ZONE
    updated_at : TIMESTAMP WITH TIME ZONE
    """
    __tablename__ = "pacientes"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    dni: Mapped[str] = mapped_column(
        String(8),
        unique=True,
        nullable=False,
        index=True,
    )
    nombres: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    apellidos: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    fecha_nacimiento: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    sexo: Mapped[str] = mapped_column(
        Enum("MASCULINO", "FEMENINO", "OTRO", name="sexo_enum"),
        nullable=False,
    )
    telefono: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )
    email: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )
    estado: Mapped[str] = mapped_column(
        Enum("ACTIVO", "INACTIVO", name="estado_paciente_enum"),
        nullable=False,
        default="ACTIVO",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    estudios: Mapped[list["EstudioORM"]] = relationship(
        "EstudioORM",
        back_populates="paciente",
        cascade="all, delete-orphan",
        lazy="select",
    )



