"""
auditoria_model.py
==================
ORM models para las tablas de auditoría (append-only):
- auditoria_diagnosticos
- auditoria_estudios

Estas tablas NUNCA se actualizan ni se borran registros.
Solo se insertan — son el log de cambios de estado.
"""

from datetime import datetime
from uuid import UUID
import uuid

from sqlalchemy import String, DateTime, ForeignKey, Text, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from app.infrastructure.database.base import Base

class AuditoriaDiagnosticoORM(Base):
    """
    Tabla: auditoria_diagnosticos

    Registra cada cambio de estado de un diagnóstico.
    Append-only — no UPDATE, no DELETE.

    Columns
    -------
    id : UUID (PK)
    diagnostico_id : UUID (FK → diagnosticos)
    odontologo_id : UUID (nullable)
    estado_anterior : ENUM
    estado_nuevo : ENUM
    notas : TEXT (nullable)
    created_at : TIMESTAMP WITH TIME ZONE
    """

    __tablename__ = "auditoria_diagnosticos"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    diagnostico_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("diagnosticos.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    odontologo_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        nullable=True,
    )
    estado_anterior: Mapped[str] = mapped_column(
        SAEnum("SUGERIDO_IA", "EN_REVISION", "VALIDADO", "RECHAZADO", name="estado_diag_audit_enum",),
        nullable=False,
    )
    estado_nuevo: Mapped[str] = mapped_column(
        SAEnum("SUGERIDO_IA", "EN_REVISION", "VALIDADO", "RECHAZADO", name="estado_diag_nuevo_enum",),
        nullable=False,
    )
    notas: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
    )


class AuditoriaEstudioORM(Base):
    """
    Tabla: auditoria_estudios

    Registra cada cambio de estado de un estudio imagenológico.
    Append-only — no UPDATE, no DELETE.

    Columns
    -------
    id : UUID (PK)
    estudio_id : UUID (FK → estudios_imagenologicos)
    estado_anterior : ENUM
    estado_nuevo : ENUM
    created_at : TIMESTAMP WITH TIME ZONE
    """

    __tablename__ = "auditoria_estudios"

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
    estado_anterior: Mapped[str] = mapped_column(
        SAEnum("PENDIENTE", "EN_ANALISIS", "PROCESADO", name="estado_estudio_ant_enum",),
        nullable=False,
    )
    estado_nuevo: Mapped[str] = mapped_column(
        SAEnum("PENDIENTE", "EN_ANALISIS", "PROCESADO", name="estado_estudio_nuevo_enum",),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
    )