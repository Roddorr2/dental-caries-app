"""
estudios.py
===========
Router FastAPI para los recursos Estudio e Imagen.

Endpoints:
    GET  /estudios                          → listar estudios fotográficos
    POST /estudios                          → crear estudio
    GET  /estudios/{id}                     → obtener estudio con imágenes
    POST /estudios/{id}/imagenes            → agregar imagen
    POST /estudios/{id}/analisis            → solicitar análisis IA (CDSS)
"""

from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from app.infrastructure.ml.worker import ejecutar_inferencia

from app.api.schemas.estudio_schemas import (
    EstudioCreate,
    EstudioListItemResponse,
    EstudioResponse,
    ImagenCreate,
    ImagenResponse,
)
from app.api.schemas.inferencia_schemas import InferenciaResponse, SolicitarAnalisisRequest
from app.application.commands.cargar_estudio import AgregarImagenCommand, CargarEstudioCommand
from app.application.commands.solicitar_analisis import SolicitarAnalisisIACommand
from app.application.handlers.cargar_estudio import AgregarImagenHandler, CargarEstudioHandler
from app.application.handlers.solicitar_analisis import SolicitarAnalisisIAHandler
from app.core.config.dependencies import (
    DBSession,
    get_estudio_repository,
    get_inferencia_repository,
    get_modelo_repository,
    get_paciente_repository,
)
from app.domain.estudios.value_objects import EstudioId
from app.domain.shared.domain_exception import DomainException
from app.infrastructure.database.models.diagnostico_model import ModeloMLORM
from app.infrastructure.database.models.estudio_model import EstudioORM, ImagenIntraoralORM
from app.infrastructure.database.models.paciente_model import PacienteORM
from app.infrastructure.repositories.estudio_repo import SQLAlchemyEstudioRepository
from app.infrastructure.repositories.inferencia_repo import SQLAlchemyInferenciaRepository
from app.infrastructure.repositories.modelo_repo import SQLAlchemyModeloMLRepository
from app.infrastructure.repositories.paciente_repo import SQLAlchemyPacienteRepository

router = APIRouter(prefix="/estudios", tags=["Estudios"])


@router.get(
    "/",
    response_model=list[EstudioListItemResponse],
    summary="Listar estudios fotográficos intraorales",
)
def listar_estudios(
    db: DBSession,
    paciente_id: UUID | None = None,
    estado: str | None = None,
):
    """
    Lista el repositorio de estudios fotográficos para el flujo clínico del odontólogo.
    """

    query = db.query(EstudioORM).join(PacienteORM, EstudioORM.paciente_id == PacienteORM.id)
    if paciente_id:
        query = query.filter(EstudioORM.paciente_id == paciente_id)
    if estado:
        query = query.filter(EstudioORM.estado_procesamiento == estado)

    rows = query.order_by(EstudioORM.created_at.desc()).all()

    items = []
    for row in rows:
        diagnostico_id = row.diagnosticos[0].id if row.diagnosticos else None
        items.append(
            EstudioListItemResponse(
                id=row.id,
                paciente_id=row.paciente_id,
                paciente_nombre=f"{row.paciente.nombres} {row.paciente.apellidos}" if row.paciente else None,
                paciente_dni=row.paciente.dni if row.paciente else None,
                tipo_examen=row.tipo_examen,
                estado_procesamiento=row.estado_procesamiento,
                total_imagenes=len(row.imagenes),
                diagnostico_id=diagnostico_id,
                created_at=row.created_at,
            )
        )
    return items


