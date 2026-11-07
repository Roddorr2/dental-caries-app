"""
yolo_detector.py
================
Adaptador YOLOv8 — implementa IDetectorPatologias.

Traduce entre:
- El dominio: "detectar patologías en una imagen" → list[Hallazgo]
- Ultralytics: model.predict() → Results con boxes, confs, classes

El dominio nunca importa ultralytics.
El adaptador nunca ejecuta lógica de negocio.

Requiere:
    pip install ultralytics
"""

from pathlib import Path
from uuid import UUID, uuid4

from app.core.config.settings import settings
from app.domain.diagnosticos.interfaces import IDetectorPatologias
from app.domain.diagnosticos.value_objects import (
    Hallazgo,
    RegionDental,
    RegistroModeloML,
    Severidad,
    TipoPatologia,
)

_CONFIDENCE_THRESHOLD = settings.MODEL_CONFIDENCE_THRESHOLD

_CLASS_MAP: dict[int, str] = {
    0: "CARIES",  # caries_permanente (D)
    1: "CARIES",  # caries_decidua (d)
}

_DENTICION_DESC: dict[int, str] = {
    0: "Caries en dentición permanente (CPO-D)",
    1: "Caries en dentición decidua (ceo-d)",
}

_SEVERIDAD_ALTA    = 0.80
_SEVERIDAD_MEDIA   = 0.55


def _confianza_a_severidad(confianza: float) -> str:
    """
    Convierte la confianza del modelo en una categoría de severidad.

    Esta es una heurística de tesis — en producción real, la severidad
    debería derivarse de características clínicas adicionales.

    Parameters
    ----------
    confianza : float
        Confianza del modelo entre 0.0 y 1.0.

    Returns
    -------
    str
        'SEVERA' | 'MODERADA' | 'LEVE'
    """
    if confianza >= _SEVERIDAD_ALTA:
        return "SEVERA"
    elif confianza >= _SEVERIDAD_MEDIA:
        return "MODERADA"
    return "LEVE"


class YOLOv8Detector(IDetectorPatologias):
    """
    Adaptador YOLOv8 para detección de patologías dentales.

    Carga el modelo en memoria al instanciarse.
    Para producción, instanciar una sola vez y reutilizar
    (el modelo es thread-safe en lectura).

    Parameters
    ----------
    model_path : str | None
        Ruta al archivo .pt. Si None, usa settings.MODEL_PATH.
    modelo_ml_id : UUID | None
        ID del registro en modelos_ml. Usado para RegistroModeloML.
    f1_score : float
        F1-Score reportado en validación clínica.
    """

    def __init__(
        self,
        model_path: str | None = None,
        modelo_ml_id: UUID | None = None,
        f1_score: float = 0.86,
    ) -> None:
        from ultralytics import YOLO

        ruta = model_path or settings.MODEL_PATH
        p = Path(ruta)
        if not p.exists():
            # Intentar resolver relativamente si la aplicación se ejecuta desde la raíz o backend
            posible_raiz = Path(__file__).resolve().parents[4] / "ml" / "models" / "best.pt"
            if posible_raiz.exists():
                ruta = str(posible_raiz)
            elif (Path("..") / ruta).exists():
                ruta = str(Path("..") / ruta)
            else:
                raise FileNotFoundError(
                    f"Modelo YOLO no encontrado en '{ruta}'. "
                    "Verifica MODEL_PATH en tu archivo .env."
                )

        self._model = YOLO(ruta)
        self._model_path = ruta
        self._modelo_ml_id = modelo_ml_id or uuid4()
        self._f1_score = f1_score

    def detectar(self, ruta_imagen: str, imagen_id: UUID | None = None) -> list[Hallazgo]:
        """
        Detecta patologías en una imagen intraoral.

        Ejecuta model.predict() con el umbral de confianza configurado
        y mapea los resultados al VO Hallazgo del dominio.

        Parameters
        ----------
        ruta_imagen : str
            Ruta al archivo de imagen (.jpg, .png).
        imagen_id : UUID | None
            ID de la ImagenIntraoral asociada. Si None, genera uno nuevo.
            En producción siempre debe proveerse para trazabilidad.

        Returns
        -------
        list[Hallazgo]
            Lista de hallazgos detectados con confianza >= threshold.
            Lista vacía si no se detecta ninguna patología.
        """
        img_id = imagen_id or uuid4()

        # Resolver ruta de imagen si es relativa o pertenece a las muestras del sistema
        p = Path(ruta_imagen)
        if not p.exists():
            root_dir = Path(__file__).resolve().parents[4]
            clean_rel = ruta_imagen.lstrip("/\\")
            candidate = root_dir / "frontend" / "public" / clean_rel
            if candidate.exists():
                ruta_imagen = str(candidate)
            elif (root_dir / clean_rel).exists():
                ruta_imagen = str(root_dir / clean_rel)

        results = self._model.predict(
            source=ruta_imagen,
            conf=_CONFIDENCE_THRESHOLD,
            save=False,
            verbose=False,
        )

        hallazgos: list[Hallazgo] = []

        for result in results:
            if result.boxes is None or len(result.boxes) == 0:
                continue

            for box in result.boxes:
                cls_id   = int(box.cls.item())
                confianza = float(box.conf.item())
                xyxyn    = box.xyxyn[0].tolist()

                tipo_str = _CLASS_MAP.get(cls_id)
                if tipo_str is None:
                    continue

                x1, y1, x2, y2 = xyxyn
                bbox_x      = x1
                bbox_y      = y1
                bbox_width  = x2 - x1
                bbox_height = y2 - y1

                hallazgo = Hallazgo(
                    imagen_id=img_id,
                    tipo_patologia=TipoPatologia(tipo_str),
                    severidad=Severidad(_confianza_a_severidad(confianza)),
                    confianza=confianza,
                    region=RegionDental(
                        bbox_x=bbox_x,
                        bbox_y=bbox_y,
                        bbox_width=bbox_width,
                        bbox_height=bbox_height,
                    ),
                    descripcion_clinica=_DENTICION_DESC.get(cls_id),
                )
                hallazgos.append(hallazgo)

        return hallazgos

    def obtener_registro_modelo(self) -> RegistroModeloML:
        """
        Retorna la metadata del modelo YOLO cargado.

        Returns
        -------
        RegistroModeloML
            Metadata del modelo con ID, nombre, versión y f1_score.
        """
        return RegistroModeloML(
            modelo_ml_id=self._modelo_ml_id,
            nombre_modelo="YOLOv8n-dental",
            version="1.0",
            f1_score=self._f1_score,
        )
