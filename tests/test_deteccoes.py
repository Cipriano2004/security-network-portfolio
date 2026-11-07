from netsoc import deteccoes


def _scan(ativos, inicio="2026-11-01T10:00:00"):
    return {"alvo": "10.0.0.0/24", "inicio": inicio, "ativos": [
        {"ip": ip, "hostname": "", "portas": [{"porta": p, "servico": "", "banner": ""} for p in portas]}
        for ip, portas in ativos]}


def _regras(achados):
    return sorted((a.regra, a.alvo, a.evidencia.get("porta")) for a in achados)


def test_servicos_de_risco_geram_achado_com_tecnica():
    achados = deteccoes.avaliar_scan(_scan([("10.0.0.5", [22, 23, 443, 3389])]))
    por_porta = {a.evidencia["porta"]: a for a in achados}
    assert set(por_porta) == {23, 3389}  # SSH (baixo) e HTTPS (info) não geram achado
    assert por_porta[23].severidade == "alto" and por_porta[23].tecnica == "T1040"
    assert por_porta[3389].tecnica == "T1021.001"


def test_dispositivo_novo_porta_nova_e_sumiu():
    antes = _scan([("10.0.0.1", [53]), ("10.0.0.2", [22]), ("10.0.0.3", [80])])
    depois = _scan([("10.0.0.1", [53]), ("10.0.0.2", [22, 8080]), ("10.0.0.9", [80])],
                   inicio="2026-11-02T10:00:00")
    regras = _regras(deteccoes.avaliar_scan(depois, antes))
    assert ("NET-002", "10.0.0.9", None) in regras
    assert ("NET-003", "10.0.0.2", 8080) in regras
    assert ("NET-004", "10.0.0.3", None) in regras


def test_sem_scan_anterior_nao_compara():
    achados = deteccoes.avaliar_scan(_scan([("10.0.0.9", [80])]))
    assert not [a for a in achados if a.regra in ("NET-002", "NET-003", "NET-004")]


def test_conexao_para_porta_de_c2():
    achados = deteccoes.avaliar_conexoes([
        {"pid": 10, "processo": "malware", "local": "x", "remoto_ip": "203.0.113.5",
         "remoto_porta": 4444, "status": "ESTABLISHED"},
        {"pid": 11, "processo": "chrome", "local": "x", "remoto_ip": "142.250.0.1",
         "remoto_porta": 443, "status": "ESTABLISHED"},
    ])
    assert [(a.regra, a.alvo, a.severidade) for a in achados] == [("HOST-001", "malware", "alto")]


def test_muitos_destinos_externos():
    conexoes = [{"pid": 5, "processo": "beacon", "local": "x", "remoto_ip": f"198.51.100.{i}",
                 "remoto_porta": 443, "status": "ESTABLISHED"} for i in range(30)]
    achados = deteccoes.avaliar_conexoes(conexoes)
    assert [a.regra for a in achados] == ["HOST-002"]
    assert achados[0].evidencia["destinos"] == 30


def test_escuta_em_porta_nao_padrao_so_em_todas_interfaces():
    achados = deteccoes.avaliar_escuta([
        {"pid": 1, "processo": "app", "endereco": "0.0.0.0", "porta": 31337},
        {"pid": 2, "processo": "web", "endereco": "0.0.0.0", "porta": 443},
        {"pid": 3, "processo": "dev", "endereco": "127.0.0.1", "porta": 31338},
        {"pid": None, "processo": "desconhecido", "endereco": "0.0.0.0", "porta": 2024},
    ])
    assert [(a.alvo, a.evidencia["porta"]) for a in achados] == [("app", 31337),
                                                                 ("desconhecido", 2024)]
    assert "administrador" in achados[1].descricao


def test_cpu_alta():
    achados = deteccoes.avaliar_processos([{"pid": 1, "nome": "xmrig", "cpu": 99.0},
                                           {"pid": 2, "nome": "code", "cpu": 40.0}])
    assert [(a.regra, a.tecnica) for a in achados] == [("HOST-004", "T1496")]


def test_chave_estavel_para_deduplicar():
    a = deteccoes.avaliar_scan(_scan([("10.0.0.5", [23])]))[0]
    b = deteccoes.avaliar_scan(_scan([("10.0.0.5", [23])], inicio="2026-12-01T00:00:00"))[0]
    assert a.chave == b.chave == "NET-001|10.0.0.5|23"


def test_contagem_por_severidade():
    assert deteccoes.contar_por_severidade([{"severidade": "alto"}, {"severidade": "alto"},
                                            {"severidade": "baixo"}]) == \
        {"info": 0, "baixo": 1, "medio": 0, "alto": 2}
