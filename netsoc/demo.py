"""Dados de DEMONSTRAÇÃO — uma rede de laboratório fictícia.

Serve para quem abre o projeto ver o painel funcionando sem varrer nenhuma rede. Tudo aqui é
inventado, e a interface mostra uma faixa "modo demonstração" enquanto estes dados estão
carregados. As detecções, porém, são geradas pelas MESMAS regras usadas com dados reais.
"""

import random
from datetime import datetime, timedelta

from . import deteccoes
from .armazenamento import Armazenamento
from .servicos import classificar_dispositivo, servico

REDE = "10.10.20.0/24"

_REDE_ANTES = [
    ("10.10.20.1", "gw-lab.local", [53, 80, 443]),
    ("10.10.20.5", "srv-arquivos", [22, 139, 445]),
    ("10.10.20.10", "srv-web", [22, 80, 443]),
    ("10.10.20.11", "srv-db", [22, 5432]),
    ("10.10.20.20", "impressora-rh", [80, 515, 631, 9100]),
    ("10.10.20.30", "cam-recepcao", [80, 554]),
    ("10.10.20.51", "pc-financeiro", [135, 139, 445, 3389]),
    ("10.10.20.52", "pc-recepcao", [135, 139, 445]),
]
_MUDANCAS = {
    "10.10.20.11": [22, 5432, 6379],          # Redis aberto depois
    "10.10.20.52": [135, 139, 445, 5900],     # VNC instalado
}
_NOVOS = [("10.10.20.77", "", [21, 23, 80])]  # equipamento desconhecido com Telnet/FTP
_BANNERS = {(22, "10.10.20.10"): "SSH-2.0-OpenSSH_8.9p1 Ubuntu-3ubuntu0.6",
            (21, "10.10.20.77"): "220 (vsFTPd 3.0.3)",
            (80, "10.10.20.10"): "nginx/1.24.0"}


def _resultado(ativos, momento: datetime) -> dict:
    return {
        "alvo": REDE, "inicio": momento.isoformat(timespec="seconds"),
        "fim": (momento + timedelta(seconds=19)).isoformat(timespec="seconds"),
        "duracao_s": 18.7, "hosts_testados": 254,
        "ativos": [{
            "ip": ip, "hostname": nome, "latencia_ms": round(random.uniform(0.4, 6.0), 1),
            "tipo": classificar_dispositivo(set(portas)),
            "portas": [{"porta": p, "servico": servico(p).nome,
                        "banner": _BANNERS.get((p, ip), "")} for p in portas],
        } for ip, nome, portas in ativos],
    }


def _metricas(n: int, fim: datetime) -> list[dict]:
    saida, rx, tx = [], 9_000_000_000, 2_000_000_000
    for i in range(n):
        momento = fim - timedelta(seconds=5 * (n - i))
        pico = i in range(n - 14, n - 9)  # um surto recente para o modelo apontar
        cpu = random.gauss(88, 4) if pico else max(2.0, random.gauss(18, 6))
        ext = random.randint(55, 70) if pico else random.randint(8, 18)
        rx += random.randint(50_000, 900_000)
        tx += random.randint(20_000, 300_000) * (8 if pico else 1)
        saida.append({
            "momento": momento.isoformat(timespec="seconds"), "cpu": round(min(cpu, 100), 1),
            "memoria": round(random.gauss(58, 2), 1), "disco": 61.4,
            "conexoes": ext + random.randint(20, 35), "conexoes_externas": ext,
            "processos": random.randint(240, 252), "bytes_enviados": tx, "bytes_recebidos": rx,
            "pontuacao": round(random.uniform(-0.18, -0.08), 3) if pico
            else round(random.uniform(0.02, 0.14), 3),
        })
    return saida


def carregar(db: Armazenamento, semente: int = 7) -> dict:
    random.seed(semente)
    db.limpar()
    agora = datetime.now().replace(microsecond=0)

    antes = _resultado(_REDE_ANTES, agora - timedelta(days=1, hours=2))
    db.salvar_scan(antes)
    db.registrar_achados(deteccoes.avaliar_scan(antes))

    atual_ativos = [(ip, nome, _MUDANCAS.get(ip, portas)) for ip, nome, portas in _REDE_ANTES]
    atual_ativos = [a for a in atual_ativos if a[0] != "10.10.20.30"] + _NOVOS  # câmera sumiu
    atual = _resultado(atual_ativos, agora - timedelta(minutes=12))
    db.salvar_scan(atual)
    db.registrar_achados(deteccoes.avaliar_scan(atual, antes))

    metricas = _metricas(120, agora)
    for m in metricas:
        pontuacao = m.pop("pontuacao")
        db.salvar_metricas(m, pontuacao)

    db.registrar_achados(deteccoes.avaliar_conexoes([
        {"pid": 4812, "processo": "updater.exe", "local": "10.10.20.51:50211",
         "remoto_ip": "203.0.113.45", "remoto_porta": 4444, "status": "ESTABLISHED"},
    ]))
    db.registrar_achados(deteccoes.avaliar_processos([
        {"pid": 7731, "nome": "xmrig", "cpu": 97.5, "memoria": 4.1},
    ]))
    db.registrar_achados([deteccoes.Achado(
        regra="HOST-005", titulo="Comportamento anômalo do host", severidade="medio",
        alvo="pc-financeiro", descricao="O modelo Isolation Forest, treinado com 106 amostras "
        "desta máquina, marcou a leitura como fora do padrão: CPU acima do normal (+11.6σ), "
        "conexões externas acima do normal (+13.2σ).",
        evidencia={"pontuacao": -0.161, "desvios": {"cpu": 11.6, "conexoes_externas": 13.2}},
    )])

    db.definir("modo", "demo")
    db.definir("host_demo", "pc-financeiro (10.10.20.51)")
    return {"scans": 2, "ativos": len(atual["ativos"]), "metricas": len(metricas)}
