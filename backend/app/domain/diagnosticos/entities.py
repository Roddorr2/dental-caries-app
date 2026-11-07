"""
entities.py
===========
Entidades del Bounded Context: Diagnóstico Asistido por IA.
"""

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

from app.domain.shared.aggregate_root import AggregateRoot
from app.domain.shared.entity import Entity
from app.domain.shared.domain_exception import DomainException
from app.domain.diagnosticos.value_objects import (
    DiagnosticoId,
    EstadoDiagnostico,
    Hallazgo,
    NivelConfianza,
    RegistroModeloML,
)
from app.domain.diagnosticos.events import (
    DiagnosticoEnRevision,
    DiagnosticoRechazado,
    DiagnosticoSugeridoPorIA,
    DiagnosticoValidado,
    SegundaOpinionSolicitada,
)

class Odontologo(Entity):
    """
    Entidad de soporte — concepto clínico de dominio.

    No es un usuario del sistema (eso es infraestructura/auth).
    Es el odontólogo como actor clínico que valida diagnósticos.

    Attributes
    ----------
    id : UUID
        Identificador único del odontólogo.
    nombres : str
        Nombres del odontólogo.
    apellidos : str
        Apellidos del odontólogo.
    numero_colegiatura : str
        Número de colegiatura profesional.
    autorizado_validar : bool
        True si está habilitado para validar diagnósticos.
    """

    def __init__(
        self,
        id: UUID,
        nombres: str,
        apellidos: str,
        numero_colegiatura: str,
        autorizado_validar: bool = True,
    ) -> None:
        super().__init__(id)
        self.nombres = nombres
        self.apellidos = apellidos
        self.numero_colegiatura = numero_colegiatura
        self.autorizado_validar = autorizado_validar

    def nombre_completo(self) -> str:
        """Retorna nombres y apellidos concatenados."""
        return f"{self.nombres} {self.apellidos}"

    def esta_autorizado_para_validar(self) -> bool:
        """Retorna True si el odontólogo puede validar diagnósticos."""
        return self.autorizado_validar


