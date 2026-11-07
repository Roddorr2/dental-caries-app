"""
rf_classifier.py
================
Adaptador Random Forest — implementa IClasificadorImagenes.

Clasificador de comparación para la tesis, junto con SVM.
Misma pipeline de características (HOG + LBP) que SVMClassifier
para que la comparación sea justa.

Reutiliza _extraer_caracteristicas de svm_classifier para evitar
duplicación de lógica de extracción de features.

Requiere:
    pip install scikit-learn scikit-image opencv-python joblib
"""

from pathlib import Path
from uuid import UUID, uuid4

from app.domain.diagnosticos.interfaces import IClasificadorImagenes
from app.domain.diagnosticos.value_objects import (
    Hallazgo,
    RegionDental,
    RegistroModeloML,
    Severidad,
    TipoPatologia,
)
from app.infrastructure.ml.svm_classifier import _extraer_caracteristicas

_CLASS_MAP: dict[int, str] = {
    0: "CARIES",
}


class RandomForestClassifier(IClasificadorImagenes):
    """
    Clasificador Random Forest para comparación con YOLO y SVM en la tesis.

    Misma interfaz que SVMClassifier — intercambiable sin cambiar el código
    que lo consume. El pipeline de features (HOG + LBP) es idéntico para
    que las métricas sean comparables.

    Parameters
    ----------
    model_path : str
        Ruta al archivo .pkl del modelo RF entrenado (joblib).
    modelo_ml_id : UUID | None
        ID del registro en modelos_ml.
    """

    def __init__(
        self,
        model_path: str,
        modelo_ml_id: UUID | None = None,
    ) -> None:
        import joblib

        if not Path(model_path).exists():
            raise FileNotFoundError(
                f"Modelo Random Forest no encontrado en '{model_path}'."
            )

        self._model = joblib.load(model_path)
        self._model_path = model_path
        self._modelo_ml_id = modelo_ml_id or uuid4()

    def clasificar(self, ruta_imagen: str, imagen_id: UUID | None = None) -> list[Hallazgo]:
        """
        Clasifica patologías en una imagen o región recortada.

        Random Forest retorna probabilidades por clase de forma nativa
        a través de predict_proba — no requiere parámetro adicional
        como SVM (probability=True).

        Parameters
        ----------
        ruta_imagen : str
            Ruta al archivo de imagen o región recortada.
        imagen_id : UUID | None
            ID de la imagen asociada.

        Returns
        -------
        list[Hallazgo]
            Lista con un único hallazgo si la confianza supera 0.5.
            Lista vacía si el modelo descarta la detección.
        """
        import numpy as np

        img_id = imagen_id or uuid4()
        features = _extraer_caracteristicas(ruta_imagen).reshape(1, -1)

        clase_predicha = int(self._model.predict(features)[0])
        tipo_str = _CLASS_MAP.get(clase_predicha)
        if tipo_str is None:
            return []

        probas = self._model.predict_proba(features)[0]
        confianza = float(np.max(probas))

        if confianza < 0.5:
            return []

        severidad = "SEVERA" if confianza >= 0.80 else ("MODERADA" if confianza >= 0.55 else "LEVE")

        return [
            Hallazgo(
                imagen_id=img_id,
                tipo_patologia=TipoPatologia(tipo_str),
                severidad=Severidad(severidad),
                confianza=confianza,
                region=RegionDental(),
            )
        ]

    def obtener_registro_modelo(self) -> RegistroModeloML:
        """
        Retorna la metadata del modelo Random Forest.

        Returns
        -------
        RegistroModeloML
            Metadata del modelo.
        """
        return RegistroModeloML(
            modelo_ml_id=self._modelo_ml_id,
            nombre_modelo="RandomForest-HOG-LBP-dental",
            version="1.0",
            f1_score=0.0,  # placeholder — sobreescribir con valor real de la BD
        )