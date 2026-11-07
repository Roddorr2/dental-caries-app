"""
rm_estadisticas.py
==================
ORM model para la tabla CQRS read side: `rm_estadisticas_modelo`.

Se actualiza cuando un diagnóstico es validado o rechazado.
Permite consultar el rendimiento real de cada modelo en producción.
"""

from datetime import datetime
from uuid import UUID
import uuid

from sqlalchemy import String, DateTime, Float, Integer
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from app.infrastructure.database.base import Base

class RMEstadisticasModeloORM(Base):
    """
    Tabla: rm_estadisticas_modelo

    Read model de métricas de rendimiento de cada modelo ML
    calculadas sobre los diagnósticos reales validados por odontólogos.

    Columns
    -------
    id : UUID (PK)
    modelo_ml_id : UUID (indexed, unique — una fila por modelo)
    nombre_modelo : VARCHAR(100)
    version : VARCHAR(20)
    total_diagnosticos : INTEGER
    total_validados : INTEGER
    total_rechazados : INTEGER
    tasa_validacion : FLOAT — validados / total
    tasa_segunda_opinion : FLOAT — diagnósticos BAJA / total
    updated_at : TIMESTAMP WITH TIME ZONE
    """

    __tablename__ = "rm_estadisticas_modelo"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    modelo_ml_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        nullable=False,
        unique=True,
        index=True,
    )
    nombre_modelo: Mapped[str] = mapped_column(String(100), nullable=False)
    version: Mapped[str] = mapped_column(String(20), nullable=False)
    total_diagnosticos: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    total_validados: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    total_rechazados: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    tasa_validacion: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )
    tasa_segunda_opinion: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )