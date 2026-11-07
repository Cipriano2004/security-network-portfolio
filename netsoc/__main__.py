"""Linha de comando.

    python -m netsoc serve                 # painel em http://127.0.0.1:8080 (monitorando este PC)
    python -m netsoc serve --demo          # painel com a rede de laboratório fictícia
    python -m netsoc scan 192.168.0.0/24   # varredura pelo terminal
    python -m netsoc host                  # achados do próprio computador agora
"""

import argparse
import json
import logging
import sys
from pathlib import Path

from . import __version__, deteccoes, host
from .alvos import AlvoInvalido
from .armazenamento import Armazenamento
from .motor import Motor

DADOS = Path("dados")
CORES = {"alto": "\033[91m", "medio": "\033[93m", "baixo": "\033[94m", "info": "\033[90m"}
FIM = "\033[0m"


def _db(demo: bool = False) -> Armazenamento:
    nome = "netsoc-demo.db" if demo else "netsoc.db"
    return Armazenamento(DADOS / nome, log_eventos=None if demo else DADOS / "eventos.jsonl")


def _imprimir_achados(achados: list[dict]) -> None:
    if not achados:
        print("Nenhum achado.")
        return
    for a in sorted(achados, key=lambda x: deteccoes.SEVERIDADES.index(x["severidade"]),
                    reverse=True):
        cor = CORES.get(a["severidade"], "") if sys.stdout.isatty() else ""
        tecnica = f" [{a['tecnica']}]" if a["tecnica"] else ""
        print(f"{cor}{a['severidade'].upper():6}{FIM if cor else ''} {a['regra']} "
              f"{a['alvo']}: {a['titulo']}{tecnica}")
        print(f"       {a['descricao']}")


def cmd_scan(args) -> int:
    db = _db()
    motor = Motor(db)
    print(f"Varrendo {args.alvo} ... (use somente em redes que você administra)")
    try:
        saida = motor.executar_scan(args.alvo, permitir_publico=args.autorizado)
    except AlvoInvalido as erro:
        print(f"Erro: {erro}", file=sys.stderr)
        return 2
    r = saida["resultado"]
    if args.json:
        print(json.dumps(r, ensure_ascii=False, indent=2))
        return 0
    print(f"\n{len(r['ativos'])} ativo(s) em {r['hosts_testados']} endereços · "
          f"{r['duracao_s']} s\n")
    for a in r["ativos"]:
        portas = ", ".join(f"{p['porta']}/{p['servico']}" for p in a["portas"]) or "—"
        print(f"  {a['ip']:15} {a['tipo'][:34]:34} {portas}")
    print()
    _imprimir_achados(saida["achados"])
    print(f"\nResultados salvos em {DADOS}/. Eventos novos em {DADOS}/eventos.jsonl")
    return 0


def cmd_host(_args) -> int:
    conexoes = [host.como_dict(c) for c in host.conexoes_estabelecidas()]
    escuta = [host.como_dict(p) for p in host.portas_escutando()]
    achados = (deteccoes.avaliar_conexoes(conexoes) + deteccoes.avaliar_escuta(escuta)
               + deteccoes.avaliar_processos(host.top_processos(15)))
    m = host.coletar_metricas()
    print(f"{host.identidade()['hostname']} · CPU {m.cpu}% · memória {m.memoria}% · "
          f"{m.conexoes} conexões ({m.conexoes_externas} externas) · "
          f"{len(escuta)} portas em escuta\n")
    _imprimir_achados([a.para_dict() for a in achados])
    return 0


def cmd_serve(args) -> int:
    from .demo import carregar
    from .web import criar_app

    db = _db(demo=args.demo)
    if args.demo:
        carregar(db)
        print("MODO DEMONSTRAÇÃO: rede de laboratório fictícia 10.10.20.0/24.")
    else:
        if db.obter("modo") == "demo":
            db.limpar()
        db.definir("modo", "real")
    app = criar_app(db, Motor(db, intervalo=args.intervalo))
    print(f"NetSOC Lab {__version__} em http://{args.host}:{args.porta}")
    from waitress import serve
    serve(app, host=args.host, port=args.porta, threads=6)
    return 0


def main(argv=None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    p = argparse.ArgumentParser(prog="netsoc", description="NetSOC Lab — inventário de rede, "
                                "detecções MITRE ATT&CK e monitoramento de host.")
    p.add_argument("--version", action="version", version=__version__)
    sub = p.add_subparsers(dest="comando", required=True)

    s = sub.add_parser("serve", help="inicia o painel web")
    s.add_argument("--demo", action="store_true", help="carrega a rede de laboratório fictícia")
    s.add_argument("--host", default="127.0.0.1")
    s.add_argument("--porta", type=int, default=8080)
    s.add_argument("--intervalo", type=float, default=5.0, help="segundos entre coletas")
    s.set_defaults(func=cmd_serve)

    sc = sub.add_parser("scan", help="varre uma rede e mostra os achados")
    sc.add_argument("alvo", help="IP ou CIDR, ex.: 192.168.0.0/24")
    sc.add_argument("--json", action="store_true", help="saída em JSON")
    sc.add_argument("--autorizado", action="store_true",
                    help="permite alvo público (somente com autorização por escrito)")
    sc.set_defaults(func=cmd_scan)

    h = sub.add_parser("host", help="avalia o próprio computador")
    h.set_defaults(func=cmd_host)

    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
