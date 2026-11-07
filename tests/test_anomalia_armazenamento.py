import json
import random

from netsoc import deteccoes
from netsoc.anomalia import MINIMO_AMOSTRAS, DetectorAnomalia, explicar
from netsoc.armazenamento import Armazenamento


def _normais(n=200, semente=1):
    r = random.Random(semente)
    return [[r.gauss(20, 5), r.gauss(55, 2), r.gauss(40, 5), r.gauss(12, 3), r.gauss(240, 4)]
            for _ in range(n)]


def test_nao_treina_sem_linha_de_base():
    d = DetectorAnomalia()
    assert d.treinar(_normais(MINIMO_AMOSTRAS - 1)) is False
    assert d.avaliar([1, 2, 3, 4, 5]) is None


def test_detecta_pico_e_aceita_leitura_normal():
    d = DetectorAnomalia()
    assert d.treinar(_normais())
    normal = d.avaliar([21, 55, 41, 12, 241])
    pico = d.avaliar([98, 57, 90, 70, 300])
    assert normal.anomala is False
    assert pico.anomala is True
    assert pico.pontuacao < normal.pontuacao
    assert pico.desvios["cpu"] > 3
    assert "CPU acima do normal" in explicar(pico.desvios)


def test_explicar_sem_desvio_relevante():
    assert explicar({"cpu": 0.5, "memoria": -0.2}) == "combinação incomum das métricas"


def _achado(alvo="10.0.0.5", porta=23):
    return deteccoes.avaliar_scan({"alvo": "x", "inicio": "2026-01-01T00:00:00", "ativos": [
        {"ip": alvo, "hostname": "", "portas": [{"porta": porta, "servico": "", "banner": ""}]}]})[0]


def test_achados_deduplicados_e_log_jsonl(tmp_path):
    log = tmp_path / "eventos.jsonl"
    db = Armazenamento(":memory:", log_eventos=log)
    assert len(db.registrar_achados([_achado()])) == 1
    assert db.registrar_achados([_achado()]) == []  # repetido não gera novo evento
    lista = db.listar_achados()
    assert len(lista) == 1 and lista[0]["ocorrencias"] == 2

    eventos = [json.loads(linha) for linha in log.read_text(encoding="utf-8").splitlines()]
    assert len(eventos) == 1
    assert eventos[0]["rule"]["id"] == "NET-001"
    assert eventos[0]["threat"]["technique"]["id"] == "T1040"
    assert eventos[0]["event"]["severity"] == "alto"


def test_ordenacao_por_severidade():
    db = Armazenamento(":memory:")
    db.registrar_achados([_achado(porta=135), _achado("10.0.0.6", 23)])  # medio, alto
    assert [a["severidade"] for a in db.listar_achados()] == ["alto", "medio"]


def test_scans_e_ultimo_por_alvo():
    db = Armazenamento(":memory:")
    a = db.salvar_scan({"alvo": "10.0.0.0/24", "inicio": "1", "duracao_s": 1, "ativos": []})
    db.salvar_scan({"alvo": "192.168.0.0/24", "inicio": "2", "duracao_s": 1, "ativos": []})
    b = db.salvar_scan({"alvo": "10.0.0.0/24", "inicio": "3", "duracao_s": 1, "ativos": []})
    assert db.ultimo_scan("10.0.0.0/24")["id"] == b
    assert db.ultimo_scan("10.0.0.0/24", antes_de=b)["id"] == a
    assert len(db.historico_scans()) == 3


def test_metricas_e_limpeza():
    db = Armazenamento(":memory:")
    db.salvar_metricas({"momento": "2026-01-01T00:00:00", "cpu": 1}, -0.1)
    assert db.ultimas_metricas()[0]["pontuacao"] == -0.1
    db.definir("modo", "demo")
    db.limpar()
    assert db.ultimas_metricas() == [] and db.obter("modo") is None
