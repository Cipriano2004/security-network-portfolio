"""Catálogo de portas: nome do serviço, risco quando exposto e técnica do MITRE ATT&CK relacionada."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Servico:
    porta: int
    nome: str
    risco: str = "info"  # info | baixo | medio | alto
    motivo: str = ""
    tecnica: str = ""  # ID ATT&CK
    tecnica_nome: str = ""


_T_REMOTO = ("T1021", "Remote Services")
_T_EXPLORA = ("T1210", "Exploitation of Remote Services")
_T_SNIFF = ("T1040", "Network Sniffing")

CATALOGO: dict[int, Servico] = {s.porta: s for s in [
    Servico(21, "FTP", "alto", "Transmite usuário e senha sem criptografia", *_T_SNIFF),
    Servico(22, "SSH", "baixo", "Acesso remoto: garanta autenticação por chave e sem login de root",
            "T1021.004", "Remote Services: SSH"),
    Servico(23, "Telnet", "alto", "Acesso remoto sem criptografia (credenciais em texto claro)",
            *_T_SNIFF),
    Servico(25, "SMTP", "baixo", "Servidor de e-mail: verifique se não é relay aberto", "", ""),
    Servico(53, "DNS"),
    Servico(80, "HTTP", "baixo", "Interface web sem HTTPS", *_T_SNIFF),
    Servico(110, "POP3", "medio", "E-mail sem criptografia", *_T_SNIFF),
    Servico(135, "MS-RPC", "medio", "RPC do Windows exposto", *_T_EXPLORA),
    Servico(139, "NetBIOS", "medio", "Compartilhamento legado do Windows", "T1021.002",
            "Remote Services: SMB/Windows Admin Shares"),
    Servico(143, "IMAP", "medio", "E-mail sem criptografia", *_T_SNIFF),
    Servico(161, "SNMP"),
    Servico(443, "HTTPS"),
    Servico(445, "SMB", "alto", "Compartilhamento de arquivos do Windows (alvo comum de ransomware)",
            "T1021.002", "Remote Services: SMB/Windows Admin Shares"),
    Servico(515, "LPD"),
    Servico(554, "RTSP", "medio", "Stream de câmera: verifique senha padrão", "T1078.001",
            "Valid Accounts: Default Accounts"),
    Servico(631, "IPP"),
    Servico(993, "IMAPS"),
    Servico(995, "POP3S"),
    Servico(1433, "MSSQL", "alto", "Banco de dados acessível pela rede", *_T_EXPLORA),
    Servico(1883, "MQTT", "medio", "Broker IoT, frequentemente sem autenticação", *_T_EXPLORA),
    Servico(2375, "Docker API", "alto", "API do Docker sem TLS permite controle total do host",
            *_T_EXPLORA),
    Servico(3306, "MySQL", "alto", "Banco de dados acessível pela rede", *_T_EXPLORA),
    Servico(3389, "RDP", "alto", "Área de trabalho remota exposta (força bruta e exploits)",
            "T1021.001", "Remote Services: Remote Desktop Protocol"),
    Servico(5432, "PostgreSQL", "alto", "Banco de dados acessível pela rede", *_T_EXPLORA),
    Servico(5900, "VNC", "alto", "Controle remoto de tela, muitas vezes com senha fraca",
            "T1021.005", "Remote Services: VNC"),
    Servico(6379, "Redis", "alto", "Redis costuma não ter autenticação", *_T_EXPLORA),
    Servico(8080, "HTTP-alt", "baixo", "Interface web alternativa sem HTTPS", *_T_SNIFF),
    Servico(8443, "HTTPS-alt"),
    Servico(9100, "JetDirect"),
    Servico(27017, "MongoDB", "alto", "Banco de dados acessível pela rede", *_T_EXPLORA),
]}

PORTAS_PADRAO = sorted(CATALOGO)

# Portas historicamente associadas a backdoors/C2 (para conexões de saída no host)
PORTAS_SUSPEITAS = {4444: "Metasploit (padrão)", 1337: "backdoor comum", 31337: "Back Orifice",
                    6667: "IRC (C2 legado)", 6666: "IRC", 9001: "Tor ORPort", 5555: "ADB/backdoor",
                    12345: "NetBus"}

ORDEM_RISCO = {"info": 0, "baixo": 1, "medio": 2, "alto": 3}


def servico(porta: int) -> Servico:
    return CATALOGO.get(porta, Servico(porta, f"porta-{porta}"))


def classificar_dispositivo(portas: set[int]) -> str:
    """Palpite do tipo de dispositivo a partir das portas abertas."""
    if portas & {9100, 515, 631}:
        return "Impressora"
    if 554 in portas:
        return "Câmera IP"
    if portas & {3389, 445, 139, 135}:
        return "Computador Windows"
    if portas & {3306, 5432, 1433, 27017, 6379}:
        return "Servidor de banco de dados"
    if 53 in portas and portas & {80, 443}:
        return "Roteador / gateway"
    if 22 in portas and not portas & {80, 443, 8080}:
        return "Servidor Linux / dispositivo de rede"
    if portas & {80, 443, 8080, 8443}:
        return "Servidor ou equipamento com interface web"
    if 1883 in portas:
        return "Dispositivo IoT"
    return "Desconhecido"
