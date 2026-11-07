"""
diagnostico_model.py
====================
ORM models para las tablas:
- diagnosticos
- hallazgos
- odontologos
- modelos_ml
"""

from datetime import datetime
from uuid import UUID
import uuid

from sqlalchemy import String, DateTime, Float, Boolean, ForeignKey, Integer, Enum as SAEnum, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from app.infrastructure.database.base import Base

class OdontologoORM(Base):
    """
    Tabla: odontologos

    Columns
    -------
    id : UUID (PK)
    nombres : VARCHAR(100)
    apellidos : VARCHAR(100)
    numero_colegiatura : VARCHAR(20) — único
    autorizado_validar : BOOLEAN
    created_at : TIMESTAMP WITH TIME ZONE
    """

    __tablename__ = "odontologos"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    nombres: Mapped[str] = mapped_column(String(100), nullable=False)
    apellidos: Mapped[str] = mapped_column(String(100), nullable=False)
    numero_colegiatura: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        nullable=False,
    )
    autorizado_validar: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
    )


    diagnosticos: Mapped[list["DiagnosticoORM"]] = relationship(
        "DiagnosticoORM",
        back_populates="odontologo",
        lazy="select",
    )


class ModeloMLORM(Base):
    """
    Tabla: modelos_ml

    Registro de modelos ML disponibles para producción.
    Permite trazabilidad clínica: qué modelo generó cada diagnóstico.

    Columns
    -------
    id : UUID (PK)
    nombre : VARCHAR(100)
    version : VARCHAR(20)
    tipo : ENUM — YOLO | SVM | RANDOM_FOREST | MOBILENET | EFFICIENTNET
    f1_score : FLOAT
    precision_score : FLOAT
    recall_score : FLOAT
    ruta_archivo : VARCHAR(500)
    aprobado_produccion : BOOLEAN
    created_at : TIMESTAMP WITH TIME ZONE
    """

    __tablename__ = "modelos_ml"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    version: Mapped[str] = mapped_column(String(20), nullable=False)
    tipo: Mapped[str] = mapped_column(
        SAEnum("YOLO", "SVM", "RANDOM_FOREST", "MOBILENET", "EFFICIENTNET", name="tipo_modelo_enum",),
        nullable=False,
    )
    f1_score: Mapped[float] = mapped_column(Float, nullable=False)
    precision_score: Mapped[float] = mapped_column(Float, nullable=False)
    recall_score: Mapped[float] = mapped_column(Float, nullable=False)
    ruta_archivo: Mapped[str] = mapped_column(String(500), nullable=False)
    aprobado_produccion: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
    )


    diagnosticos: Mapped[list["DiagnosticoORM"]] = relationship(
        "DiagnosticoORM",
        back_populates="modelo_ml",
        lazy="select",
    )
    inferencias: Mapped[list["InferenciaIAORM"]] = relationship(
        "InferenciaIAORM",
        back_populates="modelo_ml",
        lazy="select",
    )


