/* Painel NetSOC: lê a API JSON a cada 5 s e desenha tabelas e gráficos.
   Todo texto vindo da API é inserido com textContent (sem innerHTML) para evitar XSS. */
(function () {
  "use strict";
  const DEMO = document.body.dataset.demo === "sim";
  const $ = (id) => document.getElementById(id);
  const ROTULO_SEV = { alto: "Alto", medio: "Médio", baixo: "Baixo", info: "Info" };
  const RISCO_PORTA = { 21: "alto", 23: "alto", 445: "alto", 1433: "alto", 2375: "alto", 3306: "alto", 3389: "alto",
    5432: "alto", 5900: "alto", 6379: "alto", 27017: "alto", 110: "medio", 135: "medio", 139: "medio", 143: "medio",
    554: "medio", 1883: "medio" };
  let filtroSev = "";
  let achadosCache = [];

  function el(tag, attrs = {}, ...filhos) {
    const e = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs)) {
      if (k === "class") e.className = v; else if (k === "text") e.textContent = v; else e.setAttribute(k, v);
    }
    filhos.flat().forEach((f) => f != null && e.append(f instanceof Node ? f : document.createTextNode(String(f))));
    return e;
  }
  const hora = (iso) => (iso ? new Date(iso).toLocaleString("pt-BR", { dateStyle: "short", timeStyle: "short" }) : "—");

  async function api(url, opcoes) {
    const r = await fetch(url, { credentials: "same-origin", ...opcoes });
    const dados = await r.json().catch(() => ({}));
    if (!r.ok) throw new Error(dados.erro || `Erro ${r.status}`);
    return dados;
  }

  // ---------------------------------------------------------------- gráficos
  Chart.defaults.color = "#8a9bb5";
  Chart.defaults.borderColor = "#1e2a40";
  Chart.defaults.font.family = "Inter, system-ui, sans-serif";
  Chart.defaults.plugins.legend.labels.usePointStyle = true;
  Chart.defaults.plugins.legend.labels.boxWidth = 8;

  const gHost = new Chart($("grafico-host"), {
    type: "line",
    data: { labels: [], datasets: [
      { label: "CPU %", data: [], borderColor: "#60a5fa", backgroundColor: "rgba(96,165,250,.12)", fill: true, tension: .3, borderWidth: 2, pointRadius: [] , pointBackgroundColor: "#f87171" },
      { label: "Memória %", data: [], borderColor: "#a78bfa", tension: .3, borderWidth: 2, pointRadius: 0 },
      { label: "Conexões externas", data: [], borderColor: "#34d399", tension: .3, borderWidth: 2, pointRadius: 0, yAxisID: "y2" },
    ] },
    options: {
      maintainAspectRatio: false, animation: false, interaction: { mode: "index", intersect: false },
      scales: {
        x: { ticks: { maxTicksLimit: 8 }, grid: { display: false } },
        y: { min: 0, max: 100, title: { display: true, text: "%" } },
        y2: { position: "right", beginAtZero: true, grid: { display: false }, title: { display: true, text: "conexões" } },
      },
      plugins: { legend: { position: "top", align: "end" } },
    },
  });

  const gSev = new Chart($("grafico-severidade"), {
    type: "doughnut",
    data: { labels: ["Alto", "Médio", "Baixo"], datasets: [{ data: [0, 0, 0], backgroundColor: ["#f87171", "#fbbf24", "#60a5fa"], borderWidth: 0 }] },
    options: { maintainAspectRatio: false, cutout: "68%", plugins: { legend: { position: "bottom" } } },
  });

  // ---------------------------------------------------------------- atualização
  async function atualizarResumo() {
    const r = await api("/api/resumo");
    $("host-nome").textContent = DEMO ? `Demonstração · ${r.host.hostname}` : `${r.host.hostname} · ${r.host.ip}`;
    if (r.ultimo_scan) {
      $("kpi-ativos").textContent = r.ultimo_scan.ativos;
      $("kpi-ativos-extra").textContent = `${r.ultimo_scan.alvo} · ${hora(r.ultimo_scan.inicio)}`;
    }
    $("kpi-risco").textContent = r.ultimo_scan ? r.portas_risco : "—";
    $("kpi-achados").textContent = r.total_achados;
    $("kpi-achados-extra").textContent = `${r.achados.alto} alto · ${r.achados.medio} médio · ${r.achados.baixo} baixo`;
    $("kpi-modelo").textContent = r.modelo.pronto ? "Ativo" : "Aprendendo";
    $("kpi-modelo-extra").textContent = r.modelo.pronto
      ? `treinado com ${r.modelo.amostras} amostras deste host`
      : `coletando linha de base (${r.modelo.amostras}/30 amostras)`;
    gSev.data.datasets[0].data = [r.achados.alto, r.achados.medio, r.achados.baixo];
    gSev.update();
    mostrarStatusScan(r.scan_em_andamento);
  }

  let ultimoEstadoScan = null;
  function mostrarStatusScan(s) {
    const box = $("status-scan");
    if (!s) { box.hidden = true; return; }
    box.hidden = false;
    box.className = "status-scan" + (s.estado === "erro" ? " erro" : s.estado === "concluido" ? " ok" : "");
    box.replaceChildren();
    if (s.estado === "rodando") {
      box.append(el("span", { class: "spinner-border spinner-border-sm" }), `Varrendo ${s.alvo}… isso leva de 10 s a 1 min.`);
    } else if (s.estado === "concluido") {
      box.append(el("i", { class: "bi bi-check-circle" }), `Scan de ${s.alvo} concluído em ${s.duracao_s} s: ${s.ativos} ativo(s), ${s.achados_novos} achado(s) novo(s).`);
    } else {
      box.append(el("i", { class: "bi bi-x-circle" }), `Falha no scan: ${s.erro}`);
    }
    $("btn-scan").disabled = DEMO || s.estado === "rodando";
    if (ultimoEstadoScan === "rodando" && s.estado !== "rodando") { atualizarAtivos(); atualizarAchados(); }
    ultimoEstadoScan = s.estado;
  }

  async function atualizarMetricas() {
    const { metricas } = await api("/api/metricas?n=120");
    gHost.data.labels = metricas.map((m) => m.momento.slice(11, 19));
    gHost.data.datasets[0].data = metricas.map((m) => m.cpu);
    gHost.data.datasets[0].pointRadius = metricas.map((m) => (m.pontuacao !== null && m.pontuacao < 0 ? 4 : 0));
    gHost.data.datasets[1].data = metricas.map((m) => m.memoria);
    gHost.data.datasets[2].data = metricas.map((m) => m.conexoes_externas);
    gHost.update();
  }

  function renderAchados() {
    const corpo = $("tbody-achados");
    const lista = achadosCache.filter((a) => !filtroSev || a.severidade === filtroSev);
    corpo.replaceChildren();
    if (!lista.length) {
      corpo.append(el("tr", {}, el("td", { colspan: 6, class: "vazio", text: achadosCache.length ? "Nenhum achado com esse filtro." : "Nenhum achado até agora." })));
      return;
    }
    lista.forEach((a) => {
      const tecnica = a.tecnica
        ? el("a", { class: "tecnica", href: `https://attack.mitre.org/techniques/${a.tecnica.replace(".", "/")}/`, target: "_blank", rel: "noopener" }, `${a.tecnica} · ${a.tecnica_nome}`)
        : el("span", { class: "regra", text: "—" });
      corpo.append(el("tr", {},
        el("td", {}, el("span", { class: `sev sev-${a.severidade}`, text: ROTULO_SEV[a.severidade] })),
        el("td", { class: "regra", text: a.regra }),
        el("td", {}, el("div", { class: "fw-semibold", text: a.titulo }), el("div", { class: "desc", text: a.descricao })),
        el("td", { class: "mono", text: a.alvo }),
        el("td", {}, tecnica),
        el("td", { class: "regra" }, hora(a.ultimo), a.ocorrencias > 1 ? el("div", { text: `${a.ocorrencias}×` }) : null),
      ));
    });
  }

  async function atualizarAchados() {
    achadosCache = (await api("/api/achados")).achados;
    renderAchados();
  }

  async function atualizarAtivos() {
    const { scan, historico } = await api("/api/ativos");
    const corpo = $("tbody-ativos");
    if (!scan) return;
    const anterior = historico.find((h) => h.alvo === scan.alvo && h.id < scan.id);
    $("sub-inventario").textContent = `${scan.alvo} · ${scan.hosts_testados} endereços testados em ${scan.duracao_s} s · ${historico.length} scan(s) no histórico`;
    const novos = new Set(achadosCache.filter((a) => a.regra === "NET-002").map((a) => a.alvo));
    corpo.replaceChildren();
    if (!scan.ativos.length) {
      corpo.append(el("tr", {}, el("td", { colspan: 5, class: "vazio", text: "Nenhum host respondeu nessa rede." })));
      return;
    }
    scan.ativos.forEach((a) => {
      const portas = a.portas.length
        ? a.portas.map((p) => el("span", { class: `porta ${RISCO_PORTA[p.porta] ? "risco-" + RISCO_PORTA[p.porta] : ""}`, title: p.banner || p.servico }, `${p.porta}/${p.servico}`))
        : [el("span", { class: "regra", text: "nenhuma das portas testadas" })];
      corpo.append(el("tr", {},
        el("td", { class: "mono fw-semibold" }, a.ip, anterior && novos.has(a.ip) ? el("span", { class: "novo", text: "NOVO" }) : null),
        el("td", { text: a.hostname || "—" }),
        el("td", { text: a.tipo }),
        el("td", {}, portas),
        el("td", { class: "text-end regra", text: a.latencia_ms != null ? `${a.latencia_ms} ms` : "—" }),
      ));
    });
  }

  async function atualizarHost() {
    if (DEMO || !$("tbody-proc")) return;
    const h = await api("/api/host");
    const linhas = (id, itens, colunas) => {
      const c = $(id); c.replaceChildren();
      itens.forEach((i) => c.append(el("tr", {}, colunas.map(([f, cls]) => el("td", { class: cls || "", text: f(i) })))));
    };
    linhas("tbody-proc", h.processos, [[(p) => p.nome], [(p) => p.pid, "regra"], [(p) => `${p.cpu}%`, "text-end"], [(p) => `${p.memoria}%`, "text-end"]]);
    linhas("tbody-escuta", h.escuta, [[(p) => p.porta, "mono"], [(p) => p.endereco, "mono regra"], [(p) => p.processo]]);
    linhas("tbody-conexoes", h.conexoes, [[(c) => c.processo], [(c) => `${c.remoto_ip}:${c.remoto_porta}`, "mono regra"]]);
  }

  // ---------------------------------------------------------------- eventos
  $("filtro-sev").addEventListener("click", (e) => {
    const b = e.target.closest("button[data-sev]");
    if (!b) return;
    filtroSev = b.dataset.sev;
    $("filtro-sev").querySelectorAll("button").forEach((x) => x.classList.toggle("active", x === b));
    renderAchados();
  });

  $("form-scan").addEventListener("submit", async (e) => {
    e.preventDefault();
    if (DEMO) return;
    try {
      await api("/api/scan", { method: "POST", headers: { "Content-Type": "application/json", "X-NetSOC": "1" },
        body: JSON.stringify({ alvo: $("alvo").value }) });
      atualizarResumo();
    } catch (erro) {
      mostrarStatusScan({ estado: "erro", erro: erro.message, alvo: $("alvo").value });
    }
  });

  async function tudo() {
    try {
      await atualizarResumo();
      await Promise.all([atualizarMetricas(), atualizarAchados().then(atualizarAtivos), atualizarHost()]);
    } catch (erro) { console.error(erro); }
  }
  tudo();
  setInterval(() => { atualizarResumo().catch(() => {}); atualizarMetricas().catch(() => {}); atualizarHost().catch(() => {}); }, 5000);
  setInterval(() => { atualizarAchados().catch(() => {}); }, 15000);
})();
