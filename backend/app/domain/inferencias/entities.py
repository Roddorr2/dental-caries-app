"""
entities.py
===========
Entidades del Bounded Context: Gestión de Inferencias IA.
"""

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

from app.domain.shared.aggregate_root import AggregateRoot
from app.domain.shared.domain_exception import DomainException
from app.domain.inferencias.value_objects import (
    EstadoInferencia,
    InferenciaId,
    TiempoInferencia,
    WorkerId,
)
from app.domain.inferencias.events import (
    InferenciaCompletada,
    InferenciaFallida,
    InferenciaIniciada,
)


class InferenciaIA(AggregateRoot):
    """
    Entidad con ciclo de vida propio del BC: Gestión de Inferencias IA.

    Registra el proceso técnico de ejecución ML de forma explícita.
    Permite debugging, reintentos y monitoreo del pipeline.

    No es el resultado clínico — ese es el Diagnóstico (BC3).
    Es el proceso técnico que lo genera.

    Attributes
    ----------
    id : UUID
        Identificador único de la inferencia.
    estudio_id : UUID
        ID del estudio imagenológico analizado.
    modelo_ml_id : UUID
        ID del modelo ML que ejecuta la inferencia.
    estado : EstadoInferencia
        Estado actual del proceso (PENDIENTE → EN_PROCESO → COMPLETADO | FALLIDO).
    worker_id : WorkerId | None
        Worker que tomó la tarea. None hasta que inicia.
    tiempo_inferencia : TiempoInferencia | None
        Tiempo de ejecución. None hasta completar.
    gpu_utilizada : str | None
        GPU usada durante la inferencia (opcional).
    error_mensaje : str | None
        Mensaje de error si estado es FALLIDO.
    created_at : datetime
        Timestamp UTC de creación.
    completed_at : datetime | None
        Timestamp UTC de finalización. None hasta completar o fallar.
    """

    def __init__(
        self,
        id: UUID,
        estudio_id: UUID,
        modelo_ml_id: UUID,
        estado: EstadoInferencia,
        created_at: datetime,
        worker_id: Optional[WorkerId] = None,
        tiempo_inferencia: Optional[TiempoInferencia] = None,
        gpu_utilizada: Optional[str] = None,
        error_mensaje: Optional[str] = None,
        completed_at: Optional[datetime] = None,
    ) -> None:
        super().__init__(id)
        self.estudio_id = estudio_id
        self.modelo_ml_id = modelo_ml_id
        self.estado = estado
        self.worker_id = worker_id
        self.tiempo_inferencia = tiempo_inferencia
        self.gpu_utilizada = gpu_utilizada
        self.error_mensaje = error_mensaje
        self.created_at = created_at
        self.completed_at = completed_at

    @staticmethod
    def crear(estudio_id: UUID, modelo_ml_id: UUID) -> "InferenciaIA":
        """
        Crea una nueva inferencia en estado PENDIENTE.

        Parameters
        ----------
        estudio_id : UUID
            ID del estudio a analizar.
        modelo_ml_id : UUID
            ID del modelo ML que ejecutará la inferencia.

        Returns
        -------
        InferenciaIA
            Nueva instancia con estado PENDIENTE.
        """
        return InferenciaIA(
            id=uuid4(),
            estudio_id=estudio_id,
            modelo_ml_id=modelo_ml_id,
            estado=EstadoInferencia(value="PENDIENTE"),
            created_at=datetime.now(tz=timezone.utc),
        )

    def iniciar(self, worker_id: WorkerId, gpu_utilizada: Optional[str] = None) -> None:
        """
        Marca la inferencia como EN_PROCESO.

        Parameters
        ----------
        worker_id : WorkerId
            Worker que toma la tarea.
        gpu_utilizada : str | None
            GPU usada durante la inferencia.

        Raises
        ------
        DomainException
            Si la inferencia no está en estado PENDIENTE.
        """
        if not self.estado.es_pendiente():
            raise DomainException(
                f"Solo inferencias PENDIENTES pueden iniciarse. "
                f"Estado actual: {self.estado.value}."
            )
        self.estado = EstadoInferencia(value="EN_PROCESO")
        self.worker_id = worker_id
        self.gpu_utilizada = gpu_utilizada
        self.add_event(
            InferenciaIniciada(
                inferencia_id=self.id,
                estudio_id=self.estudio_id,
                modelo_ml_id=self.modelo_ml_id,
                worker_id=worker_id.value,
            )
        )

    def completar(self, tiempo_inferencia: TiempoInferencia) -> None:
        """
        Marca la inferencia como COMPLETADO.

        Parameters
        ----------
        tiempo_inferencia : TiempoInferencia
            Tiempo total de ejecución en milisegundos.

        Raises
        ------
        DomainException
            Si la inferencia no está EN_PROCESO.
        """
        if not self.estado.es_en_proceso():
            raise DomainException(
                f"Solo inferencias EN_PROCESO pueden completarse. "
                f"Estado actual: {self.estado.value}."
            )
        self.estado = EstadoInferencia(value="COMPLETADO")
        self.tiempo_inferencia = tiempo_inferencia
        self.completed_at = datetime.now(tz=timezone.utc)
        self.add_event(
            InferenciaCompletada(
                inferencia_id=self.id,
                estudio_id=self.estudio_id,
                modelo_ml_id=self.modelo_ml_id,
                tiempo_ms=tiempo_inferencia.valor_ms,
            )
        )

    def fallar(self, error_mensaje: str) -> None:
        """
        Marca la inferencia como FALLIDO.

        Parameters
        ----------
        error_mensaje : str
            Descripción del error ocurrido.

        Raises
        ------
        DomainException
            Si la inferencia no está EN_PROCESO.
        DomainException
            Si el mensaje de error está vacío.
        """
        if not self.estado.es_en_proceso():
            raise DomainException(
                f"Solo inferencias EN_PROCESO pueden marcarse como fallidas. "
                f"Estado actual: {self.estado.value}."
            )
        if not error_mensaje or not error_mensaje.strip():
            raise DomainException("El mensaje de error no puede estar vacío.")

        self.estado = EstadoInferencia(value="FALLIDO")
        self.error_mensaje = error_mensaje
        self.completed_at = datetime.now(tz=timezone.utc)
        self.add_event(
            InferenciaFallida(
                inferencia_id=self.id,
                estudio_id=self.estudio_id,
                modelo_ml_id=self.modelo_ml_id,
                error_mensaje=error_mensaje,
            )
        )

    def puede_reintentarse(self) -> bool:
        """
        Verifica si la inferencia puede reintentarse.

        Returns
        -------
        bool
            True si el estado es FALLIDO.
        """
        return self.estado.es_fallido()