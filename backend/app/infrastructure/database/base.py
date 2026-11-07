"""
base.py
=======
Base declarativa SQLAlchemy.

Todos los ORM models heredan de esta Base.
Alembic la usa para generar migraciones automáticas.
"""

from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    """
    Base declarativa para todos los modelos ORM del proyecto.

    Uso:
        class PacienteORM(Base):
            __tablename__ = "pacientes"
            ...
    """
    pass