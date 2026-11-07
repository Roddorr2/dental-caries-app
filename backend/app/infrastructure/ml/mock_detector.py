"""
mock_detector.py
================
Adaptador Mock para detección de patologías — implementa IDetectorPatologias.

Permite desacoplar el desarrollo del Frontend (React) y la integración del
Backend (FastAPI) sin requerir modelos de Deep Learning previamente entrenados
ni hardware GPU/servidores activos.

Genera hallazgos realistas con bounding boxes normalizados (YOLO format),
grados de severidad clínica y confianzas sintéticas para validar tanto
el flujo normal como el flujo de segunda opinión prioritaria (confianza < 0.5).
"""

from uuid import UUID, uuid4
import random
from app.domain.diagnosticos.interfaces import IDetectorPatologias
from app.domain.diagnosticos.value_objects import (
    Hallazgo,
    RegionDental,
    RegistroModeloML,
    Severidad,
    TipoPatologia,
)


class MockYOLOv8Detector(IDetectorPatologias):
    """
    Detector simulado (Mock) para desacoplamiento e integración continua.

    Retorna detecciones verosímiles en imágenes intraorales sin sobrecarga computacional.
    Garantiza compatibilidad con las invariantes del dominio clínico (F1 >= 0.85).
    """

    def __init__(
        self,
        modelo_ml_id: UUID | None = None,
        simular_segunda_opinion: bool = False,
    ) -> None:
        self._modelo_ml_id = modelo_ml_id or uuid4()
        self._simular_segunda_opinion = simular_segunda_opinion

    def detectar(self, ruta_imagen: str, imagen_id: UUID | None = None) -> list[Hallazgo]:
        """
        Genera hallazgos sintéticos pero realistas para la imagen especificada.

        Parameters
        ----------
        ruta_imagen : str
            Ruta de la imagen de entrada.
        imagen_id : UUID | None
            ID de la imagen intraoral asociada.

        Returns
        -------
        list[Hallazgo]
            Lista de 1 a 3 hallazgos simulados con coordenadas normalizadas.
        """
        img_id = imagen_id or uuid4()

        # Si se solicita simular baja confianza para probar el flujo de segunda opinión
        if self._simular_segunda_opinion:
            confianza = 0.42
            severidad = "LEVE"
            diente_fdi = 36
            cuadrante = 3
            bbox = (0.45, 0.40, 0.12, 0.10)
            return [
                Hallazgo(
                    imagen_id=img_id,
                    tipo_patologia=TipoPatologia("CARIES"),
                    severidad=Severidad(severidad),
                    confianza=confianza,
                    region=RegionDental(
                        diente_numero=diente_fdi,
                        cuadrante=cuadrante,
                        bbox_x=bbox[0],
                        bbox_y=bbox[1],
                        bbox_width=bbox[2],
                        bbox_height=bbox[3],
                    ),
                    descripcion_clinica="Posible caries oclusal incipiente — requiere confirmación visual.",
                )
            ]

        # Casos realistas simulados: Caries oclusal e interproximal
        casos_simulados = [
            {
                "tipo": "CARIES",
                "severidad": "SEVERA",
                "confianza": 0.88,
                "diente": 46,
                "cuadrante": 4,
                "bbox": (0.35, 0.42, 0.18, 0.16),
                "desc": "Caries oclusal profunda en primer molar inferior derecho (FDI 46).",
            },
            {
                "tipo": "CARIES",
                "severidad": "MODERADA",
                "confianza": 0.72,
                "diente": 45,
                "cuadrante": 4,
                "bbox": (0.58, 0.38, 0.11, 0.12),
                "desc": "Lesión cariosa proximal en segundo premolar inferior derecho (FDI 45).",
            },
        ]

        hallazgos = []
        for caso in casos_simulados:
            hallazgos.append(
                Hallazgo(
                    imagen_id=img_id,
                    tipo_patologia=TipoPatologia(caso["tipo"]),
                    severidad=Severidad(caso["severidad"]),
                    confianza=caso["confianza"],
                    region=RegionDental(
                        diente_numero=caso["diente"],
                        cuadrante=caso["cuadrante"],
                        bbox_x=caso["bbox"][0],
                        bbox_y=caso["bbox"][1],
                        bbox_width=caso["bbox"][2],
                        bbox_height=caso["bbox"][3],
                    ),
                    descripcion_clinica=caso["desc"],
                )
            )

        return hallazgos

    def obtener_registro_modelo(self) -> RegistroModeloML:
        """
        Retorna la metadata del modelo simulado cumpliendo el umbral clínico F1 >= 0.85
        para permitir la aprobación y creación de diagnósticos en el Aggregate Root.
        """
        return RegistroModeloML(
            modelo_ml_id=self._modelo_ml_id,
            nombre_modelo="MockYOLOv8-DentalCaries",
            version="1.0-mock",
            f1_score=0.89,  # Cumple invariante clínica: f1_score >= 0.85
        )
