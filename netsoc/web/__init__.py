"""Painel web e API JSON. Escuta só em 127.0.0.1 por padrão."""

from flask import Flask, abort, jsonify, render_template, request

from .. import __version__, deteccoes, host
from ..alvos import AlvoInvalido, validar_alvo
from ..armazenamento import Armazenamento
from ..motor import Motor

CSP = ("default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; "
       "font-src 'self'; img-src 'self' data:; connect-src 'self'; object-src 'none'; "
       "frame-ancestors 'none'; base-uri 'self'; form-action 'self'")


def criar_app(db: Armazenamento, motor: Motor | None = None, monitorar: bool = True) -> Flask:
    app = Flask(__name__)
    app.json.sort_keys = False
    app.json.ensure_ascii = False
    motor = motor or Motor(db)
    app.extensions["netsoc"] = {"db": db, "motor": motor}
    modo_demo = db.obter("modo") == "demo"
    if monitorar and not modo_demo:
        motor.iniciar()

    def demo() -> bool:
        return db.obter("modo") == "demo"

    @app.after_request
    def cabecalhos(resp):
        resp.headers.setdefault("X-Content-Type-Options", "nosniff")
        resp.headers.setdefault("X-Frame-Options", "DENY")
        resp.headers.setdefault("Referrer-Policy", "no-referrer")
        resp.headers.setdefault("Content-Security-Policy", CSP)
        resp.headers.setdefault("Cache-Control", "no-store")
        return resp

    @app.before_request
    def somente_mesma_origem():
        # A API altera estado (scan): bloqueia requisições de outros sites (CSRF via navegador)
        if request.method == "POST":
            origem = request.headers.get("Origin") or request.headers.get("Referer") or ""
            if origem and not origem.startswith(request.host_url.rstrip("/")):
                abort(403)
            if request.headers.get("X-NetSOC") != "1":
                abort(403)

    @app.get("/")
    def painel():
        return render_template("painel.html", versao=__version__, demo=demo(),
                               alvo_sugerido="10.10.20.0/24" if demo()
                               else host.rede_local_sugerida())

    @app.get("/api/resumo")
    def resumo():
        scan = db.ultimo_scan()
        achados = db.listar_achados()
        portas_risco = 0
        if scan:
            from ..servicos import CATALOGO, ORDEM_RISCO
            portas_risco = sum(
                1 for a in scan["ativos"] for p in a["portas"]
                if p["porta"] in CATALOGO and ORDEM_RISCO[CATALOGO[p["porta"]].risco] >= 2)
        return jsonify(
            demo=demo(),
            host=({"hostname": db.obter("host_demo"), "ip": ""} if demo() else host.identidade()),
            ultimo_scan={k: scan[k] for k in ("id", "alvo", "inicio", "duracao_s",
                                               "hosts_testados")} | {"ativos": len(scan["ativos"])}
            if scan else None,
            achados=deteccoes.contar_por_severidade(achados),
            total_achados=len(achados),
            portas_risco=portas_risco,
            modelo={"pronto": motor.detector.pronto or demo(),
                    "amostras": motor.detector.amostras_treino if not demo() else 106},
            scan_em_andamento=motor.scan_em_andamento,
        )

    @app.get("/api/ativos")
    def ativos():
        scan = db.ultimo_scan()
        return jsonify(scan=scan, historico=db.historico_scans())

    @app.get("/api/achados")
    def achados():
        return jsonify(achados=db.listar_achados())

    @app.get("/api/metricas")
    def metricas():
        return jsonify(metricas=db.ultimas_metricas(request.args.get("n", 120, type=int)))

    @app.get("/api/host")
    def host_detalhe():
        if demo():
            return jsonify(demo=True, processos=[], escuta=[], conexoes=[])
        return jsonify(
            demo=False,
            processos=host.top_processos(8),
            escuta=[host.como_dict(p) for p in host.portas_escutando()],
            conexoes=[host.como_dict(c) for c in host.conexoes_estabelecidas()][:60],
        )

    @app.post("/api/scan")
    def scan():
        if demo():
            return jsonify(erro="Modo demonstração: rode 'python -m netsoc serve' sem a "
                                "opção --demo para varrer uma rede real."), 409
        alvo = (request.get_json(silent=True) or {}).get("alvo", "")
        try:
            rede = validar_alvo(alvo)
        except AlvoInvalido as erro:
            return jsonify(erro=str(erro)), 400
        if not motor.iniciar_scan(str(rede)):
            return jsonify(erro="Já existe um scan em andamento."), 409
        return jsonify(ok=True, alvo=str(rede)), 202

    @app.get("/api/eventos.jsonl")
    def exportar():
        linhas = [{"@timestamp": a["momento"], "rule": {"id": a["regra"], "name": a["titulo"]},
                   "event": {"severity": a["severidade"]},
                   "threat": {"technique": {"id": a["tecnica"], "name": a["tecnica_nome"]}},
                   "netsoc": {"alvo": a["alvo"], "descricao": a["descricao"]}}
                  for a in db.listar_achados(1000)]
        import json
        corpo = "\n".join(json.dumps(linha, ensure_ascii=False) for linha in linhas) + "\n"
        return app.response_class(corpo, mimetype="application/x-ndjson", headers={
            "Content-Disposition": "attachment; filename=netsoc-eventos.jsonl"})

    return app
