"""Regras de detecção. Cada achado vem de um dado coletado de verdade e aponta a técnica
do MITRE ATT&CK relacionada.

Regras de rede (a partir do scan):
  NET-001 serviço de risco exposto
  NET-002 dispositivo novo na rede (comparado ao scan anterior do mesmo alvo)
  NET-003 porta nova aberta em dispositivo conhecido
  NET-004 dispositivo deixou de responder
Regras de host (a partir do psutil):
  HOST-001 conexão de saída para porta associada a backdoor/C2
  HOST-002 processo com muitas conexões externas distintas (possível beacon/exfiltração)
  HOST-003 serviço escutando em todas as interfaces numa porta não padrão
  HOST-004 uso de CPU sustentado alto por um processo
  HOST-005 comportamento anômalo do host (modelo de ML)
"""

from dataclasses import asdict, dataclass, field
from datetime import datetime

from .servicos import CATALOGO, ORDEM_RISCO, PORTAS_SUSPEITAS, servico

SEVERIDADES = ("info", "baixo", "medio", "alto")


@dataclass
class Achado:
    regra: str
    titulo: str
    severidade: str
    alvo: str
    descricao: str
    tecnica: str = ""
    tecnica_nome: str = ""
    evidencia: dict = field(default_factory=dict)
    momento: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))

    def para_dict(self) -> dict:
        return asdict(self)

    @property
    def chave(self) -> str:
        """Identifica o mesmo achado entre execuções (para não duplicar)."""
        extra = self.evidencia.get("porta") or self.evidencia.get("processo") or ""
        return f"{self.regra}|{self.alvo}|{extra}"


# ---------------------------------------------------------------- rede

def _data(iso: str) -> str:
    try:
        return datetime.fromisoformat(iso).strftime("%d/%m/%Y %H:%M")
    except ValueError:
        return iso


def avaliar_scan(atual: dict, anterior: dict | None = None) -> list[Achado]:
    """Recebe ResultadoScan.para_dict() do scan atual e, se houver, do anterior do mesmo alvo."""
    achados: list[Achado] = []
    for ativo in atual["ativos"]:
        rotulo = ativo["ip"] + (f" ({ativo['hostname']})" if ativo.get("hostname") else "")
        for p in ativo["portas"]:
            s = CATALOGO.get(p["porta"])
            if s and ORDEM_RISCO[s.risco] >= ORDEM_RISCO["medio"]:
                achados.append(Achado(
                    regra="NET-001", titulo=f"{s.nome} exposto na rede", severidade=s.risco,
                    alvo=ativo["ip"], descricao=f"{rotulo} aceita conexões em {s.porta}/tcp "
                    f"({s.nome}). {s.motivo}.", tecnica=s.tecnica, tecnica_nome=s.tecnica_nome,
                    evidencia={"porta": s.porta, "servico": s.nome, "banner": p.get("banner", "")},
                ))

    if anterior:
        antes = {a["ip"]: {p["porta"] for p in a["portas"]} for a in anterior["ativos"]}
        agora = {a["ip"]: {p["porta"] for p in a["portas"]} for a in atual["ativos"]}
        for ip in sorted(set(agora) - set(antes)):
            achados.append(Achado(
                regra="NET-002", titulo="Dispositivo novo na rede", severidade="medio", alvo=ip,
                descricao=f"{ip} não aparecia no scan anterior ({_data(anterior['inicio'])}). "
                "Confirme se é um equipamento autorizado.",
                tecnica="T1200", tecnica_nome="Hardware Additions",
                evidencia={"portas": sorted(agora[ip])},
            ))
        for ip in sorted(set(agora) & set(antes)):
            for porta in sorted(agora[ip] - antes[ip]):
                achados.append(Achado(
                    regra="NET-003", titulo="Porta nova aberta", severidade="medio", alvo=ip,
                    descricao=f"{ip} passou a aceitar conexões em {porta}/tcp "
                    f"({servico(porta).nome}), que estava fechada no scan anterior.",
                    tecnica="T1571", tecnica_nome="Non-Standard Port",
                    evidencia={"porta": porta, "servico": servico(porta).nome},
                ))
        for ip in sorted(set(antes) - set(agora)):
            achados.append(Achado(
                regra="NET-004", titulo="Dispositivo deixou de responder", severidade="baixo",
                alvo=ip, descricao=f"{ip} respondia no scan anterior e não respondeu agora.",
                evidencia={"portas_antes": sorted(antes[ip])},
            ))
    return achados


