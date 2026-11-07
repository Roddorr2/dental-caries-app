"""
solicitar_analisis.py
=====================
Handler para SolicitarAnalisisIACommand.
"""

from uuid import UUID

from app.application.commands.solicitar_analisis import SolicitarAnalisisIACommand
from app.domain.estudios.repository import IEstudioRepository
from app.domain.estudios.value_objects import EstudioId
from app.domain.inferencias.entities import InferenciaIA
from app.domain.inferencias.repository import IInferenciaRepository
from app.domain.shared.domain_exception import DomainException

class SolicitarAnalisisIAHandler:
    """
    Caso de uso: solicitar análisis IA sobre un estudio imagenológico.

    Orquesta:
    1. Verificar que el estudio existe y puede ser analizado
    2. Marcar estudio como EN_ANALISIS
    3. Crear InferenciaIA en estado PENDIENTE
    4. Persistir ambos agregados
    — El worker de inferencia toma la tarea desde la cola de pendientes.
    """

    def __init__(
        self,
        estudio_repo: IEstudioRepository,
        inferencia_repo: IInferenciaRepository,
    ) -> None:
        self._estudio_repo = estudio_repo
        self._inferencia_repo = inferencia_repo

    def handle(self, cmd: SolicitarAnalisisIACommand) -> UUID:
        """
        Returns
        -------
        UUID
            ID de la inferencia creada (en estado PENDIENTE).

        Raises
        ------
        DomainException
            Si el estudio no existe o no puede ser analizado.
        """
        estudio = self._estudio_repo.get_by_id(EstudioId(cmd.estudio_id))

        if estudio is None:
            raise DomainException(
                f"No existe el estudio con ID '{cmd.estudio_id}'."
            )
        if not estudio.puede_ser_analizado():
            raise DomainException(
                f"El estudio no puede iniciar análisis. "
                f"Estado: {estudio.estado_procesamiento.value}, "
                f"Imágenes: {len(estudio.imagenes)}."
            )

        estudio.iniciar_analisis()

        inferencia = InferenciaIA.crear(
            estudio_id=cmd.estudio_id,
            modelo_ml_id=cmd.modelo_ml_id,
        )

        self._estudio_repo.save(estudio)
        self._inferencia_repo.save(inferencia)

        return inferencia.id