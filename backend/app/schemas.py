from typing import Dict, List, Optional

from pydantic import BaseModel


class Keypoint(BaseModel):
    x: float
    y: float
    confidence: float


class AnguloInfo(BaseModel):
    valor: float
    classificacao: str  # "adequado" | "atencao" | "critico"


class InferenciaResponse(BaseModel):
    pessoa_detectada: bool
    keypoints: Optional[List[Keypoint]] = None
    angulos: Optional[Dict[str, AnguloInfo]] = None
    risco_geral: Optional[str] = None
    imagem_anotada_base64: Optional[str] = None


class HistoricoResponse(BaseModel):
    tempo_adequado_s: float
    tempo_atencao_s: float
    tempo_critico_s: float
    total_frames: int
    timeline: List[str]  # sequência de riscos detectados, para gráfico de barras ou linha
