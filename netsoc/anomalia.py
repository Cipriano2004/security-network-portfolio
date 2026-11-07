"""Detecção de anomalia nas métricas do host com Isolation Forest.

O modelo é treinado com as amostras reais coletadas desta máquina (linha de base) e avalia
cada nova amostra. Não há rótulos de "ataque" — então não existe "acurácia" a reportar;
o resultado é uma pontuação: quanto mais negativa, mais fora do padrão.
"""

from dataclasses import dataclass

import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

MINIMO_AMOSTRAS = 30
CARACTERISTICAS = ["cpu", "memoria", "conexoes", "conexoes_externas", "processos"]


@dataclass
class Avaliacao:
    pontuacao: float
    anomala: bool
    desvios: dict[str, float]  # z-score de cada característica, para explicar o alerta


class DetectorAnomalia:
    def __init__(self, contaminacao: float = 0.03, semente: int = 42):
        self.contaminacao = contaminacao
        self.semente = semente
        self.modelo: IsolationForest | None = None
        self.escala: StandardScaler | None = None
        self.amostras_treino = 0

    @property
    def pronto(self) -> bool:
        return self.modelo is not None

    def treinar(self, amostras: list[list[float]]) -> bool:
        if len(amostras) < MINIMO_AMOSTRAS:
            return False
        dados = np.asarray(amostras, dtype=float)
        self.escala = StandardScaler().fit(dados)
        self.modelo = IsolationForest(n_estimators=150, contamination=self.contaminacao,
                                      random_state=self.semente)
        self.modelo.fit(self.escala.transform(dados))
        self.amostras_treino = len(amostras)
        return True

    def avaliar(self, amostra: list[float]) -> Avaliacao | None:
        if not self.pronto:
            return None
        x = self.escala.transform(np.asarray([amostra], dtype=float))
        pontuacao = float(self.modelo.decision_function(x)[0])
        anomala = bool(self.modelo.predict(x)[0] == -1)
        desvios = {nome: round(float(z), 2) for nome, z in zip(CARACTERISTICAS, x[0], strict=True)}
        return Avaliacao(pontuacao=round(pontuacao, 4), anomala=anomala, desvios=desvios)


def explicar(desvios: dict[str, float], limite: float = 2.0) -> str:
    rotulos = {"cpu": "CPU", "memoria": "memória", "conexoes": "conexões",
               "conexoes_externas": "conexões externas", "processos": "processos"}
    fora = sorted(((abs(z), nome, z) for nome, z in desvios.items() if abs(z) >= limite),
                  reverse=True)
    if not fora:
        return "combinação incomum das métricas"
    return ", ".join(f"{rotulos[n]} {'acima' if z > 0 else 'abaixo'} do normal ({z:+.1f}σ)"
                     for _, n, z in fora)
