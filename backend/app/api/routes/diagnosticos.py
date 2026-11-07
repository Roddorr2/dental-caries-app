"""
diagnosticos.py
===============
Router FastAPI para el recurso Diagnóstico.

Endpoints:
    GET  /diagnosticos/pendientes          → cola de revisión
    GET  /diagnosticos/{id}                → obtener diagnóstico
    POST /diagnosticos/{id}/validar        → validar diagnóstico
    POST /diagnosticos/{id}/rechazar       → rechazar diagnóstico
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.schemas.diagnostico_schemas import (
    DiagnosticoResponse,
    HallazgoResponse,
    RechazarRequest,
    ValidarRequest,
)
from app.application.commands.rechazar_diagnostico import RechazarDiagnosticoCommand
from app.application.commands.validar_diagnostico import ValidarDiagnosticoCommand
from app.application.handlers.rechazar_diagnostico import RechazarDiagnosticoHandler
from app.application.handlers.validar_diagnostico import ValidarDiagnosticoHandler
from app.application.queries.cola_revision import ConsultarColaRevisionQuery
from app.application.services.diagnostico_service import ServicioDiagnostico
from app.core.config.dependencies import (
    DBSession,
    get_diagnostico_repository,
    get_odontologo_repository,
)
from app.domain.diagnosticos.value_objects import DiagnosticoId
from app.domain.shared.domain_exception import DomainException
from app.infrastructure.repositories.diagnostico_repo import SQLAlchemyDiagnosticoRepository
from app.infrastructure.repositories.odontologo_repo import SQLAlchemyOdontologoRepository

router = APIRouter(prefix="/diagnosticos", tags=["Diagnósticos"])


@router.get(
    "/odontologos",
    response_model=list[dict],
    summary="Lista de odontólogos colegiados autorizados para validación",
)
def listar_odontologos_autorizados(
    odontologo_repo: SQLAlchemyOdontologoRepository = Depends(get_odontologo_repository),
):
    """
    Retorna la lista de odontólogos colegiados autorizados para la firma diagnóstica.
    No requiere autenticación: el odontólogo tratante se selecciona en el formulario de firma/rechazo.
    """
    odontologos = odontologo_repo.list_autorizados()
    return [
        {
            "id": str(o.id),
            "nombres": o.nombres,
            "apellidos": o.apellidos,
            "nombre_completo": o.nombre_completo(),
            "numero_colegiatura": o.numero_colegiatura,
            "autorizado_validar": o.autorizado_validar,
        }
        for o in odontologos
    ]


@router.get(
    "/pendientes",
    response_model=list[dict],
    summary="Cola de diagnósticos pendientes de revisión",
)
def cola_revision(
    solo_segunda_opinion: bool = False,
    limit: int = 20,
    offset: int = 0,
    db: DBSession = None,
):
    """
    Retorna los diagnósticos pendientes de revisión.

    Lee desde rm_cola_revision (read model CQRS) — sin JOINs.

    Parameters
    ----------
    solo_segunda_opinion : bool
        Si True, retorna solo casos con confianza BAJA.
    limit : int
        Máximo de registros.
    offset : int
        Desplazamiento para paginación.

    Returns
    -------
    list[dict]
        Lista de entradas de la cola.
    """
    servicio = ServicioDiagnostico(db)
    return servicio.consultar_cola_revision(
        ConsultarColaRevisionQuery(
            solo_segunda_opinion=solo_segunda_opinion,
            limit=limit,
            offset=offset,
        )
    )


@router.get(
    "/{diagnostico_id}",
    response_model=DiagnosticoResponse,
    summary="Obtener diagnóstico por ID",
)
def obtener_diagnostico(
    diagnostico_id: UUID,
    repo: SQLAlchemyDiagnosticoRepository = Depends(get_diagnostico_repository),
):
    """
    Obtiene un diagnóstico por su ID, incluyendo hallazgos.

    Parameters
    ----------
    diagnostico_id : UUID
        ID del diagnóstico.

    Returns
    -------
    DiagnosticoResponse
        Datos del diagnóstico con hallazgos.

    Raises
    ------
    HTTPException 404
        Si el diagnóstico no existe.
    """
    diagnostico = repo.get_by_id(DiagnosticoId(diagnostico_id))
    if diagnostico is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Diagnóstico con ID '{diagnostico_id}' no encontrado.",
        )
    return DiagnosticoResponse(
        id=diagnostico.id,
        estudio_id=diagnostico.estudio_id,
        paciente_id=diagnostico.paciente_id,
        estado=diagnostico.estado.value,
        confianza_global=diagnostico.nivel_confianza.valor,
        categoria_confianza=diagnostico.nivel_confianza.categoria,
        hallazgos=[
            HallazgoResponse(
                id=h.imagen_id,  # Hallazgo es VO — usa imagen_id como referencia
                imagen_id=h.imagen_id,
                tipo_patologia=h.tipo_patologia.value,
                severidad=h.severidad.value,
                confianza=h.confianza,
                diente_numero=h.region.diente_numero,
                cuadrante=h.region.cuadrante,
                bbox_x=h.region.bbox_x,
                bbox_y=h.region.bbox_y,
                bbox_width=h.region.bbox_width,
                bbox_height=h.region.bbox_height,
                descripcion_clinica=h.descripcion_clinica,
            )
            for h in diagnostico.hallazgos
        ],
        fecha_generacion=diagnostico.fecha_generacion,
        fecha_validacion=diagnostico.fecha_validacion,
        notas_validacion=diagnostico.notas_validacion,
        motivo_rechazo=diagnostico.motivo_rechazo,
    )


@router.post(
    "/{diagnostico_id}/validar",
    status_code=status.HTTP_200_OK,
    summary="Validar diagnóstico sugerido por IA",
)
def validar_diagnostico(
    diagnostico_id: UUID,
    body: ValidarRequest,
    db: DBSession,
    diagnostico_repo: SQLAlchemyDiagnosticoRepository = Depends(get_diagnostico_repository),
    odontologo_repo: SQLAlchemyOdontologoRepository = Depends(get_odontologo_repository),
):
    """
    El odontólogo valida un diagnóstico sugerido por IA.

    Parameters
    ----------
    diagnostico_id : UUID
        ID del diagnóstico a validar.
    body : ValidarRequest
        ID del odontólogo y notas de validación.

    Raises
    ------
    HTTPException 404
        Si el diagnóstico u odontólogo no existen.
    HTTPException 409
        Si el dominio rechaza la operación.
    """
    try:
        handler = ValidarDiagnosticoHandler(diagnostico_repo, odontologo_repo)
        handler.handle(
            ValidarDiagnosticoCommand(
                diagnostico_id=diagnostico_id,
                odontologo_id=body.odontologo_id,
                notas=body.notas,
            )
        )
        db.commit()
        return {"detail": "Diagnóstico validado correctamente."}
    except DomainException as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.post(
    "/{diagnostico_id}/rechazar",
    status_code=status.HTTP_200_OK,
    summary="Rechazar diagnóstico sugerido por IA",
)
def rechazar_diagnostico(
    diagnostico_id: UUID,
    body: RechazarRequest,
    db: DBSession,
    diagnostico_repo: SQLAlchemyDiagnosticoRepository = Depends(get_diagnostico_repository),
    odontologo_repo: SQLAlchemyOdontologoRepository = Depends(get_odontologo_repository),
):
    """
    El odontólogo rechaza un diagnóstico sugerido por IA.

    Parameters
    ----------
    diagnostico_id : UUID
        ID del diagnóstico a rechazar.
    body : RechazarRequest
        ID del odontólogo y motivo del rechazo.

    Raises
    ------
    HTTPException 404
        Si el diagnóstico u odontólogo no existen.
    HTTPException 409
        Si el dominio rechaza la operación.
    """
    try:
        handler = RechazarDiagnosticoHandler(diagnostico_repo, odontologo_repo)
        handler.handle(
            RechazarDiagnosticoCommand(
                diagnostico_id=diagnostico_id,
                odontologo_id=body.odontologo_id,
                motivo=body.motivo,
            )
        )
        db.commit()
        return {"detail": "Diagnóstico rechazado correctamente."}
    except DomainException as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))