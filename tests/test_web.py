import pytest

from netsoc import demo
from netsoc.armazenamento import Armazenamento
from netsoc.motor import Motor
from netsoc.web import criar_app


@pytest.fixture
def app_real():
    db = Armazenamento(":memory:")
    db.definir("modo", "real")
    return criar_app(db, Motor(db), monitorar=False)


@pytest.fixture
def app_demo():
    db = Armazenamento(":memory:")
    demo.carregar(db)
    return criar_app(db, Motor(db), monitorar=False)


POST_OK = {"X-NetSOC": "1"}


def test_painel_e_cabecalhos(app_real):
    r = app_real.test_client().get("/")
    assert r.status_code == 200
    assert b"NetSOC Lab" in r.data
    assert "script-src 'self'" in r.headers["Content-Security-Policy"]
    assert r.headers["X-Frame-Options"] == "DENY"


def test_scan_exige_cabecalho_e_mesma_origem(app_real):
    c = app_real.test_client()
    assert c.post("/api/scan", json={"alvo": "127.0.0.1"}).status_code == 403
    assert c.post("/api/scan", json={"alvo": "127.0.0.1"},
                  headers=POST_OK | {"Origin": "http://site-malicioso.com"}).status_code == 403


def test_scan_recusa_rede_publica(app_real):
    r = app_real.test_client().post("/api/scan", json={"alvo": "8.8.8.0/24"}, headers=POST_OK)
    assert r.status_code == 400
    assert "não é uma rede privada" in r.get_json()["erro"]


def test_scan_aceito_em_segundo_plano(app_real):
    motor = app_real.extensions["netsoc"]["motor"]
    r = app_real.test_client().post("/api/scan", json={"alvo": "127.0.0.1"}, headers=POST_OK)
    assert r.status_code == 202 and r.get_json()["alvo"] == "127.0.0.1/32"
    assert motor.scan_em_andamento["alvo"] == "127.0.0.1/32"


def test_demo_resumo_achados_e_ativos(app_demo):
    c = app_demo.test_client()
    resumo = c.get("/api/resumo").get_json()
    assert resumo["demo"] is True
    assert resumo["ultimo_scan"]["ativos"] == 8
    assert resumo["achados"]["alto"] > 0
    regras = {a["regra"] for a in c.get("/api/achados").get_json()["achados"]}
    assert {"NET-001", "NET-002", "NET-003", "NET-004", "HOST-001", "HOST-004"} <= regras
    assert len(c.get("/api/metricas").get_json()["metricas"]) == 120
    assert c.get("/api/ativos").get_json()["scan"]["alvo"] == demo.REDE


def test_demo_nao_permite_scan(app_demo):
    r = app_demo.test_client().post("/api/scan", json={"alvo": "10.0.0.0/24"}, headers=POST_OK)
    assert r.status_code == 409


def test_exportacao_jsonl(app_demo):
    r = app_demo.test_client().get("/api/eventos.jsonl")
    assert r.mimetype == "application/x-ndjson"
    assert r.data.count(b"\n") >= 10
    assert b'"rule"' in r.data


def test_ciclo_do_motor_coleta_e_avalia_o_host_real():
    db = Armazenamento(":memory:")
    motor = Motor(db)
    saida = motor.ciclo()
    assert 0 <= saida["metricas"].cpu <= 100
    assert len(db.ultimas_metricas()) == 1
