"""
analisis_service.py
===================
Servicio de aplicación: Análisis Imagenológico.

Orquesta la coordinación entre BC2 (Estudios), BC3 (Diagnósticos)
y BC5 (Inferencias) para el flujo completo de análisis IA.

Este servicio existe porque el caso de uso cruza múltiples agregados
de distintos BCs — ningún handler individual puede hacerlo solo
sin violar el principio de responsabilidad única.

Flujo completo:
    1. SolicitarAnalisisIAHandler crea InferenciaIA (PENDIENTE) y marca
       estudio EN_ANALISIS.
    2. El worker toma la inferencia, ejecuta el modelo ML y llama a
       ServicioAnalisisImagenologico.completar_analisis().
    3. Este servicio crea el Diagnostico desde los resultados de la IA
       y persiste todo en una sola transacción.
"""

from uuid import UUID

from app.domain.diagnosticos.entities import Diagnostico
from app.domain.diagnosticos.repository import IDiagnosticoRepository
from app.domain.diagnosticos.value_objects import Hallazgo, RegistroModeloML
from app.domain.inferencias.entities import InferenciaIA
from app.domain.inferencias.repository import IInferenciaRepository
from app.domain.inferencias.value_objects import InferenciaId, TiempoInferencia, WorkerId
from app.domain.estudios.repository import IEstudioRepository
from app.domain.estudios.value_objects import EstudioId
from app.domain.shared.domain_exception import DomainException
from app.infrastructure.repositories.modelo_repo import SQLAlchemyModeloMLRepository

class ServicioAnalisisImagenologico:
    """
    Servicio de aplicación que coordina BC2, BC3 y BC5.

    Se inyecta en el worker de inferencia — no en los routers HTTP.
    Los routers solo usan handlers simples.
    """

    def __init__(
        self,
        estudio_repo: IEstudioRepository,
        inferencia_repo: IInferenciaRepository,
        diagnostico_repo: IDiagnosticoRepository,
        modelo_repo: SQLAlchemyModeloMLRepository,
    ) -> None:
        self._estudio_repo = estudio_repo
        self._inferencia_repo = inferencia_repo
        self._diagnostico_repo = diagnostico_repo
        self._modelo_repo = modelo_repo

    def iniciar_inferencia(
        self,
        inferencia_id: InferenciaId,
        worker_id: str,
        gpu_utilizada: str | None = None,
    ) -> None:
        """
        Marca una inferencia como EN_PROCESO.

        Llamado por el worker al tomar la tarea de la cola.

        Parameters
        ----------
        inferencia_id : InferenciaId
            ID de la inferencia a iniciar.
        worker_id : str
            Identificador del worker que toma la tarea.
        gpu_utilizada : str | None
            GPU usada. Opcional.

        Raises
        ------
        DomainException
            Si la inferencia no existe o no está en estado PENDIENTE.
        """
        inferencia = self._inferencia_repo.get_by_id(inferencia_id)
        if inferencia is None:
            raise DomainException(
                f"No existe la inferencia con ID '{inferencia_id.value}'."
            )

        inferencia.iniciar(
            worker_id=WorkerId(worker_id),
            gpu_utilizada=gpu_utilizada,
        )
        self._inferencia_repo.save(inferencia)

    def completar_analisis(
        self,
        inferencia_id: InferenciaId,
        hallazgos: list[Hallazgo],
        tiempo_ms: float,
    ) -> UUID:
        """
        Completa el análisis IA y crea el Diagnóstico resultante.

        Llamado por el worker tras ejecutar el modelo ML exitosamente.
        Persiste InferenciaIA (COMPLETADO) + Diagnostico (SUGERIDO_IA)
        en la misma transacción gestionada por el caller (worker).

        Parameters
        ----------
        inferencia_id : InferenciaId
            ID de la inferencia completada.
        hallazgos : list[Hallazgo]
            Patologías detectadas por el modelo ML.
        tiempo_ms : float
            Tiempo de ejecución del modelo en milisegundos.

        Returns
        -------
        UUID
            ID del diagnóstico creado.

        Raises
        ------
        DomainException
            Si la inferencia no existe, no está EN_PROCESO,
            o el modelo no está aprobado para producción.
        """
        inferencia = self._inferencia_repo.get_by_id(inferencia_id)
        if inferencia is None:
            raise DomainException(
                f"No existe la inferencia con ID '{inferencia_id.value}'."
            )

        modelo_vo = self._modelo_repo.get_by_id(inferencia.modelo_ml_id)
        if modelo_vo is None:
            raise DomainException(
                f"No existe el modelo ML con ID '{inferencia.modelo_ml_id}'."
            )

        estudio = self._estudio_repo.get_by_id(EstudioId(inferencia.estudio_id))
        if estudio is None:
            raise DomainException(
                f"No existe el estudio con ID '{inferencia.estudio_id}'."
            )

        inferencia.completar(TiempoInferencia(valor_ms=tiempo_ms))
        self._inferencia_repo.save(inferencia)

        diagnostico = Diagnostico.crear_desde_ia(
            estudio_id=inferencia.estudio_id,
            paciente_id=estudio.paciente_id,
            modelo=modelo_vo,
            hallazgos=hallazgos,
            inferencia_id=inferencia.id,
            tiempo_inferencia_ms=tiempo_ms,
        )
        self._diagnostico_repo.save(diagnostico)

        estudio.marcar_como_procesado()
        self._estudio_repo.save(estudio)

        return diagnostico.id

    def registrar_fallo(
        self,
        inferencia_id: InferenciaId,
        error_mensaje: str,
    ) -> None:
        """
        Registra un fallo en el pipeline de inferencia.

        Llamado por el worker cuando el modelo ML lanza una excepción.
        El estudio queda en EN_ANALISIS para reintento manual.

        Parameters
        ----------
        inferencia_id : InferenciaId
            ID de la inferencia fallida.
        error_mensaje : str
            Descripción del error ocurrido.

        Raises
        ------
        DomainException
            Si la inferencia no existe o no está EN_PROCESO.
        """
        inferencia = self._inferencia_repo.get_by_id(inferencia_id)
        if inferencia is None:
            raise DomainException(
                f"No existe la inferencia con ID '{inferencia_id.value}'."
            )

        inferencia.fallar(error_mensaje=error_mensaje)
        self._inferencia_repo.save(inferencia)