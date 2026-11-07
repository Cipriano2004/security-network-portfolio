"""Descoberta de hosts e varredura de portas TCP (connect scan), sem precisar de root.

Um host é considerado ativo se responder a qualquer porta de sondagem — tanto aceitando a
conexão quanto recusando (RST). Isso funciona mesmo quando o ICMP (ping) está bloqueado.
"""

import errno
import socket
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass, field
from datetime import datetime

from .alvos import hosts_do_alvo, validar_alvo
from .servicos import PORTAS_PADRAO, classificar_dispositivo, servico

PORTAS_SONDA = [80, 443, 22, 445, 139, 3389, 53, 8080]
RECUSADO = {errno.ECONNREFUSED, 10061}  # 10061 = WSAECONNREFUSED no Windows


@dataclass
class PortaAberta:
    porta: int
    servico: str
    banner: str = ""


@dataclass
class Ativo:
    ip: str
    hostname: str = ""
    tipo: str = "Desconhecido"
    portas: list[PortaAberta] = field(default_factory=list)
    latencia_ms: float | None = None

    def numeros_portas(self) -> set[int]:
        return {p.porta for p in self.portas}


@dataclass
class ResultadoScan:
    alvo: str
    inicio: str
    fim: str = ""
    duracao_s: float = 0.0
    hosts_testados: int = 0
    ativos: list[Ativo] = field(default_factory=list)

    def para_dict(self) -> dict:
        return asdict(self)


def _conectar(ip: str, porta: int, timeout: float) -> tuple[bool, bool, float]:
    """Retorna (aberta, host_respondeu, latência_ms)."""
    inicio = time.perf_counter()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(timeout)
        codigo = s.connect_ex((ip, porta))
    ms = (time.perf_counter() - inicio) * 1000
    if codigo == 0:
        return True, True, ms
    return False, codigo in RECUSADO, ms


def host_ativo(ip: str, timeout: float = 0.6) -> float | None:
    """Latência em ms se o host respondeu em alguma porta de sondagem; senão None."""
    for porta in PORTAS_SONDA:
        try:
            _aberta, respondeu, ms = _conectar(ip, porta, timeout)
        except OSError:
            continue
        if respondeu:
            return round(ms, 1)
    return None


def capturar_banner(ip: str, porta: int, timeout: float = 1.5) -> str:
    """Lê a apresentação do serviço (SSH/FTP/SMTP) ou o cabeçalho Server: de HTTP."""
    try:
        with socket.create_connection((ip, porta), timeout=timeout) as s:
            s.settimeout(timeout)
            if porta in (80, 8080):
                s.sendall(f"HEAD / HTTP/1.0\r\nHost: {ip}\r\n\r\n".encode())
                dados = s.recv(1024).decode(errors="ignore")
                for linha in dados.splitlines():
                    if linha.lower().startswith("server:"):
                        return linha.split(":", 1)[1].strip()[:120]
                return ""
            return s.recv(256).decode(errors="ignore").strip().splitlines()[0][:120]
    except (OSError, IndexError):
        return ""


def varrer_portas(ip: str, portas: list[int], timeout: float = 0.6,
                  banners: bool = True) -> list[PortaAberta]:
    abertas = []
    for porta in portas:
        try:
            aberta, _, _ = _conectar(ip, porta, timeout)
        except OSError:
            continue
        if aberta:
            banner = capturar_banner(ip, porta) if banners and porta in (21, 22, 25, 80, 8080) \
                else ""
            abertas.append(PortaAberta(porta, servico(porta).nome, banner))
    return abertas


def _hostname(ip: str) -> str:
    try:
        return socket.gethostbyaddr(ip)[0]
    except (OSError, UnicodeError):
        return ""


def varrer(alvo: str, portas: list[int] | None = None, permitir_publico: bool = False,
           trabalhadores: int = 64, timeout: float = 0.6, banners: bool = True,
           progresso=None) -> ResultadoScan:
    """Descobre hosts ativos no alvo e varre as portas de cada um."""
    rede = validar_alvo(alvo, permitir_publico=permitir_publico)
    portas = portas or PORTAS_PADRAO
    ips = hosts_do_alvo(rede)
    inicio = time.perf_counter()
    resultado = ResultadoScan(alvo=str(rede), inicio=datetime.now().isoformat(timespec="seconds"),
                              hosts_testados=len(ips))

    with ThreadPoolExecutor(max_workers=min(trabalhadores, len(ips))) as ex:
        latencias = dict(zip(ips, ex.map(lambda ip: host_ativo(ip, timeout), ips), strict=True))
    vivos = [ip for ip, lat in latencias.items() if lat is not None]
    if progresso:
        progresso(f"{len(vivos)} host(s) ativo(s) de {len(ips)} testados")

    def detalhar(ip: str) -> Ativo:
        abertas = varrer_portas(ip, portas, timeout, banners)
        return Ativo(ip=ip, hostname=_hostname(ip), latencia_ms=latencias[ip], portas=abertas,
                     tipo=classificar_dispositivo({p.porta for p in abertas}))

    with ThreadPoolExecutor(max_workers=min(16, max(1, len(vivos)))) as ex:
        ativos = list(ex.map(detalhar, vivos))

    resultado.ativos = sorted(ativos, key=lambda a: tuple(int(o) for o in a.ip.split(".")))
    resultado.fim = datetime.now().isoformat(timespec="seconds")
    resultado.duracao_s = round(time.perf_counter() - inicio, 2)
    return resultado
