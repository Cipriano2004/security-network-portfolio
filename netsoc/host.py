"""Coleta de telemetria real do próprio computador (psutil)."""

import ipaddress
import platform
import socket
from dataclasses import asdict, dataclass
from datetime import datetime

import psutil


@dataclass
class Metricas:
    momento: str
    cpu: float
    memoria: float
    disco: float
    conexoes: int
    conexoes_externas: int
    processos: int
    bytes_enviados: int
    bytes_recebidos: int

    def vetor(self) -> list[float]:
        """Características usadas pelo modelo de anomalia."""
        return [self.cpu, self.memoria, float(self.conexoes), float(self.conexoes_externas),
                float(self.processos)]


@dataclass
class Conexao:
    pid: int | None
    processo: str
    local: str
    remoto_ip: str
    remoto_porta: int
    status: str


@dataclass
class PortaEscutando:
    pid: int | None
    processo: str
    endereco: str
    porta: int


def _nome_processo(pid: int | None, cache: dict) -> str:
    if not pid:
        return "desconhecido"
    if pid not in cache:
        try:
            cache[pid] = psutil.Process(pid).name()
        except (psutil.Error, OSError):
            cache[pid] = "desconhecido"
    return cache[pid]


def _externo(ip: str) -> bool:
    try:
        end = ipaddress.ip_address(ip)
    except ValueError:
        return False
    return not (end.is_private or end.is_loopback or end.is_link_local or end.is_multicast)


def _conexoes_inet() -> list:
    try:
        return psutil.net_connections(kind="inet")
    except (psutil.AccessDenied, PermissionError, OSError):
        return []


def coletar_metricas() -> Metricas:
    conexoes = [c for c in _conexoes_inet() if c.raddr]
    rede = psutil.net_io_counters()
    try:
        disco = psutil.disk_usage("/").percent
    except OSError:
        disco = 0.0
    return Metricas(
        momento=datetime.now().isoformat(timespec="seconds"),
        cpu=psutil.cpu_percent(interval=None),
        memoria=psutil.virtual_memory().percent,
        disco=disco,
        conexoes=len(conexoes),
        conexoes_externas=sum(1 for c in conexoes if _externo(c.raddr.ip)),
        processos=len(psutil.pids()),
        bytes_enviados=rede.bytes_sent,
        bytes_recebidos=rede.bytes_recv,
    )


def conexoes_estabelecidas() -> list[Conexao]:
    cache: dict = {}
    saida = []
    for c in _conexoes_inet():
        if not c.raddr or c.status != psutil.CONN_ESTABLISHED:
            continue
        saida.append(Conexao(pid=c.pid, processo=_nome_processo(c.pid, cache),
                             local=f"{c.laddr.ip}:{c.laddr.port}", remoto_ip=c.raddr.ip,
                             remoto_porta=c.raddr.port, status=c.status))
    return saida


def portas_escutando() -> list[PortaEscutando]:
    cache: dict = {}
    vistos = set()
    saida = []
    for c in _conexoes_inet():
        if c.status != psutil.CONN_LISTEN or not c.laddr:
            continue
        chave = (c.laddr.ip, c.laddr.port)
        if chave in vistos:
            continue
        vistos.add(chave)
        saida.append(PortaEscutando(pid=c.pid, processo=_nome_processo(c.pid, cache),
                                    endereco=c.laddr.ip, porta=c.laddr.port))
    return sorted(saida, key=lambda p: p.porta)


def top_processos(n: int = 8) -> list[dict]:
    lista = []
    for p in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
        info = p.info
        lista.append({"pid": info["pid"], "nome": info["name"] or "?",
                      "cpu": round(info["cpu_percent"] or 0.0, 1),
                      "memoria": round(info["memory_percent"] or 0.0, 1)})
    return sorted(lista, key=lambda x: (x["cpu"], x["memoria"]), reverse=True)[:n]


def identidade() -> dict:
    return {
        "hostname": socket.gethostname(),
        "ip": _ip_local(),
        "sistema": f"{platform.system()} {platform.release()}",
        "cpus": psutil.cpu_count(),
        "memoria_gb": round(psutil.virtual_memory().total / 1024**3, 1),
        "boot": datetime.fromtimestamp(psutil.boot_time()).isoformat(timespec="seconds"),
    }


def _ip_local() -> str:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("10.255.255.255", 1))  # não envia pacotes; só escolhe a interface
            return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"


def rede_local_sugerida() -> str:
    """Sugestão de /24 da interface principal, para preencher o campo de alvo."""
    ip = _ip_local()
    return str(ipaddress.ip_network(f"{ip}/24", strict=False))


def como_dict(obj) -> dict:
    return asdict(obj)