# ---------------------------------------------------------------- host

LIMIAR_DESTINOS_EXTERNOS = 25
LIMIAR_CPU_PROCESSO = 90.0
PORTAS_COMUNS_ESCUTA = {22, 53, 80, 443, 631, 3306, 5432, 8000, 8080, 5000, 6379, 27017}


def avaliar_conexoes(conexoes: list[dict]) -> list[Achado]:
    achados = []
    por_processo: dict[str, set[str]] = {}
    for c in conexoes:
        if c["remoto_porta"] in PORTAS_SUSPEITAS:
            achados.append(Achado(
                regra="HOST-001", titulo="Conexão para porta associada a backdoor/C2",
                severidade="alto", alvo=c["processo"],
                descricao=f"O processo {c['processo']} (PID {c['pid']}) está conectado a "
                f"{c['remoto_ip']}:{c['remoto_porta']} — porta usada por "
                f"{PORTAS_SUSPEITAS[c['remoto_porta']]}.",
                tecnica="T1571", tecnica_nome="Non-Standard Port",
                evidencia={"processo": c["processo"], "pid": c["pid"],
                           "destino": f"{c['remoto_ip']}:{c['remoto_porta']}"},
            ))
        por_processo.setdefault(c["processo"], set()).add(c["remoto_ip"])

    for processo, destinos in por_processo.items():
        if len(destinos) >= LIMIAR_DESTINOS_EXTERNOS:
            achados.append(Achado(
                regra="HOST-002", titulo="Processo falando com muitos destinos",
                severidade="medio", alvo=processo,
                descricao=f"{processo} mantém conexões com {len(destinos)} IPs diferentes. "
                "Navegadores fazem isso; outros processos podem indicar beacon ou exfiltração.",
                tecnica="T1041", tecnica_nome="Exfiltration Over C2 Channel",
                evidencia={"processo": processo, "destinos": len(destinos)},
            ))
    return achados


def _quem(p: dict) -> str:
    if p.get("pid"):
        return f"{p['processo']} (PID {p['pid']})"
    return "Um processo (execute como administrador para identificá-lo)"


def avaliar_escuta(portas: list[dict]) -> list[Achado]:
    achados = []
    for p in portas:
        if p["endereco"] in ("0.0.0.0", "::") and p["porta"] not in PORTAS_COMUNS_ESCUTA \
                and p["porta"] < 49152:
            achados.append(Achado(
                regra="HOST-003", titulo="Serviço aberto para a rede em porta não padrão",
                severidade="baixo", alvo=p["processo"],
                descricao=f"{_quem(p)} escuta em todas as interfaces na porta {p['porta']}/tcp. "
                "Confirme se precisa estar acessível pela rede.",
                tecnica="T1571", tecnica_nome="Non-Standard Port",
                evidencia={"processo": p["processo"], "porta": p["porta"]},
            ))
    return achados


def avaliar_processos(processos: list[dict]) -> list[Achado]:
    return [
        Achado(regra="HOST-004", titulo="Uso de CPU muito alto", severidade="medio",
               alvo=p["nome"], descricao=f"{p['nome']} (PID {p['pid']}) está usando "
               f"{p['cpu']}% de CPU. Mineração de criptomoeda é uma causa comum em hosts "
               "comprometidos.", tecnica="T1496", tecnica_nome="Resource Hijacking",
               evidencia={"processo": p["nome"], "pid": p["pid"], "cpu": p["cpu"]})
        for p in processos if p["cpu"] >= LIMIAR_CPU_PROCESSO
    ]


def contar_por_severidade(achados: list[dict]) -> dict[str, int]:
    contagem = dict.fromkeys(SEVERIDADES, 0)
    for a in achados:
        contagem[a["severidade"]] = contagem.get(a["severidade"], 0) + 1
    return contagem
