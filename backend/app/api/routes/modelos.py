"""
modelos.py
==========
Router FastAPI para el recurso Modelo ML.

Endpoints:
    GET /modelos                    → listar modelos registrados
    GET /modelos/{id}/estadisticas  → estadísticas de producción
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.schemas.modelo_schemas import EstadisticasResponse, ModeloResponse
from app.application.queries.estadisticas_modelo import ObtenerEstadisticasModeloQuery
from app.application.services.diagnostico_service import ServicioDiagnostico
from app.core.config.dependencies import DBSession, get_modelo_repository
from app.infrastructure.repositories.modelo_repo import SQLAlchemyModeloMLRepository

router = APIRouter(prefix="/modelos", tags=["Modelos ML"])


@router.get(
    "/",
    response_model=list[ModeloResponse],
    summary="Listar modelos ML registrados",
)
def listar_modelos(
    repo: SQLAlchemyModeloMLRepository = Depends(get_modelo_repository),
):
    """
    Lista todos los modelos ML registrados en el sistema.

    Returns
    -------
    list[ModeloResponse]
        Lista de modelos con sus métricas de entrenamiento.
    """
    from app.infrastructure.database.models.diagnostico_model import ModeloMLORM
    from app.core.config.dependencies import get_db
    # Acceso directo al ORM para datos completos no cubiertos por RegistroModeloML
    rows = repo._db.query(ModeloMLORM).order_by(ModeloMLORM.tipo).all()
    return [
        ModeloResponse(
            id=r.id,
            nombre=r.nombre,
            version=r.version,
            tipo=r.tipo,
            f1_score=r.f1_score,
            precision_score=r.precision_score,
            recall_score=r.recall_score,
            aprobado_produccion=r.aprobado_produccion,
            created_at=r.created_at,
        )
        for r in rows
    ]


@router.get(
    "/{modelo_id}/estadisticas",
    response_model=list[EstadisticasResponse],
    summary="Estadísticas de producción de un modelo",
)
def estadisticas_modelo(
    modelo_id: UUID,
    db: DBSession,
):
    """
    Retorna estadísticas de rendimiento de un modelo en producción.

    Calculadas sobre diagnósticos reales validados por odontólogos.
    Lee desde rm_estadisticas_modelo (read model CQRS).

    Parameters
    ----------
    modelo_id : UUID
        ID del modelo. Retorna solo ese modelo.

    Returns
    -------
    list[EstadisticasResponse]
        Estadísticas del modelo.
    """
    servicio = ServicioDiagnostico(db)
    resultados = servicio.obtener_estadisticas_modelo(
        ObtenerEstadisticasModeloQuery(modelo_ml_id=modelo_id)
    )
    return [EstadisticasResponse(**r) for r in resultados]