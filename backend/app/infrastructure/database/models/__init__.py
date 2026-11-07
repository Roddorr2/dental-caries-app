"""
models/__init__.py
==================
Barrel export para modelos ORM de SQLAlchemy.
Facilita imports limpios y garantiza el registro de todas las entidades
y relaciones cruzadas en el mapper declarativo.
"""

from app.infrastructure.database.models.paciente_model import PacienteORM
from app.infrastructure.database.models.diagnostico_model import (
    DiagnosticoORM,
    HallazgoORM,
    ModeloMLORM,
    OdontologoORM,
)
from app.infrastructure.database.models.estudio_model import (
    EstudioORM,
    ImagenIntraoralORM,
)
from app.infrastructure.database.models.inferencia_model import InferenciaIAORM
from app.infrastructure.database.models.auditoria_model import (
    AuditoriaDiagnosticoORM,
    AuditoriaEstudioORM,
)
from app.infrastructure.database.models.read_models.rm_cola import RMColaRevisionORM
from app.infrastructure.database.models.read_models.rm_estadisticas import RMEstadisticasModeloORM
from app.infrastructure.database.models.read_models.rm_historial import RMHistorialPacienteORM

__all__ = [
    "PacienteORM",
    "OdontologoORM",
    "ModeloMLORM",
    "DiagnosticoORM",
    "HallazgoORM",
    "EstudioORM",
    "ImagenIntraoralORM",
    "InferenciaIAORM",
    "AuditoriaDiagnosticoORM",
    "AuditoriaEstudioORM",
    "RMColaRevisionORM",
    "RMEstadisticasModeloORM",
    "RMHistorialPacienteORM",
]
