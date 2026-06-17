"""
Lógica de análise ergonômica.

Recebe os keypoints no formato COCO (17 pontos, na ordem usada pelo
YOLO-pose) e calcula ângulos de articulações relevantes para postura,
classificando cada um em faixas de risco.

As faixas de ângulo abaixo são valores de referência inspirados em
métodos simplificados de avaliação postural (como o RULA), pensados
para o cenário de "pessoa sentada usando o computador". Ajustem esses
limites conforme os testes da equipe e citem a referência usada no
README.
"""

from typing import Dict, List, Tuple

import numpy as np

# Índices dos keypoints no formato COCO usado pelo YOLO-pose
NOSE = 0
L_EYE, R_EYE = 1, 2
L_EAR, R_EAR = 3, 4
L_SHOULDER, R_SHOULDER = 5, 6
L_ELBOW, R_ELBOW = 7, 8
L_WRIST, R_WRIST = 9, 10
L_HIP, R_HIP = 11, 12
L_KNEE, R_KNEE = 13, 14
L_ANKLE, R_ANKLE = 15, 16

# Cada faixa é uma lista de tuplas (limite_superior_em_graus, classificacao),
# avaliadas em ordem; o primeiro limite que o ângulo não excede é usado.
FAIXAS: Dict[str, List[Tuple[float, str]]] = {
    "tronco": [(20.0, "adequado"), (45.0, "atencao"), (float("inf"), "critico")],
    "pescoco": [(15.0, "adequado"), (30.0, "atencao"), (float("inf"), "critico")],
}

_PRIORIDADE = {"adequado": 0, "atencao": 1, "critico": 2}


def _classificar(valor: float, faixa: List[Tuple[float, str]]) -> str:
    for limite, classe in faixa:
        if valor <= limite:
            return classe
    return faixa[-1][1]


def _midpoint(p1: Tuple[float, float], p2: Tuple[float, float]) -> Tuple[float, float]:
    return ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)


def _angulo_com_vertical(vetor: Tuple[float, float]) -> float:
    """Ângulo (em graus) entre um vetor (dx, dy) e a vertical (0, -1).

    Como a origem da imagem fica no canto superior esquerdo, "para cima"
    é (0, -1). Um vetor alinhado com a vertical dá 0°; quanto mais
    inclinado, maior o ângulo.
    """
    v = np.array(vetor, dtype=float)
    vertical = np.array([0.0, -1.0])
    norma = np.linalg.norm(v)
    if norma == 0:
        return 0.0
    cos_theta = np.clip(np.dot(v, vertical) / norma, -1.0, 1.0)
    return float(np.degrees(np.arccos(cos_theta)))


def calcular_angulos(
    keypoints: List[Tuple[float, float, float]],
    confianca_minima: float = 0.3,
) -> Dict[str, Dict[str, object]]:
    """Calcula os ângulos de tronco e pescoço a partir dos keypoints de uma pessoa.

    keypoints: lista de 17 tuplas (x, y, confidence), na ordem COCO.
    Retorna um dicionário, ex.: {"tronco": {"valor": 12.4, "classificacao": "adequado"}, ...}
    Articulações cujos pontos não foram detectados com confiança suficiente
    são simplesmente omitidas do resultado.
    """

    def valido(i: int) -> bool:

        if i >= len(keypoints):
            return False

        return keypoints[i][2] >= confianca_minima

    angulos: Dict[str, Dict[str, object]] = {}

    if valido(L_SHOULDER) and valido(R_SHOULDER) and valido(L_HIP) and valido(R_HIP):
        ombro = _midpoint(keypoints[L_SHOULDER][:2], keypoints[R_SHOULDER][:2])
        quadril = _midpoint(keypoints[L_HIP][:2], keypoints[R_HIP][:2])
        vetor_tronco = (ombro[0] - quadril[0], ombro[1] - quadril[1])
        angulo_tronco = _angulo_com_vertical(vetor_tronco)
        angulos["tronco"] = {
            "valor": round(angulo_tronco, 1),
            "classificacao": _classificar(angulo_tronco, FAIXAS["tronco"]),
        }

        if valido(NOSE):
            nariz = keypoints[NOSE][:2]
            vetor_pescoco = (nariz[0] - ombro[0], nariz[1] - ombro[1])
            angulo_pescoco_abs = _angulo_com_vertical(vetor_pescoco)
            # ângulo do pescoço relativo à inclinação do tronco, para isolar
            # a flexão da cabeça da inclinação geral do corpo
            angulo_pescoco_relativo = abs(angulo_pescoco_abs - angulo_tronco)
            angulos["pescoco"] = {
                "valor": round(angulo_pescoco_relativo, 1),
                "classificacao": _classificar(angulo_pescoco_relativo, FAIXAS["pescoco"]),
            }

    # Extensão futura: cotovelo (L_SHOULDER-L_ELBOW-L_WRIST) e joelho
    # (L_HIP-L_KNEE-L_ANKLE) seguem o mesmo padrão de cálculo de ângulo
    # entre três pontos, caso a equipe queira cobrir mais articulações.

    return angulos


def risco_geral(angulos: Dict[str, Dict[str, object]]) -> str:
    """Define o risco geral como o pior (mais crítico) entre os ângulos calculados."""
    if not angulos:
        return "indeterminado"
    pior = max(angulos.values(), key=lambda a: _PRIORIDADE[a["classificacao"]])
    return pior["classificacao"]
