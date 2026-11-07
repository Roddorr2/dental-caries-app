"""
rm_cola.py
==========
ORM model para la tabla CQRS read side: `rm_cola_revision`.

Se inserta cuando se genera un DiagnosticoSugeridoPorIA.
Se elimina cuando se valida o rechaza el diagnóstico.
"""

from datetime import datetime
from uuid import UUID
import uuid

from sqlalchemy import String, DateTime, Float, Boolean, Enum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from app.infrastructure.database.base import Base

class RMColaRevisionORM(Base):
    """
    Tabla: rm_cola_revision

    Read model de la cola de diagnósticos pendientes de revisión.
    Permite al odontólogo ver rápidamente qué casos necesitan atención.

    Columns
    -------
    id : UUID (PK)
    diagnostico_id : UUID (indexed)
    paciente_id : UUID
    estudio_id : UUID
    paciente_nombre : VARCHAR(200)
    tipo_examen : VARCHAR(50)
    confianza_global : FLOAT
    categoria_confianza : ENUM
    segunda_opinion : BOOLEAN — True si confianza BAJA
    fecha_generacion : TIMESTAMP WITH TIME ZONE
    created_at : TIMESTAMP WITH TIME ZONE
    """

    __tablename__ = "rm_cola_revision"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    diagnostico_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        nullable=False,
        unique=True,
        index=True,
    )
    paciente_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        nullable=False,
        index=True,
    )
    estudio_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        nullable=False,
    )
    paciente_nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    tipo_examen: Mapped[str] = mapped_column(String(50), nullable=False)
    confianza_global: Mapped[float] = mapped_column(Float, nullable=False)
    categoria_confianza: Mapped[str] = mapped_column(Enum(
        "BAJA", "MEDIA", "ALTA", name="rm_cola_confianza_enum"),
        nullable=False,
    )
    segunda_opinion: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )
    fecha_generacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
    )