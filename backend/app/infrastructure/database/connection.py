"""
connection.py
=============
Configuración de SQLAlchemy: engine, SessionLocal y dependencia get_db.

Usa las variables de entorno definidas en core/config/settings.py.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

from app.core.config.settings import Settings

engine = create_engine(
    Settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    echo=Settings.DEBUG,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

def get_db() -> Generator[Session, None, None]:
    """
    Dependencia FastAPI que provee una sesión de base de datos
    por request y garantiza su cierre al finalizar.

    Uso en un endpoint:
        @router.get("/")
        def endpoint(db: Session = Depends(get_db):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
