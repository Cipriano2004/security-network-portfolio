"""Validação do alvo de varredura.

Varrer redes de terceiros sem autorização pode ser crime (no Brasil, Lei 12.737/2012) e viola
termos de uso de provedores. Por padrão o NetSOC só aceita redes privadas (RFC 1918),
loopback e link-local, com tamanho máximo de /22.
"""

import ipaddress

MAX_HOSTS = 1024


class AlvoInvalido(ValueError):
    pass


def validar_alvo(alvo: str, permitir_publico: bool = False) -> ipaddress.IPv4Network:
    """Converte '192.168.0.0/24' ou '10.0.0.5' em rede e aplica as travas de segurança."""
    try:
        rede = ipaddress.ip_network((alvo or "").strip(), strict=False)
    except ValueError as erro:
        raise AlvoInvalido(f"Alvo inválido: {alvo!r}. Use um IP ou CIDR, ex.: 192.168.0.0/24") \
            from erro

    if rede.version != 4:
        raise AlvoInvalido("Somente IPv4 é suportado.")
    if rede.num_addresses > MAX_HOSTS:
        raise AlvoInvalido(f"Rede grande demais ({rede.num_addresses} endereços). "
                           f"O máximo é /22 ({MAX_HOSTS} endereços).")

    interno = rede.is_private or rede.is_loopback or rede.is_link_local
    if not interno and not permitir_publico:
        raise AlvoInvalido(
            f"{rede} não é uma rede privada. Varra somente redes que você administra ou tem "
            "autorização por escrito para testar. Para um alvo público autorizado, use a opção "
            "--autorizado."
        )
    return rede


def hosts_do_alvo(rede: ipaddress.IPv4Network) -> list[str]:
    """Lista os IPs a testar (um único IP retorna ele mesmo)."""
    if rede.num_addresses == 1:
        return [str(rede.network_address)]
    return [str(ip) for ip in rede.hosts()]
