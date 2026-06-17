# Backend — API de Análise Ergonômica

## Instalação

```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Modelo treinado

Coloque o arquivo `best.pt` (resultado do treino do YOLO-pose) na pasta
`models/`. Por padrão a API procura em `models/best.pt`; para usar outro
caminho, defina a variável de ambiente `MODEL_PATH`:

```bash
export MODEL_PATH=/caminho/para/seu/best.pt
```

## Executar

```bash
uvicorn app.main:app --reload --port 8000
```

A API ficará disponível em `http://localhost:8000`. Documentação
interativa automática (Swagger) em `http://localhost:8000/docs`.

## Endpoints

| Rota | Método | Entrada | Saída |
|---|---|---|---|
| `/health` | GET | — | `{"status": "ok"}` |
| `/infer` | POST | `multipart/form-data`, campo `arquivo` (imagem) | keypoints, ângulos, risco geral, imagem anotada em base64 |
| `/historico` | GET | — | tempo acumulado (s) em cada faixa de risco na sessão |
| `/historico/reiniciar` | POST | — | zera o histórico acumulado |

## Próximos passos sugeridos

- Trocar o `.plot()` padrão do Ultralytics por um desenho customizado do
  esqueleto, com cores diferentes por faixa de risco.
- Adicionar cálculo de ângulo de cotovelo e joelho em `app/posture.py`,
  seguindo o mesmo padrão usado para tronco e pescoço.
- Se quiser processar vídeo direto (não só frame a frame vindo do
  frontend), criar um endpoint que recebe o arquivo de vídeo e itera
  sobre os frames com OpenCV, reaproveitando `run_inference`.
