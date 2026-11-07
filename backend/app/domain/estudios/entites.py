"""
entities.py
===========
Entidades del Bounded Context: Adquisición Imagenológica
"""

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4
from wsgiref.util import setup_testing_defaults

from app.domain.shared.aggregate_root import AggregateRoot
from app.domain.shared.entity import Entity
from app.domain.shared.domain_exception import DomainException
from app.domain.estudios.value_objects import (
    EstudioId,
    CalidadImagen,
    FormatoImagen,
    RutaAlmacenamiento,
    EstadoProcesamiento,
    TipoExamen,
    TipoVista,
    HashSHA256,
    ImagenId
)
from app.domain.estudios.events import (
    AnalisisIASolicitado,
    EstudioCreado,
    EstudioProcesado,
    ImagenAgregada
)

MAXIMO_IMAGENES_POR_ESTUDIO = 10

class ImagenIntraoral(Entity):
    """
    Entidad hija del agregado EstudioImagenologico.

    Representa una imagen intraoral dentro de un estudio.
    No puede existir ni ser accedida fuera de su estudio.

    Attributes
    ----------
    id : UUID
        Identificador único de la imagen.
    estudio_id : UUID
        ID del estudio al que pertenece.
    tipo_vista : TipoVista
        Ángulo de la imagen.
    ruta_almacenamiento : RutaAlmacenamiento
        Ruta al archivo en storage.
    nombre_archivo : str
        Nombre del archivo.
    formato : FormatoImagen
        Formato del archivo (jpg, jpeg, png).
    calidad : CalidadImagen
        Métricas de calidad de la imagen.
    hash_sha256 : HashSHA256
        Hash del archivo para evitar duplicados.
    resolucion_ancho : int | None
        Ancho de la imagen en píxeles.
    resolucion_alto : int | None
        Alto de la imagen en píxeles.
    created_at : datetime
        Timestamp UTC de creación.
    """

    def __init__(
            self,
            id: UUID,
            estudio_id: UUID,
            tipo_vista: TipoVista,
            ruta_almacenamiento: RutaAlmacenamiento,
            nombre_archivo: str,
            formato: FormatoImagen,
            calidad: CalidadImagen,
            hash_sha256: HashSHA256,
            resolucion_ancho: Optional[int] = None,
            resolucion_alto: Optional[int] = None,
            created_at: Optional[datetime] = None) -> None:
        super().__init__(id)
        self.estudio_id = estudio_id
        self.tipo_vista = tipo_vista
        self.ruta_almacenamiento = ruta_almacenamiento
        self.nombre_archivo = nombre_archivo
        self.formato = formato
        self.calidad = calidad
        self.hash_sha256 = hash_sha256
        self.resolucion_ancho = resolucion_ancho
        self.resolucion_alto = resolucion_alto
        self.created_at = created_at or datetime.now(tz=timezone.utc)

    def tiene_calidad_suficiente(self) -> bool:
        """
        Verifica si la imagen tiene calidad suficiente para ser procesada.

        Returns
        -------
        bool
            True si calidad.suficiente es True.
        """
        return self.calidad.suficiente

