"""
pacientes.py
============
Router FastAPI para el recurso Paciente.

Endpoints:
    POST /pacientes          → registrar nuevo paciente
    GET  /pacientes          → listar pacientes activos
    GET  /pacientes/{id}     → obtener paciente por ID
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.schemas.pacientes_schemas import PacienteCreate, PacienteResponse
from app.application.commands.registrar_paciente import RegistrarPacienteCommand
from app.application.handlers.registrar_paciente import RegistrarPacienteHandler
from app.core.config.dependencies import DBSession, get_paciente_repository
from app.domain.pacientes.value_objects import PacienteId
from app.domain.shared.domain_exception import DomainException
from app.infrastructure.repositories.paciente_repo import SQLAlchemyPacienteRepository

router = APIRouter(prefix="/pacientes", tags=["Pacientes"])


@router.post(
    "/",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar nuevo paciente",
)
def registrar_paciente(
    body: PacienteCreate,
    db: DBSession,
    repo: SQLAlchemyPacienteRepository = Depends(get_paciente_repository),
):
    """
    Registra un nuevo paciente en el sistema.

    Parameters
    ----------
    body : PacienteCreate
        Datos del paciente a registrar.

    Returns
    -------
    dict
        ID del paciente creado.

    Raises
    ------
    HTTPException 409
        Si el DNI ya está registrado.
    HTTPException 422
        Si algún dato no supera la validación de dominio.
    """
    try:
        handler = RegistrarPacienteHandler(repo)
        paciente_id = handler.handle(
            RegistrarPacienteCommand(
                dni=body.dni,
                nombres=body.nombres,
                apellidos=body.apellidos,
                fecha_nacimiento=body.fecha_nacimiento,
                sexo=body.sexo,
                telefono=body.telefono,
                email=str(body.email),
            )
        )
        db.commit()
        return {"id": str(paciente_id)}
    except DomainException as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))


@router.get(
    "/",
    response_model=list[PacienteResponse],
    summary="Listar pacientes activos",
)
def listar_pacientes(
    limit: int = 50,
    offset: int = 0,
    repo: SQLAlchemyPacienteRepository = Depends(get_paciente_repository),
):
    """
    Lista pacientes en estado ACTIVO ordenados por apellido.

    Parameters
    ----------
    limit : int
        Máximo de registros a retornar.
    offset : int
        Desplazamiento para paginación.

    Returns
    -------
    list[PacienteResponse]
        Lista de pacientes activos.
    """
    pacientes = repo.list_activos(limit=limit, offset=offset)
    return [
        PacienteResponse(
            id=p.id,
            dni=p.dni.value,
            nombres=p.nombre.nombres,
            apellidos=p.nombre.apellidos,
            fecha_nacimiento=p.fecha_nacimiento,
            sexo=p.sexo.value,
            telefono=p.telefono.value,
            email=p.email.value,
            estado=p.estado.value,
        )
        for p in pacientes
    ]


@router.get(
    "/{paciente_id}",
    response_model=PacienteResponse,
    summary="Obtener paciente por ID",
)
def obtener_paciente(
    paciente_id: UUID,
    repo: SQLAlchemyPacienteRepository = Depends(get_paciente_repository),
):
    """
    Obtiene un paciente por su ID.

    Parameters
    ----------
    paciente_id : UUID
        ID del paciente.

    Returns
    -------
    PacienteResponse
        Datos del paciente.

    Raises
    ------
    HTTPException 404
        Si el paciente no existe.
    """
    paciente = repo.get_by_id(PacienteId(paciente_id))
    if paciente is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Paciente con ID '{paciente_id}' no encontrado.",
        )
    return PacienteResponse(
        id=paciente.id,
        dni=paciente.dni.value,
        nombres=paciente.nombre.nombres,
        apellidos=paciente.nombre.apellidos,
        fecha_nacimiento=paciente.fecha_nacimiento,
        sexo=paciente.sexo.value,
        telefono=paciente.telefono.value,
        email=paciente.email.value,
        estado=paciente.estado.value,
    )