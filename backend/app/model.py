import os

import numpy as np
from ultralytics import YOLO

# Caminho dos pesos treinados pela equipe (best.pt). Pode ser sobrescrito
# por variável de ambiente, útil para trocar de modelo sem alterar código.
MODEL_PATH = os.getenv("MODEL_PATH", os.path.join("models", "best.pt"))

_model = None


def get_model() -> YOLO:
    """Carrega o modelo uma única vez (lazy loading) e reutiliza a instância."""
    global _model
    if _model is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(
                f"Pesos do modelo não encontrados em '{MODEL_PATH}'. "
                "Treine o modelo (yolo task=pose mode=train ...) e copie o "
                "best.pt resultante para essa pasta, ou ajuste a variável "
                "de ambiente MODEL_PATH."
            )
        _model = YOLO(MODEL_PATH)
    return _model


def run_inference(imagem_bgr: np.ndarray):
    """Executa a inferência de pose em uma única imagem (formato BGR, como o OpenCV usa).

    Retorna o primeiro (e único) resultado do Ultralytics para essa imagem,
    que já contém boxes, keypoints e o método .plot() para desenhar o esqueleto.
    """
    modelo = get_model()
    resultados = modelo.predict(imagem_bgr, verbose=False)
    return resultados[0]