class EstudioImagenologico(AggregateRoot):
    """
    Aggregate Root del BC: Adquisición Imagenológica.

    Gestiona el conjunto de imágenes de un estudio clínico
    y controla el estado de procesamiento.

    Attributes
    ----------
    id : UUID
        Identificador único del estudio.
    paciente_id : UUID
        ID del paciente al que pertenece el estudio.
    tipo_examen : TipoExamen
        Tipo de examen clínico.
    estado_procesamiento : EstadoProcesamiento
        Estado actual del estudio.
    imagenes : list[ImagenIntraoral]
        Imágenes asociadas al estudio. Máximo 10.
    region_examinada : str | None
        Región clínica examinada.
    observaciones : str | None
        Notas clínicas adicionales.
    created_at : datetime
        Timestamp UTC de creación.
    updated_at : datetime
        Timestamp UTC de última modificación.
    """

    def __init__(
            self,
            id: UUID,
            paciente_id: UUID,
            tipo_examen: TipoExamen,
            estado_procesamiento: EstadoProcesamiento,
            created_at: datetime,
            updated_at: datetime,
            imagenes: Optional[list] = None,
            region_examinada: Optional[str] = None,
            observaciones: Optional[str] = None
    ) -> None:
        super().__init__(id)
        self.paciente_id = paciente_id
        self.tipo_examen = tipo_examen
        self.estado_procesamiento = estado_procesamiento
        self.imagenes: list[ImagenIntraoral] = imagenes or []
        self.region_examinada = region_examinada
        self.observaciones = observaciones
        self.created_at = created_at
        self.updated_at = updated_at

    @staticmethod
    def crear(
            paciente_id: UUID,
            tipo_examen: TipoExamen,
            region_examinada: Optional[str] = None,
            observaciones: Optional[str] = None,
    ) -> "EstudioImagenologico":
        """
        Crea un nuevo estudio imagenológico para un paciente.

        Parameters
        ----------
        paciente_id : UUID
            ID del paciente que recibe el estudio.
        tipo_examen : TipoExamen
            Tipo de examen clínico a realizar.
        region_examinada : str | None
            Región clínica examinada.
        observaciones : str | None
            Notas clínicas adicionales.

        Returns
        -------
        EstudioImagenologico
            Nueva instancia con estado PENDIENTE y evento EstudioCreado emitido.
        """
        ahora = datetime.now(tz=timezone.utc)
        estudio = EstudioImagenologico(
            id=uuid4(),
            paciente_id=paciente_id,
            tipo_examen=tipo_examen,
            estado_procesamiento=EstadoProcesamiento(value="PENDIENTE"),
            region_examinada=region_examinada,
            observaciones=observaciones,
            created_at=ahora,
            updated_at=ahora,
        )
        estudio.add_event(
            EstudioCreado(
                estudio_id=estudio.id,
                paciente_id=paciente_id,
                tipo_examen=tipo_examen.value,
            )
        )
        return estudio

    def agregar_imagen(self, imagen: ImagenIntraoral) -> None:
        """
        Agrega una imagen al estudio.

        Parameters
        ----------
        imagen : ImagenIntraoral
            Imagen a agregar al estudio.

        Raises
        ------
        DomainException
            Si el estudio ya tiene 10 imágenes.
        DomainException
            Si la imagen no tiene calidad suficiente.
        DomainException
            Si el estudio no está en estado PENDIENTE.
        """
        if self.estado_procesamiento.es_en_analisis():
            raise DomainException("No se pueden agregar imágenes a un estudio en análisis.")
        if self.estado_procesamiento.es_procesado():
            raise DomainException("No se pueden agregar imágenes a un estudio ya procesado")
        if len(self.imagenes) >= MAXIMO_IMAGENES_POR_ESTUDIO:
            raise DomainException(f"El estudio ya tiene el máximo de {MAXIMO_IMAGENES_POR_ESTUDIO} imágenes")
        if not imagen.tiene_calidad_suficiente():
            raise DomainException(f"La imagen '{imagen.nombre_archivo}' no tiene calidad suficiente.")

        self.imagenes.append(imagen)
        self.updated_at = datetime.now(tz=timezone.utc)
        self.add_event(
            ImagenAgregada(
                estudio_id=self.id,
                imagen_id=imagen.id,
                tipo_vista=imagen.tipo_vista.value
            )
        )

    def puede_ser_analizado(self) -> bool:
        """
        Verifica si el estado puede solicitar análisis IA.

        Returns
        -------
        bool
            True si no está actualmente en análisis (PENDIENTE o PROCESADO)
            y tiene al menos una imagen.
        """
        return not self.estado_procesamiento.es_en_analisis() and len(self.imagenes) > 0

    def iniciar_analisis(self) -> None:
        """
        Marca el estudio como EN_ANALISIS

        Raises
        ------
        DomainException
            Si el estudio no puede ser analizado.
        """
        if not self.puede_ser_analizado():
            raise DomainException(
                f"El estudio no puede iniciar análisis. "
                f"Estado: {self.estado_procesamiento.value}, "
                f"Imágenes: {len(self.imagenes)}."
              )
        self.estado_procesamiento = EstadoProcesamiento(value="EN_ANALISIS")
        self.updated_at = datetime.now(tz=timezone.utc)
        self.add_event(
            AnalisisIASolicitado(
                estudio_id=self.id,
                paciente_id=self.paciente_id,
                total_imagenes=len(self.imagenes)
            )
        )

    def marcar_como_procesado(self) -> None:
        """
        Marca el estudio como PROCESADO.

        Raises
        ------
        DomainException
            Si el estudio no está EN_ANALISIS.
        """
        if not self.estado_procesamiento.es_en_analisis():
            raise DomainException(
                f"Solo estudios en EN_ANALISIS pueden marcarse como procesados."
                f"Estado actual: {self.estado_procesamiento.value}"
            )
        self.estado_procesamiento = EstadoProcesamiento(value="PROCESADO")
        self.updated_at = datetime.now(tz=timezone.utc)
        self.add_event(EstudioProcesado(estudio_id=self.id, paciente_id=self.paciente_id,))