@router.post(
    "/",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Crear estudio imagenológico",
)
def crear_estudio(
    body: EstudioCreate,
    db: DBSession,
    estudio_repo: SQLAlchemyEstudioRepository = Depends(get_estudio_repository),
    paciente_repo: SQLAlchemyPacienteRepository = Depends(get_paciente_repository),
):
    """
    Crea un nuevo estudio imagenológico para un paciente.
    """
    try:
        handler = CargarEstudioHandler(estudio_repo, paciente_repo)
        estudio_id = handler.handle(
            CargarEstudioCommand(
                paciente_id=body.paciente_id,
                tipo_examen=body.tipo_examen,
                region_examinada=body.region_examinada,
                observaciones=body.observaciones,
            )
        )
        db.commit()
        return {"id": str(estudio_id)}
    except DomainException as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.get(
    "/{estudio_id}",
    response_model=EstudioResponse,
    summary="Obtener estudio por ID con fotografías",
)
def obtener_estudio(
    estudio_id: UUID,
    db: DBSession,
):
    """
    Obtiene un estudio por su ID, incluyendo sus imágenes intraorales asociadas.
    """
    estudio = db.query(EstudioORM).filter(EstudioORM.id == estudio_id).first()
    if estudio is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Estudio con ID '{estudio_id}' no encontrado.",
        )
    return EstudioResponse(
        id=estudio.id,
        paciente_id=estudio.paciente_id,
        tipo_examen=estudio.tipo_examen,
        estado_procesamiento=estudio.estado_procesamiento,
        imagenes=[
            ImagenResponse(
                id=img.id,
                tipo_vista=img.tipo_vista,
                formato=img.formato,
                nombre_archivo=img.ruta_almacenamiento.split("/")[-1],
                calidad_suficiente=img.calidad_suficiente,
                created_at=img.created_at,
            )
            for img in estudio.imagenes
        ],
        created_at=estudio.created_at,
    )


@router.post(
    "/{estudio_id}/imagenes",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Agregar imagen a un estudio",
)
def agregar_imagen(
    estudio_id: UUID,
    body: ImagenCreate,
    db: DBSession,
    repo: SQLAlchemyEstudioRepository = Depends(get_estudio_repository),
):
    """
    Agrega una imagen intraoral a un estudio existente.
    """
    try:
        handler = AgregarImagenHandler(repo)
        imagen_id = handler.handle(
            AgregarImagenCommand(
                estudio_id=estudio_id,
                tipo_vista=body.tipo_vista,
                formato=body.formato,
                ruta_almacenamiento=body.ruta_almacenamiento,
                nombre_archivo=body.nombre_archivo,
                hash_sha256=body.hash_sha256,
                calidad_suficiente=body.calidad_suficiente,
                nitidez=body.nitidez,
                iluminacion=body.iluminacion,
            )
        )
        db.commit()
        return {"id": str(imagen_id)}
    except DomainException as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.post(
    "/{estudio_id}/analisis",
    response_model=dict,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Solicitar análisis IA / CDSS",
)
def solicitar_analisis(
    estudio_id: UUID,
    db: DBSession,
    background_tasks: BackgroundTasks,
    body: SolicitarAnalisisRequest | None = None,
    estudio_repo: SQLAlchemyEstudioRepository = Depends(get_estudio_repository),
    inferencia_repo: SQLAlchemyInferenciaRepository = Depends(get_inferencia_repository),
    modelo_repo: SQLAlchemyModeloMLRepository = Depends(get_modelo_repository),
):
    """
    Solicita análisis CDSS sobre un estudio fotográfico intraoral.
    Si no se envía modelo_ml_id, el CDSS selecciona automáticamente el
    modelo detector oficial aprobado para producción (YOLOv8n / best.pt).
    """
    try:
        modelo_id = body.modelo_ml_id if (body and body.modelo_ml_id) else None
        if not modelo_id:
            aprobado = modelo_repo.get_aprobado_produccion("YOLO")
            if aprobado:
                modelo_id = aprobado.modelo_ml_id
            else:
                primer = db.query(ModeloMLORM).filter(ModeloMLORM.aprobado_produccion == True).first()
                if not primer:
                    primer = db.query(ModeloMLORM).first()
                if primer:
                    modelo_id = primer.id
                else:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="No hay ningún modelo CDSS disponible en el sistema.",
                    )

        handler = SolicitarAnalisisIAHandler(estudio_repo, inferencia_repo)
        inferencia_id = handler.handle(
            SolicitarAnalisisIACommand(
                estudio_id=estudio_id,
                modelo_ml_id=modelo_id,
            )
        )
        db.commit()
        background_tasks.add_task(ejecutar_inferencia, inferencia_id)
        return {"inferencia_id": str(inferencia_id), "modelo_ml_id": str(modelo_id)}
    except DomainException as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))