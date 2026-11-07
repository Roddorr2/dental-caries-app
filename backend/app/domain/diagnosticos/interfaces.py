"""
interfaces.py
=============
Interfaces (puertos) de ML del Bounded Context: Diagnóstico Asistido por IA.

El dominio define aquí el contrato.
La infraestructura lo implementa en infrastructure/ml/.
"""

from abc import ABC, abstractmethod

from app.domain.diagnosticos.value_objects import Hallazgo, RegistroModeloML

class IDetectorPatologias(ABC):
    """
    Puerto para detección de patologías en imágenes intraorales.

    Implementado por: YOLOv8Detector (infrastructure/ml/yolo_detector.py)

    El dominio habla de 'detectar patologías', no de 'ejecutar YOLOv8'.
    Esto permite cambiar el modelo sin tocar el dominio.
    """

    @abstractmethod
    def detectar(self, ruta_imagen: str) -> list[Hallazgo]:
        """
        Detecta patologías en una imagen intraoral.

        Parameters
        ----------
        ruta_imagen : str
            Ruta al archivo de imagen.

        Returns
        -------
        list[Hallazgo]
            Lista de hallazgos detectados con confianza >= 0.5.
        """
        ...

    @abstractmethod
    def obtener_registro_modelo(self) -> RegistroModeloML:
        """
        Retorna la metadata del modelo actual.

        Returns
        -------
        RegistroModeloML
            Registro con nombre, versión y métricas del modelo.
        """
        ...


class IClasificadorImagenes(ABC):
    """
    Puerto para clasificación de imágenes o regiones detectadas.

    Implementado por: SVMClassifier, RandomForestClassifier
    (infrastructure/ml/)

    Usado opcionalmente para clasificación sobre regiones
    detectadas por YOLO.
    """

    @abstractmethod
    def clasificar(self, ruta_imagen: str) -> list[Hallazgo]:
        """
        Clasifica patologías en una imagen o región.

        Parameters
        ----------
        ruta_imagen : str
            Ruta al archivo de imagen o región recortada.

        Returns
        -------
        list[Hallazgo]
            Lista de hallazgos clasificados.
        """
        ...

    @abstractmethod
    def obtener_registro_modelo(self) -> RegistroModeloML:
        """
        Retorna la metadata del modelo actual.

        Returns
        -------
        RegistroModeloML
            Registro con nombre, versión y métricas del modelo.
        """
        ...