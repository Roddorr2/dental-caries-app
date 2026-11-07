"""
dependencies.py
===============
Inyección de dependencias FastAPI (Depends).

Centraliza las dependencias reutilizables en toda la API:
- Sesión de base de datos
- Repositorios
- Servicios de aplicación

Uso en un endpoint:
    from app.core.config.dependencies import get_paciente_service

    @router.post("/")
    def crear_paciente(
        cmd: RegistrarPacienteCommand,
        service: PacienteService = Depends(get_paciente_service),
    ):
        ...
"""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.infrastructure.database.connection import get_db

DBSession = Annotated[Session, Depends(get_db)]

def get_paciente_repository(db: DBSession):
    from app.infrastructure.repositories.paciente_repo import SQLAlchemyPacienteRepository
    return SQLAlchemyPacienteRepository(db)


def get_estudio_repository(db: DBSession):
    from app.infrastructure.repositories.estudio_repo import SQLAlchemyEstudioRepository
    return SQLAlchemyEstudioRepository(db)


def get_diagnostico_repository(db: DBSession):
    from app.infrastructure.repositories.diagnostico_repo import SQLAlchemyDiagnosticoRepository
    return SQLAlchemyDiagnosticoRepository(db)


def get_inferencia_repository(db: DBSession):
    from app.infrastructure.repositories.inferencia_repo import SQLAlchemyInferenciaRepository
    return SQLAlchemyInferenciaRepository(db)


def get_modelo_repository(db: DBSession):
    from app.infrastructure.repositories.modelo_repo import SQLAlchemyModeloMLRepository
    return SQLAlchemyModeloMLRepository(db)

def get_odontologo_repository(db: DBSession):
    from app.infrastructure.repositories. odontologo_repo import SQLAlchemyOdontologoRepository
    return SQLAlchemyOdontologoRepository(db)