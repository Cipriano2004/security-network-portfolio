"""Orquestra a coleta contínua do host, os scans de rede e o modelo de anomalia."""

import logging
import threading
import time
from datetime import datetime

from . import deteccoes, host
from .anomalia import DetectorAnomalia, explicar
from .armazenamento import Armazenamento
from .scanner import varrer

log = logging.getLogger("netsoc")


class Motor:
    def __init__(self, armazenamento: Armazenamento, intervalo: float = 5.0,
                 retreino_a_cada: int = 60):
        self.db = armazenamento
        self.intervalo = intervalo
        self.retreino_a_cada = retreino_a_cada
        self.detector = DetectorAnomalia()
        self._parar = threading.Event()
        self._thread: threading.Thread | None = None
        self._ciclos = 0
        self.scan_em_andamento: dict | None = None
        self._trava_scan = threading.Lock()

    # ------------------------------------------------------------ monitoramento contínuo
    def iniciar(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        host.coletar_metricas()  # primeira leitura de CPU do psutil é sempre 0
        self._parar.clear()
        self._thread = threading.Thread(target=self._loop, name="netsoc-monitor", daemon=True)
        self._thread.start()

    def parar(self) -> None:
        self._parar.set()

    def _loop(self) -> None:
        while not self._parar.wait(self.intervalo):
            try:
                self.ciclo()
            except Exception:  # noqa: BLE001 - o monitor não pode morrer por um erro pontual
                log.exception("erro no ciclo de monitoramento")

    def ciclo(self) -> dict:
        """Uma rodada: coleta métricas, avalia anomalia e regras de host."""
        self._ciclos += 1
        metricas = host.coletar_metricas()
        historico = self.db.ultimas_metricas(500)
        if self._ciclos % self.retreino_a_cada == 1 or not self.detector.pronto:
            vetores = [[m[c] for c in ("cpu", "memoria", "conexoes", "conexoes_externas",
                                       "processos")] for m in historico]
            self.detector.treinar(vetores)

        achados = []
        avaliacao = self.detector.avaliar(metricas.vetor())
        if avaliacao and avaliacao.anomala:
            achados.append(deteccoes.Achado(
                regra="HOST-005", titulo="Comportamento anômalo do host", severidade="medio",
                alvo=host.identidade()["hostname"],
                descricao="O modelo Isolation Forest, treinado com "
                f"{self.detector.amostras_treino} amostras desta máquina, marcou a leitura "
                f"como fora do padrão: {explicar(avaliacao.desvios)}.",
                evidencia={"pontuacao": avaliacao.pontuacao, "desvios": avaliacao.desvios,
                           "momento_amostra": metricas.momento},
            ))

        conexoes = [host.como_dict(c) for c in host.conexoes_estabelecidas()]
        escuta = [host.como_dict(p) for p in host.portas_escutando()]
        achados += deteccoes.avaliar_conexoes(conexoes)
        achados += deteccoes.avaliar_escuta(escuta)
        achados += deteccoes.avaliar_processos(host.top_processos(15))

        self.db.salvar_metricas(host.como_dict(metricas),
                                avaliacao.pontuacao if avaliacao else None)
        return {"metricas": metricas, "novos": self.db.registrar_achados(achados)}

    # ------------------------------------------------------------ scans
    def executar_scan(self, alvo: str, permitir_publico: bool = False) -> dict:
        """Roda o scan (bloqueante), salva e aplica as regras de rede."""
        with self._trava_scan:
            anterior = self.db.ultimo_scan(alvo=str(alvo))
            resultado = varrer(alvo, permitir_publico=permitir_publico).para_dict()
            scan_id = self.db.salvar_scan(resultado)
            if anterior is None:
                anterior = self.db.ultimo_scan(alvo=resultado["alvo"], antes_de=scan_id)
            achados = deteccoes.avaliar_scan(resultado, anterior)
            novos = self.db.registrar_achados(achados)
            return {"scan_id": scan_id, "resultado": resultado, "achados_novos": len(novos),
                    "achados": [a.para_dict() for a in achados]}

    def iniciar_scan(self, alvo: str) -> bool:
        """Dispara o scan em segundo plano (para a interface web). False se já houver um."""
        if self.scan_em_andamento and self.scan_em_andamento.get("estado") == "rodando":
            return False
        self.scan_em_andamento = {"alvo": alvo, "estado": "rodando",
                                  "inicio": datetime.now().isoformat(timespec="seconds")}

        def tarefa():
            inicio = time.perf_counter()
            try:
                saida = self.executar_scan(alvo)
                self.scan_em_andamento |= {
                    "estado": "concluido", "ativos": len(saida["resultado"]["ativos"]),
                    "achados_novos": saida["achados_novos"],
                    "duracao_s": round(time.perf_counter() - inicio, 1)}
            except Exception as erro:  # noqa: BLE001
                self.scan_em_andamento |= {"estado": "erro", "erro": str(erro)}

        threading.Thread(target=tarefa, name="netsoc-scan", daemon=True).start()
        return True
