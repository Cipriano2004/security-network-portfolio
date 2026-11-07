"""Persistência em SQLite (scans, achados e métricas) e log de eventos em JSON Lines.

O arquivo JSONL segue nomes de campos inspirados no Elastic Common Schema e pode ser
lido diretamente por Wazuh, Splunk ou Filebeat.
"""

import json
import sqlite3
import threading
from pathlib import Path

ESQUEMA = """
CREATE TABLE IF NOT EXISTS scans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    alvo TEXT NOT NULL,
    inicio TEXT NOT NULL,
    duracao_s REAL,
    ativos INTEGER,
    dados TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS achados (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chave TEXT NOT NULL UNIQUE,
    regra TEXT NOT NULL,
    severidade TEXT NOT NULL,
    alvo TEXT,
    titulo TEXT,
    primeiro TEXT NOT NULL,
    ultimo TEXT NOT NULL,
    ocorrencias INTEGER NOT NULL DEFAULT 1,
    dados TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS metricas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    momento TEXT NOT NULL,
    dados TEXT NOT NULL,
    pontuacao REAL
);
CREATE TABLE IF NOT EXISTS meta (chave TEXT PRIMARY KEY, valor TEXT);
"""


class Armazenamento:
    def __init__(self, caminho: str | Path, log_eventos: str | Path | None = None):
        self.caminho = str(caminho)
        if self.caminho != ":memory:":
            Path(self.caminho).parent.mkdir(parents=True, exist_ok=True)
        self.log_eventos = Path(log_eventos) if log_eventos else None
        if self.log_eventos:
            self.log_eventos.parent.mkdir(parents=True, exist_ok=True)
        self._trava = threading.Lock()
        self._con = sqlite3.connect(self.caminho, check_same_thread=False)
        self._con.row_factory = sqlite3.Row
        self._con.executescript(ESQUEMA)

    # ---------------------------------------------------------- meta
    def definir(self, chave: str, valor: str) -> None:
        with self._trava, self._con:
            self._con.execute("INSERT OR REPLACE INTO meta VALUES (?, ?)", (chave, valor))

    def obter(self, chave: str, padrao: str | None = None) -> str | None:
        linha = self._con.execute("SELECT valor FROM meta WHERE chave = ?", (chave,)).fetchone()
        return linha["valor"] if linha else padrao

    # ---------------------------------------------------------- scans
    def salvar_scan(self, resultado: dict) -> int:
        with self._trava, self._con:
            cur = self._con.execute(
                "INSERT INTO scans (alvo, inicio, duracao_s, ativos, dados) VALUES (?,?,?,?,?)",
                (resultado["alvo"], resultado["inicio"], resultado["duracao_s"],
                 len(resultado["ativos"]), json.dumps(resultado, ensure_ascii=False)))
            return cur.lastrowid

    def ultimo_scan(self, alvo: str | None = None, antes_de: int | None = None) -> dict | None:
        sql, args = "SELECT id, dados FROM scans", []
        filtros = []
        if alvo:
            filtros.append("alvo = ?")
            args.append(alvo)
        if antes_de:
            filtros.append("id < ?")
            args.append(antes_de)
        if filtros:
            sql += " WHERE " + " AND ".join(filtros)
        linha = self._con.execute(sql + " ORDER BY id DESC LIMIT 1", args).fetchone()
        if not linha:
            return None
        return json.loads(linha["dados"]) | {"id": linha["id"]}

    def historico_scans(self, limite: int = 20) -> list[dict]:
        linhas = self._con.execute(
            "SELECT id, alvo, inicio, duracao_s, ativos FROM scans ORDER BY id DESC LIMIT ?",
            (limite,)).fetchall()
        return [dict(linha) for linha in linhas]

    # ---------------------------------------------------------- achados
    def registrar_achados(self, achados) -> list[dict]:
        """Grava achados novos e atualiza os repetidos. Retorna só os novos (para o log)."""
        novos = []
        with self._trava, self._con:
            for a in achados:
                d = a.para_dict()
                existente = self._con.execute("SELECT id FROM achados WHERE chave = ?",
                                              (a.chave,)).fetchone()
                if existente:
                    self._con.execute(
                        "UPDATE achados SET ultimo = ?, ocorrencias = ocorrencias + 1, dados = ? "
                        "WHERE id = ?", (a.momento, json.dumps(d, ensure_ascii=False),
                                         existente["id"]))
                else:
                    self._con.execute(
                        "INSERT INTO achados (chave, regra, severidade, alvo, titulo, primeiro, "
                        "ultimo, dados) VALUES (?,?,?,?,?,?,?,?)",
                        (a.chave, a.regra, a.severidade, a.alvo, a.titulo, a.momento, a.momento,
                         json.dumps(d, ensure_ascii=False)))
                    novos.append(d)
        for d in novos:
            self._escrever_evento(d)
        return novos

    def listar_achados(self, limite: int = 200) -> list[dict]:
        ordem = ("CASE severidade WHEN 'alto' THEN 3 WHEN 'medio' THEN 2 "
                 "WHEN 'baixo' THEN 1 ELSE 0 END")
        linhas = self._con.execute(
            f"SELECT dados, primeiro, ultimo, ocorrencias FROM achados "  # noqa: S608
            f"ORDER BY {ordem} DESC, ultimo DESC LIMIT ?", (limite,)).fetchall()
        return [json.loads(r["dados"]) | {"primeiro": r["primeiro"], "ultimo": r["ultimo"],
                                          "ocorrencias": r["ocorrencias"]} for r in linhas]

    def _escrever_evento(self, achado: dict) -> None:
        if not self.log_eventos:
            return
        evento = {
            "@timestamp": achado["momento"],
            "event": {"kind": "alert", "module": "netsoc", "severity": achado["severidade"]},
            "rule": {"id": achado["regra"], "name": achado["titulo"]},
            "threat": {"framework": "MITRE ATT&CK",
                       "technique": {"id": achado["tecnica"], "name": achado["tecnica_nome"]}},
            "netsoc": {"alvo": achado["alvo"], "descricao": achado["descricao"],
                       "evidencia": achado["evidencia"]},
        }
        with self._trava, self.log_eventos.open("a", encoding="utf-8") as f:
            f.write(json.dumps(evento, ensure_ascii=False) + "\n")

    # ---------------------------------------------------------- métricas
    def salvar_metricas(self, metricas: dict, pontuacao: float | None = None) -> None:
        with self._trava, self._con:
            self._con.execute("INSERT INTO metricas (momento, dados, pontuacao) VALUES (?,?,?)",
                              (metricas["momento"], json.dumps(metricas), pontuacao))
            self._con.execute("DELETE FROM metricas WHERE id <= "
                              "(SELECT MAX(id) - 5000 FROM metricas)")

    def ultimas_metricas(self, limite: int = 120) -> list[dict]:
        linhas = self._con.execute(
            "SELECT dados, pontuacao FROM metricas ORDER BY id DESC LIMIT ?", (limite,)).fetchall()
        return [json.loads(r["dados"]) | {"pontuacao": r["pontuacao"]} for r in reversed(linhas)]

    def limpar(self) -> None:
        with self._trava, self._con:
            for tabela in ("scans", "achados", "metricas", "meta"):
                self._con.execute(f"DELETE FROM {tabela}")  # noqa: S608
