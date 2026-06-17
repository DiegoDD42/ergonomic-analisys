import base64

import cv2
import numpy as np
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app.history import historico
from app.model import run_inference
from app.posture import calcular_angulos, risco_geral
from app.schemas import HistoricoResponse, InferenciaResponse

app = FastAPI(title="API de Análise Ergonômica e Prevenção de Lesões")

# Em produção, troque "*" pela URL real do frontend (ex.: o domínio do deploy).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def _ler_imagem(arquivo: UploadFile) -> np.ndarray:
    conteudo = arquivo.file.read()
    array = np.frombuffer(conteudo, dtype=np.uint8)
    imagem = cv2.imdecode(array, cv2.IMREAD_COLOR)
    if imagem is None:
        raise HTTPException(status_code=400, detail="Não foi possível decodificar a imagem enviada.")
    return imagem


def _imagem_para_base64(imagem: np.ndarray) -> str:
    sucesso, buffer = cv2.imencode(".jpg", imagem)
    if not sucesso:
        raise HTTPException(status_code=500, detail="Falha ao codificar a imagem anotada.")
    return base64.b64encode(buffer).decode("utf-8")


@app.get("/health")
def health():
    """Endpoint simples para o frontend (ou você) checar se a API está no ar."""
    return {"status": "ok"}


@app.post("/infer", response_model=InferenciaResponse)
def infer(arquivo: UploadFile = File(...)):
    """Recebe uma imagem (frame de câmera ou upload) e retorna a análise postural.

    Entrada: multipart/form-data com o campo "arquivo" contendo a imagem.
    Saída: keypoints detectados, ângulos calculados, risco geral e a imagem
    anotada (esqueleto desenhado) em base64, pronta para exibir no frontend.
    """
    imagem = _ler_imagem(arquivo)
    resultado = run_inference(imagem)

    sem_pessoa = resultado.keypoints is None or len(resultado.keypoints.xy) == 0
    if sem_pessoa:
        return InferenciaResponse(pessoa_detectada=False)

    # Usa a primeira pessoa detectada no frame.
    # Se o cenário exigir múltiplas pessoas, iterar sobre resultado.keypoints.xy.
    xy = resultado.keypoints.xy[0].cpu().numpy()
    if resultado.keypoints.conf is not None:
        conf = resultado.keypoints.conf[0].cpu().numpy()
    else:
        conf = np.ones(len(xy))

    keypoints = [(float(x), float(y), float(c)) for (x, y), c in zip(xy, conf)]

    print("TOTAL KEYPOINTS:", len(keypoints))
    angulos = calcular_angulos(keypoints)
    risco = risco_geral(angulos)
    historico.registrar(risco)

    # .plot() desenha o esqueleto padrão do Ultralytics; pode ser substituído
    # por um desenho customizado (cores por faixa de risco, por exemplo).
    imagem_anotada = resultado.plot()
    imagem_b64 = _imagem_para_base64(imagem_anotada)

    return InferenciaResponse(
        pessoa_detectada=True,
        keypoints=[{"x": x, "y": y, "confidence": c} for x, y, c in keypoints],
        angulos=angulos,
        risco_geral=risco,
        imagem_anotada_base64=imagem_b64,
    )


@app.get("/historico", response_model=HistoricoResponse)
def obter_historico():
    """Retorna o tempo acumulado em cada faixa de risco na sessão atual, para o relatório."""
    return historico.snapshot()


@app.post("/historico/reiniciar")
def reiniciar_historico():
    """Zera o histórico acumulado (útil para começar uma nova demonstração do zero)."""
    historico.reset()
    return {"status": "reiniciado"}
