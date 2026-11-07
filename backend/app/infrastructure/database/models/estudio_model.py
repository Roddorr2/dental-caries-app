"""
estudio_model.py
================
ORM models para las tablas `estudios_imagenologicos` e `imagenes_intraorales`.
"""

from datetime import datetime
from uuid import UUID
import uuid

from sqlalchemy import Boolean, String, DateTime, Float, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID

SAEnum = Enum

from app.infrastructure.database.base import Base

class EstudioORM(Base):
    """
    Tabla: estudios_imagenologicos

    Columns
    -------
    id : UUID (PK)
    paciente_id : UUID (FK → pacientes)
    tipo_examen : ENUM
    estado_procesamiento : ENUM
    created_at : TIMESTAMP WITH TIME ZONE
    updated_at : TIMESTAMP WITH TIME ZONE
    """

    __tablename__ = "estudios_imagenologicos"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    paciente_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("pacientes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    tipo_examen: Mapped[str] = mapped_column(
        Enum(
            "FOTOGRAFIA_INTRAORAL",
            "SERIE_COMPLETA",
            "OCLUSAL_MANDIBULAR",
            "OCLUSAL_MAXILAR",
            "FRONTAL_VESTIBULAR",
            "LATERAL_DERECHA",
            "LATERAL_IZQUIERDA",
            name="tipo_examen_enum",
        ),
        nullable=False,
    )
    estado_procesamiento: Mapped[str] = mapped_column(
        Enum("PENDIENTE", "EN_ANALISIS", "PROCESADO",name="estado_procesamiento_enum",),
        nullable=False,
        default="PENDIENTE",
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


    paciente: Mapped["PacienteORM"] = relationship(
        "PacienteORM",
        back_populates="estudios",
    )
    imagenes: Mapped[list["ImagenIntraoralORM"]] = relationship(
        "ImagenIntraoralORM",
        back_populates="estudio",
        cascade="all, delete-orphan",
        lazy="select",
    )
    inferencias: Mapped[list["InferenciaIAORM"]] = relationship(
        "InferenciaIAORM",
        back_populates="estudio",
        cascade="all, delete-orphan",
        lazy="select",
    )
    diagnosticos: Mapped[list["DiagnosticoORM"]] = relationship(
        "DiagnosticoORM",
        back_populates="estudio",
        cascade="all, delete-orphan",
        lazy="select",
    )


class ImagenIntraoralORM(Base):
    """
    Tabla: imagenes_intraorales

    Columns
    -------
    id : UUID (PK)
    estudio_id : UUID (FK → estudios_imagenologicos)
    tipo_vista : ENUM
    formato : ENUM
    ruta_almacenamiento : VARCHAR(500)
    hash_sha256 : VARCHAR(64) — único, para deduplicación
    nitidez : FLOAT (nullable)
    iluminacion : FLOAT (nullable)
    calidad_suficiente : BOOLEAN
    created_at : TIMESTAMP WITH TIME ZONE
    """

    __tablename__ = "imagenes_intraorales"

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
    tipo_vista: Mapped[str] = mapped_column(
        SAEnum(
            "OCLUSAL_MANDIBULAR",
            "OCLUSAL_MAXILAR",
            "FRONTAL_VESTIBULAR",
            "LATERAL_DERECHA",
            "LATERAL_IZQUIERDA",
            name="tipo_vista_enum",
        ),
        nullable=False,
    )
    formato: Mapped[str] = mapped_column(
        SAEnum("JPG", "JPEG", "PNG", name="formato_imagen_enum"),
        nullable=False,
    )
    ruta_almacenamiento: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )
    hash_sha256: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        nullable=False,
    )
    nitidez: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )
    iluminacion: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )
    calidad_suficiente: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
    )

    estudio: Mapped["EstudioORM"] = relationship(
        "EstudioORM",
        back_populates="imagenes",
    )
    hallazgos: Mapped[list["HallazgoORM"]] = relationship(
        "HallazgoORM",
        back_populates="imagen",
        cascade="all, delete-orphan",
        lazy="select",
    )