class DiagnosticoORM(Base):
    """
    Tabla: diagnosticos

    Aggregate Root del BC3: Diagnóstico Asistido por IA.

    Columns
    -------
    id : UUID (PK)
    estudio_id : UUID (FK → estudios_imagenologicos)
    paciente_id : UUID — redundante, justificado por CQRS
    inferencia_id : UUID (FK → inferencias_ia, nullable)
    modelo_ml_id : UUID (FK → modelos_ml)
    odontologo_id : UUID (FK → odontologos, nullable)
    estado : ENUM
    confianza_global : FLOAT
    categoria_confianza : ENUM
    tiempo_inferencia_ms : FLOAT (nullable)
    fecha_generacion : TIMESTAMP WITH TIME ZONE
    fecha_validacion : TIMESTAMP WITH TIME ZONE (nullable)
    notas_validacion : TEXT (nullable)
    motivo_rechazo : TEXT (nullable)
    created_at : TIMESTAMP WITH TIME ZONE
    updated_at : TIMESTAMP WITH TIME ZONE
    """

    __tablename__ = "diagnosticos"

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
    paciente_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        nullable=False,
        index=True,
    )
    inferencia_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("inferencias_ia.id", ondelete="SET NULL"),
        nullable=True,
    )
    modelo_ml_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("modelos_ml.id", ondelete="RESTRICT"),
        nullable=False,
    )
    odontologo_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("odontologos.id", ondelete="SET NULL"),
        nullable=True,
    )
    estado: Mapped[str] = mapped_column(
        SAEnum(
            "SUGERIDO_IA", "EN_REVISION", "VALIDADO", "RECHAZADO",
            name="estado_diagnostico_enum",
        ),
        nullable=False,
        default="SUGERIDO_IA",
        index=True,
    )
    confianza_global: Mapped[float] = mapped_column(Float, nullable=False)
    categoria_confianza: Mapped[str] = mapped_column(
        SAEnum("BAJA", "MEDIA", "ALTA", name="categoria_confianza_enum"),
        nullable=False,
    )
    tiempo_inferencia_ms: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )
    fecha_generacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    fecha_validacion: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    notas_validacion: Mapped[str | None] = mapped_column(Text, nullable=True)
    motivo_rechazo: Mapped[str | None] = mapped_column(Text, nullable=True)
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


    estudio: Mapped["EstudioORM"] = relationship(
        "EstudioORM",
        back_populates="diagnosticos",
    )
    modelo_ml: Mapped["ModeloMLORM"] = relationship(
        "ModeloMLORM",
        back_populates="diagnosticos",
    )
    odontologo: Mapped["OdontologoORM | None"] = relationship(
        "OdontologoORM",
        back_populates="diagnosticos",
    )
    hallazgos: Mapped[list["HallazgoORM"]] = relationship(
        "HallazgoORM",
        back_populates="diagnostico",
        cascade="all, delete-orphan",
        lazy="select",
    )


class HallazgoORM(Base):
    """
    Tabla: hallazgos

    Una fila = una patología detectada por el modelo en una imagen.

    Columns
    -------
    id : UUID (PK)
    diagnostico_id : UUID (FK → diagnosticos)
    imagen_id : UUID (FK → imagenes_intraorales)
    tipo_patologia : ENUM
    severidad : ENUM
    confianza : FLOAT
    diente_numero : INTEGER (nullable) — notación FDI 11-48
    cuadrante : INTEGER (nullable)
    bbox_x : FLOAT (nullable)
    bbox_y : FLOAT (nullable)
    bbox_width : FLOAT (nullable)
    bbox_height : FLOAT (nullable)
    descripcion_clinica : TEXT (nullable)
    created_at : TIMESTAMP WITH TIME ZONE
    """

    __tablename__ = "hallazgos"

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
    imagen_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("imagenes_intraorales.id", ondelete="CASCADE"),
        nullable=False,
    )
    tipo_patologia: Mapped[str] = mapped_column(
        SAEnum(
            "CARIES", "FRACTURA", "CALCULO_DENTAL",
            name="tipo_patologia_enum",
        ),
        nullable=False,
    )
    severidad: Mapped[str] = mapped_column(
        SAEnum("LEVE", "MODERADA", "SEVERA", name="severidad_enum"),
        nullable=False,
    )
    confianza: Mapped[float] = mapped_column(Float, nullable=False)
    diente_numero: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cuadrante: Mapped[int | None] = mapped_column(Integer, nullable=True)
    bbox_x: Mapped[float | None] = mapped_column(Float, nullable=True)
    bbox_y: Mapped[float | None] = mapped_column(Float, nullable=True)
    bbox_width: Mapped[float | None] = mapped_column(Float, nullable=True)
    bbox_height: Mapped[float | None] = mapped_column(Float, nullable=True)
    descripcion_clinica: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
    )


    diagnostico: Mapped["DiagnosticoORM"] = relationship(
        "DiagnosticoORM",
        back_populates="hallazgos",
    )
    imagen: Mapped["ImagenIntraoralORM"] = relationship(
        "ImagenIntraoralORM",
        back_populates="hallazgos",
    )