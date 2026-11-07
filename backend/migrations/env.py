"""
env.py
======
Configuración del entorno Alembic.

Lee DATABASE_URL desde settings (variables de entorno)
e importa todos los ORM models para que Alembic pueda
detectar los cambios en el schema automáticamente.

Uso:
    # Generar migración automática tras cambiar un ORM model:
    alembic revision --autogenerate -m "descripcion_del_cambio"

    # Aplicar migraciones pendientes:
    alembic upgrade head

    # Ver historial de migraciones:
    alembic history

    # Revertir última migración:
    alembic downgrade -1
"""

from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context



import sys
from pathlib import Path

# Asegurar que el directorio raíz del backend esté en sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

from app.infrastructure.database.base import Base  # noqa: E402

from app.infrastructure.database.models.paciente_model import PacienteORM  
from app.infrastructure.database.models.estudio_model import (  
    EstudioORM,
    ImagenIntraoralORM,
)
from app.infrastructure.database.models.diagnostico_model import ( 
    DiagnosticoORM,
    HallazgoORM,
    OdontologoORM,
    ModeloMLORM,
)
from app.infrastructure.database.models.inferencia_model import InferenciaIAORM  
from app.infrastructure.database.models.auditoria_model import ( 
    AuditoriaDiagnosticoORM,
    AuditoriaEstudioORM,
)


from app.infrastructure.database.models.read_models.rm_historial import (
    RMHistorialPacienteORM,
)
from app.infrastructure.database.models.read_models.rm_cola import (
    RMColaRevisionORM,
)
from app.infrastructure.database.models.read_models.rm_estadisticas import (
    RMEstadisticasModeloORM,
)

target_metadata = Base.metadata


from app.core.config.settings import settings

config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

def run_migrations_offline() -> None:
    """
    Ejecuta migraciones en modo offline (sin conexión a la BD).

    Genera el SQL puro sin ejecutarlo — útil para revisar
    qué cambios se van a aplicar antes de hacerlo.

    Uso:
        alembic upgrade head --sql
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Ejecuta migraciones en modo online (conectado a la BD).

    Modo normal de uso — aplica los cambios directamente.

    Uso:
        alembic upgrade head
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()