class Diagnostico(AggregateRoot):
    """
    Aggregate Root CORE del sistema — BC: Diagnóstico Asistido por IA.

    Gestiona el ciclo de vida clínico de un diagnóstico:
    desde su generación por IA hasta su validación o rechazo humano.

    Attributes
    ----------
    id : UUID
        Identificador único del diagnóstico.
    estudio_id : UUID
        ID del estudio imagenológico analizado.
    paciente_id : UUID
        ID del paciente (redundante, justificado por CQRS).
    inferencia_id : UUID | None
        ID de la inferencia que generó este diagnóstico.
    modelo : RegistroModeloML
        Metadata del modelo ML usado.
    hallazgos : list[Hallazgo]
        Patologías detectadas. Al menos uno requerido.
    nivel_confianza : NivelConfianza
        Confianza global del diagnóstico.
    estado : EstadoDiagnostico
        Estado actual del ciclo de vida clínico.
    tiempo_inferencia_ms : float | None
        Tiempo de inferencia en ms.
    fecha_generacion : datetime
        Timestamp UTC de generación por IA.
    odontologo : Odontologo | None
        Odontólogo validador. None hasta la validación.
    fecha_validacion : datetime | None
        Timestamp UTC de validación.
    notas_validacion : str | None
        Notas del odontólogo al validar.
    motivo_rechazo : str | None
        Motivo del odontólogo al rechazar.
    created_at : datetime
        Timestamp UTC de creación.
    updated_at : datetime
        Timestamp UTC de última modificación.
    """

    def __init__(
        self,
        id: UUID,
        estudio_id: UUID,
        paciente_id: UUID,
        modelo: RegistroModeloML,
        hallazgos: list[Hallazgo],
        nivel_confianza: NivelConfianza,
        estado: EstadoDiagnostico,
        fecha_generacion: datetime,
        created_at: datetime,
        updated_at: datetime,
        inferencia_id: Optional[UUID] = None,
        tiempo_inferencia_ms: Optional[float] = None,
        odontologo: Optional[Odontologo] = None,
        fecha_validacion: Optional[datetime] = None,
        notas_validacion: Optional[str] = None,
        motivo_rechazo: Optional[str] = None,
    ) -> None:
        super().__init__(id)
        self.estudio_id = estudio_id
        self.paciente_id = paciente_id
        self.inferencia_id = inferencia_id
        self.modelo = modelo
        self.hallazgos = hallazgos
        self.nivel_confianza = nivel_confianza
        self.estado = estado
        self.tiempo_inferencia_ms = tiempo_inferencia_ms
        self.fecha_generacion = fecha_generacion
        self.odontologo = odontologo
        self.fecha_validacion = fecha_validacion
        self.notas_validacion = notas_validacion
        self.motivo_rechazo = motivo_rechazo
        self.created_at = created_at
        self.updated_at = updated_at

    @staticmethod
    def crear_desde_ia(
        estudio_id: UUID,
        paciente_id: UUID,
        modelo: RegistroModeloML,
        hallazgos: list[Hallazgo],
        inferencia_id: Optional[UUID] = None,
        tiempo_inferencia_ms: Optional[float] = None,
    ) -> "Diagnostico":
        """
        Crea un diagnóstico a partir del resultado de la IA.

        Parameters
        ----------
        estudio_id : UUID
            ID del estudio analizado.
        paciente_id : UUID
            ID del paciente.
        modelo : RegistroModeloML
            Metadata del modelo que generó el diagnóstico.
        hallazgos : list[Hallazgo]
            Patologías detectadas por el modelo.
        inferencia_id : UUID | None
            ID de la inferencia asociada.
        tiempo_inferencia_ms : float | None
            Tiempo de inferencia en milisegundos.

        Returns
        -------
        Diagnostico
            Nueva instancia con estado SUGERIDO_IA.

        Raises
        ------
        DomainException
            Si el modelo no está aprobado para producción.
        DomainException
            Si no hay hallazgos.
        """
        if not modelo.es_aprobado_para_produccion():
            raise DomainException(
                f"El modelo '{modelo.nombre_modelo}' v{modelo.version} "
                "no está aprobado para producción (F1-Score < 0.85)."
            )
        if not hallazgos:
            raise DomainException(
                "No se puede crear un diagnóstico sin hallazgos."
            )

        confianza_promedio = sum(h.confianza for h in hallazgos) / len(hallazgos)
        nivel_confianza = NivelConfianza.desde_valor(confianza_promedio)
        ahora = datetime.now(tz=timezone.utc)

        diagnostico = Diagnostico(
            id=uuid4(),
            estudio_id=estudio_id,
            paciente_id=paciente_id,
            inferencia_id=inferencia_id,
            modelo=modelo,
            hallazgos=hallazgos,
            nivel_confianza=nivel_confianza,
            estado=EstadoDiagnostico(value="SUGERIDO_IA"),
            tiempo_inferencia_ms=tiempo_inferencia_ms,
            fecha_generacion=ahora,
            created_at=ahora,
            updated_at=ahora,
        )
        diagnostico.add_event(
            DiagnosticoSugeridoPorIA(
                diagnostico_id=diagnostico.id,
                estudio_id=estudio_id,
                paciente_id=paciente_id,
                modelo_ml_id=modelo.modelo_ml_id,
                confianza_global=nivel_confianza.valor,
                categoria_confianza=nivel_confianza.categoria,
                total_hallazgos=len(hallazgos),
            )
        )
        if nivel_confianza.requiere_revision_prioritaria():
            diagnostico.add_event(
                SegundaOpinionSolicitada(
                    diagnostico_id=diagnostico.id,
                    paciente_id=paciente_id,
                    confianza_global=nivel_confianza.valor,
                )
            )
        return diagnostico

    def iniciar_revision(self, odontologo: Odontologo) -> None:
        """
        Marca el diagnóstico como EN_REVISION.

        Parameters
        ----------
        odontologo : Odontologo
            Odontólogo que inicia la revisión.

        Raises
        ------
        DomainException
            Si el diagnóstico no está en estado SUGERIDO_IA.
        DomainException
            Si el odontólogo no está autorizado.
        """
        if not self.estado.es_sugerido_ia():
            raise DomainException(
                f"Solo diagnósticos SUGERIDO_IA pueden iniciar revisión. "
                f"Estado actual: {self.estado.value}."
            )
        if not odontologo.esta_autorizado_para_validar():
            raise DomainException(
                f"El odontólogo '{odontologo.nombre_completo()}' "
                "no está autorizado para validar diagnósticos."
            )
        self.estado = EstadoDiagnostico(value="EN_REVISION")
        self.odontologo = odontologo
        self.updated_at = datetime.now(tz=timezone.utc)
        self.add_event(
            DiagnosticoEnRevision(
                diagnostico_id=self.id,
                odontologo_id=odontologo.id,
            )
        )

    def validar(self, odontologo: Odontologo, notas: str) -> None:
        """
        Valida el diagnóstico sugerido por IA.

        Parameters
        ----------
        odontologo : Odontologo
            Odontólogo que valida el diagnóstico.
        notas : str
            Notas clínicas de la validación.

        Raises
        ------
        DomainException
            Si el diagnóstico no puede validarse desde su estado actual.
        DomainException
            Si el odontólogo no está autorizado.
        DomainException
            Si las notas están vacías.
        """
        if not self.estado.puede_validarse():
            raise DomainException(
                f"El diagnóstico no puede validarse desde el estado '{self.estado.value}'."
            )
        if not odontologo.esta_autorizado_para_validar():
            raise DomainException(
                f"El odontólogo '{odontologo.nombre_completo()}' "
                "no está autorizado para validar diagnósticos."
            )
        if not notas or not notas.strip():
            raise DomainException("Las notas de validación no pueden estar vacías.")

        self.estado = EstadoDiagnostico(value="VALIDADO")
        self.odontologo = odontologo
        self.notas_validacion = notas
        self.fecha_validacion = datetime.now(tz=timezone.utc)
        self.updated_at = self.fecha_validacion
        self.add_event(
            DiagnosticoValidado(
                diagnostico_id=self.id,
                estudio_id=self.estudio_id,
                paciente_id=self.paciente_id,
                odontologo_id=odontologo.id,
            )
        )

    def rechazar(self, odontologo: Odontologo, motivo: str) -> None:
        """
        Rechaza el diagnóstico sugerido por IA.

        Parameters
        ----------
        odontologo : Odontologo
            Odontólogo que rechaza el diagnóstico.
        motivo : str
            Motivo del rechazo.

        Raises
        ------
        DomainException
            Si el diagnóstico no puede rechazarse desde su estado actual.
        DomainException
            Si el odontólogo no está autorizado.
        DomainException
            Si el motivo está vacío.
        """
        if not self.estado.puede_rechazarse():
            raise DomainException(
                f"El diagnóstico no puede rechazarse desde el estado '{self.estado.value}'."
            )
        if not odontologo.esta_autorizado_para_validar():
            raise DomainException(
                f"El odontólogo '{odontologo.nombre_completo()}' "
                "no está autorizado para validar diagnósticos."
            )
        if not motivo or not motivo.strip():
            raise DomainException("El motivo de rechazo no puede estar vacío.")

        self.estado = EstadoDiagnostico(value="RECHAZADO")
        self.odontologo = odontologo
        self.motivo_rechazo = motivo
        self.fecha_validacion = datetime.now(tz=timezone.utc)
        self.updated_at = self.fecha_validacion
        self.add_event(
            DiagnosticoRechazado(
                diagnostico_id=self.id,
                estudio_id=self.estudio_id,
                paciente_id=self.paciente_id,
                odontologo_id=odontologo.id,
                motivo=motivo,
            )
        )

    def requiere_segunda_opinion(self) -> bool:
        """
        Verifica si el diagnóstico requiere segunda opinión.

        Returns
        -------
        bool
            True si la confianza global es BAJA.
        """
        return self.nivel_confianza.requiere_revision_prioritaria()