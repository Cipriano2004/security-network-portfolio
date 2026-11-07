import socket
import threading

import pytest

from netsoc import scanner
from netsoc.alvos import AlvoInvalido, hosts_do_alvo, validar_alvo
from netsoc.servicos import classificar_dispositivo


@pytest.mark.parametrize("alvo", ["192.168.0.0/24", "10.0.0.5", "172.16.4.0/23", "127.0.0.1",
                                  "169.254.1.0/24"])
def test_aceita_redes_internas(alvo):
    assert validar_alvo(alvo)


@pytest.mark.parametrize("alvo, trecho", [
    ("8.8.8.0/24", "não é uma rede privada"),
    ("1.1.1.1", "não é uma rede privada"),
    ("10.0.0.0/16", "grande demais"),
    ("abc", "inválido"),
    ("", "inválido"),
    ("::1", "IPv4"),
])
def test_recusa_alvos_perigosos_ou_invalidos(alvo, trecho):
    with pytest.raises(AlvoInvalido, match=trecho):
        validar_alvo(alvo)


def test_publico_somente_com_autorizacao_explicita():
    assert str(validar_alvo("8.8.8.8", permitir_publico=True)) == "8.8.8.8/32"


def test_hosts_do_alvo():
    assert hosts_do_alvo(validar_alvo("10.0.0.7")) == ["10.0.0.7"]
    assert len(hosts_do_alvo(validar_alvo("10.0.0.0/30"))) == 2


def test_classificacao_de_dispositivos():
    assert classificar_dispositivo({9100, 80}) == "Impressora"
    assert classificar_dispositivo({554, 80}) == "Câmera IP"
    assert classificar_dispositivo({445, 3389}) == "Computador Windows"
    assert classificar_dispositivo({5432}) == "Servidor de banco de dados"
    assert classificar_dispositivo(set()) == "Desconhecido"


@pytest.fixture
def servidor_falso():
    """Servidor TCP local que se apresenta como SSH, para testar o scanner de verdade."""
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("127.0.0.1", 0))
    srv.listen(8)
    parar = threading.Event()

    def atender():
        srv.settimeout(0.2)
        while not parar.is_set():
            try:
                con, _ = srv.accept()
            except OSError:
                continue
            try:
                con.sendall(b"SSH-2.0-OpenSSH_9.6 teste\r\n")
            finally:
                con.close()

    t = threading.Thread(target=atender, daemon=True)
    t.start()
    yield srv.getsockname()[1]
    parar.set()
    srv.close()


def test_varredura_real_em_localhost(servidor_falso, monkeypatch):
    porta = servidor_falso
    monkeypatch.setattr(scanner, "PORTAS_SONDA", [porta])
    r = scanner.varrer("127.0.0.1", portas=[porta], banners=False)
    assert r.hosts_testados == 1
    assert [a.ip for a in r.ativos] == ["127.0.0.1"]
    assert [p.porta for p in r.ativos[0].portas] == [porta]


def test_banner_ssh(servidor_falso):
    assert scanner.capturar_banner("127.0.0.1", servidor_falso).startswith("SSH-2.0-OpenSSH_9.6")


def test_porta_fechada_nao_aparece():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        livre = s.getsockname()[1]  # porta que fica fechada após sair do bloco
    assert scanner.varrer_portas("127.0.0.1", [livre], banners=False) == []
