import time
from threading import Lock
from typing import Dict, Optional


class HistoricoSessao:
    """Acumula, em memória, quanto tempo a pessoa passou em cada faixa de risco.

    Pensado para uma demonstração ao vivo de uma sessão por vez. Para um
    cenário com múltiplos usuários simultâneos, troque por um armazenamento
    por sessão (ex.: um dicionário indexado por session_id, ou um banco).
    """

    def __init__(self) -> None:
        self._lock = Lock()
        self.tempos: Dict[str, float] = {}
        self.total_frames: int = 0
        self._ultimo_timestamp: Optional[float] = None
        self.timeline = []
        self.reset()

    def reset(self) -> None:
        with self._lock:
            self.tempos = {"adequado": 0.0, "atencao": 0.0, "critico": 0.0}
            self.total_frames = 0
            self._ultimo_timestamp = None
            self.timeline = []

    def registrar(self, risco: str) -> None:
        agora = time.time()
        with self._lock:
            if risco in self.tempos and self._ultimo_timestamp is not None:
                delta = agora - self._ultimo_timestamp
                # ignora intervalos muito grandes (pausas, reconexão da câmera etc.)
                if 0 < delta < 5:
                    self.tempos[risco] += delta
            self._ultimo_timestamp = agora
            self.total_frames += 1
            if risco in self.tempos:
                self.timeline.append(risco)

    def snapshot(self) -> Dict[str, float]:
        with self._lock:
            return {
                "tempo_adequado_s": round(self.tempos["adequado"], 1),
                "tempo_atencao_s": round(self.tempos["atencao"], 1),
                "tempo_critico_s": round(self.tempos["critico"], 1),
                "total_frames": self.total_frames,
                "timeline": self.timeline,
            }


# Instância única do processo. É simples e suficiente para a demonstração;
# basta reiniciar o servidor (ou chamar POST /historico/reiniciar) para zerar.
historico = HistoricoSessao()
