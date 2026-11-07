"""
rm_historial.py
===============
ORM model para la tabla CQRS read side: `rm_historial_paciente`.

Se actualiza mediante event handlers al validar/rechazar un diagnóstico.
Solo lectura desde la API — no es write model.
"""

from datetime import datetime
from uuid import UUID
import uuid

from sqlalchemy import String, DateTime, Float, Integer, Text, Enum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from app.infrastructure.database.base import Base

class RMHistorialPacienteORM(Base):
    """
    Tabla: rm_historial_paciente

    Read model desnormalizado para consulta rápida del historial
    de un paciente sin necesidad de JOINs complejos.

    Columns
    -------
    id : UUID (PK)
    paciente_id : UUID (indexed)
    estudio_id : UUID
    diagnostico_id : UUID
    fecha_estudio : TIMESTAMP WITH TIME ZONE
    tipo_examen : VARCHAR(50)
    estado_diagnostico : ENUM
    total_hallazgos : INTEGER
    confianza_global : FLOAT
    odontologo_nombre : VARCHAR(200) (nullable)
    fecha_validacion : TIMESTAMP WITH TIME ZONE (nullable)
    updated_at : TIMESTAMP WITH TIME ZONE
    """

    __tablename__ = "rm_historial_paciente"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
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
    diagnostico_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        nullable=False,
    )
    fecha_estudio: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    tipo_examen: Mapped[str] = mapped_column(String(50), nullable=False)
    estado_diagnostico: Mapped[str] = mapped_column(
        Enum("SUGERIDO_IA", "EN_REVISION", "VALIDADO", "RECHAZADO", name="rm_estado_diag_enum",),
        nullable=False,
    )
    total_hallazgos: Mapped[int] = mapped_column(Integer, nullable=False)
    confianza_global: Mapped[float] = mapped_column(Float, nullable=False)
    odontologo_nombre: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
    )
    fecha_validacion: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )