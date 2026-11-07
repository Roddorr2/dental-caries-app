"""
cargar_estudio.py
=================
Handlers para CargarEstudioCommand y AgregarImagenCommand.
"""

from uuid import UUID

from app.application.commands.cargar_estudio import AgregarImagenCommand, CargarEstudioCommand
from app.domain.estudios.entites import EstudioImagenologico, ImagenIntraoral
from app.domain.estudios.repository import IEstudioRepository
from app.domain.estudios.value_objects import (
    CalidadImagen,
    FormatoImagen,
    HashSHA256,
    RutaAlmacenamiento,
    TipoExamen,
    TipoVista,
)
from app.domain.pacientes.repository import IPacienteRepository
from app.domain.pacientes.value_objects import PacienteId
from app.domain.shared.domain_exception import DomainException
from uuid import uuid4


class CargarEstudioHandler:
    """
    Caso de uso: crear un nuevo estudio imagenológico.

    Orquesta:
    1. Verificar que el paciente existe y está activo
    2. Crear EstudioImagenologico via factory method
    3. Persistir
    """

    def __init__(
        self,
        estudio_repo: IEstudioRepository,
        paciente_repo: IPacienteRepository,
    ) -> None:
        self._estudio_repo = estudio_repo
        self._paciente_repo = paciente_repo

    def handle(self, cmd: CargarEstudioCommand) -> UUID:
        """
        Returns
        -------
        UUID
            ID del estudio creado.

        Raises
        ------
        DomainException
            Si el paciente no existe o está inactivo.
        """
        paciente = self._paciente_repo.get_by_id(PacienteId(cmd.paciente_id))

        if paciente is None:
            raise DomainException(
                f"No existe el paciente con ID '{cmd.paciente_id}'."
            )
        if not paciente.puede_recibir_nuevo_estudio():
            raise DomainException(
                f"El paciente '{paciente.nombre.completo()}' está inactivo."
            )

        estudio = EstudioImagenologico.crear(
            paciente_id=cmd.paciente_id,
            tipo_examen=TipoExamen(cmd.tipo_examen),
            region_examinada=cmd.region_examinada,
            observaciones=cmd.observaciones,
        )

        self._estudio_repo.save(estudio)
        return estudio.id


class AgregarImagenHandler:
    """
    Caso de uso: agregar una imagen intraoral a un estudio existente.

    Orquesta:
    1. Verificar que el estudio existe
    2. Verificar que la imagen no está duplicada (hash)
    3. Construir ImagenIntraoral
    4. Agregar via método de dominio (controla reglas: máx 10, calidad)
    5. Persistir
    """

    def __init__(self, estudio_repo: IEstudioRepository) -> None:
        self._estudio_repo = estudio_repo

    def handle(self, cmd: AgregarImagenCommand) -> UUID:
        """
        Returns
        -------
        UUID
            ID de la imagen agregada.

        Raises
        ------
        DomainException
            Si el estudio no existe, la imagen está duplicada,
            o el dominio rechaza la operación.
        """
        from app.domain.estudios.value_objects import EstudioId

        estudio = self._estudio_repo.get_by_id(EstudioId(cmd.estudio_id))

        if estudio is None:
            raise DomainException(
                f"No existe el estudio con ID '{cmd.estudio_id}'."
            )
        if self._estudio_repo.exists_imagen_by_hash(cmd.hash_sha256):
            raise DomainException(
                f"La imagen '{cmd.nombre_archivo}' ya existe en el sistema (hash duplicado)."
            )

        imagen = ImagenIntraoral(
            id=uuid4(),
            estudio_id=cmd.estudio_id,
            tipo_vista=TipoVista(cmd.tipo_vista),
            ruta_almacenamiento=RutaAlmacenamiento(cmd.ruta_almacenamiento),
            nombre_archivo=cmd.nombre_archivo,
            formato=FormatoImagen(cmd.formato),
            calidad=CalidadImagen(
                suficiente=cmd.calidad_suficiente,
                nitidez=cmd.nitidez,
                iluminacion=cmd.iluminacion,
            ),
            hash_sha256=HashSHA256(cmd.hash_sha256),
        )

        estudio.agregar_imagen(imagen)
        self._estudio_repo.save(estudio)
        return imagen.id