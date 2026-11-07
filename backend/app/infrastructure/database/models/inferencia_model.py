"""
inferencia_model.py
===================
ORM model para la tabla `inferencias_ia`.
"""

from datetime import datetime
from uuid import UUID
import uuid

from sqlalchemy import String, DateTime, Float, ForeignKey, Text, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from app.infrastructure.database.base import Base

class InferenciaIAORM(Base):
    """
    Tabla: inferencias_ia

    Registra el proceso técnico de ejecución ML.
    No es el diagnóstico clínico — es el proceso que lo genera.

    Columns
    -------
    id : UUID (PK)
    estudio_id : UUID (FK → estudios_imagenologicos)
    modelo_ml_id : UUID (FK → modelos_ml)
    estado : ENUM
    worker_id : VARCHAR(100) — nullable hasta que inicia
    gpu_utilizada : VARCHAR(100) — nullable
    tiempo_ms : FLOAT — nullable hasta completar
    error_mensaje : TEXT — nullable, solo si FALLIDO
    created_at : TIMESTAMP WITH TIME ZONE
    completed_at : TIMESTAMP WITH TIME ZONE — nullable
    """

    __tablename__ = "inferencias_ia"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    estudio_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("estudios_imagenologicos.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    modelo_ml_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("modelos_ml.id", ondelete="RESTRICT"),
        nullable=False,
    )
    estado: Mapped[str] = mapped_column(
        SAEnum(
            "PENDIENTE", "EN_PROCESO", "COMPLETADO", "FALLIDO",
            name="estado_inferencia_enum",
        ),
        nullable=False,
        default="PENDIENTE",
        index=True,
    )
    worker_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    gpu_utilizada: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    tiempo_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    error_mensaje: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )


    estudio: Mapped["EstudioORM"] = relationship(
        "EstudioORM",
        back_populates="inferencias",
    )
    modelo_ml: Mapped["ModeloMLORM"] = relationship(
        "ModeloMLORM",
        back_populates="inferencias",
    )
    diagnostico: Mapped["DiagnosticoORM | None"] = relationship(
        "DiagnosticoORM",
        foreign_keys="DiagnosticoORM.inferencia_id",
        back_populates=None,
        uselist=False,
        lazy="select",
    )