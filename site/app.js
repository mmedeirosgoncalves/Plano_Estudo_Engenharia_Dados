(async function () {
  const $ = (id) => document.getElementById(id);
  const fmt = new Intl.DateTimeFormat("pt-BR", { day: "2-digit", month: "2-digit" });

  const [plan, progress] = await Promise.all([
    fetch("data/plan.json").then((r) => r.json()),
    fetch("data/progress.json").then((r) => r.json()).catch(() => ({ days: {} })),
  ]);

  const STORAGE_KEY = "plano-estudo-inicio";
  let startDate = readStart();

  function readStart() {
    let value = plan.start_date;
    try { value = localStorage.getItem(STORAGE_KEY) || value; } catch (_) {}
    return value ? new Date(value + "T00:00:00") : null;
  }

  function stateOf(day) {
    if (day.rest) return "rest";
    return (progress.days[String(day.day)] || {}).state || "todo";
  }

  function dateOf(day) {
    if (!startDate) return null;
    const d = new Date(startDate);
    d.setDate(d.getDate() + day.day - 1);
    return d;
  }

  function todayNumber() {
    if (!startDate) return null;
    const ms = new Date().setHours(0, 0, 0, 0) - startDate.getTime();
    const n = Math.floor(ms / 86400000) + 1;
    return n >= 1 && n <= plan.days.length ? n : null;
  }

  function el(tag, attrs = {}, children = []) {
    const node = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs)) {
      if (k === "class") node.className = v;
      else if (k === "text") node.textContent = v;
      else node.setAttribute(k, v);
    }
    for (const c of [].concat(children)) if (c) node.append(c);
    return node;
  }

  function renderSummary() {
    const study = plan.days.filter((d) => !d.rest);
    const done = study.filter((d) => stateOf(d) === "done").length;
    const pct = Math.round((done / study.length) * 100);
    $("title").textContent = plan.title;
    $("done-count").textContent = done;
    $("total-count").textContent = study.length;
    $("pct").textContent = pct + "%";
    $("ring").style.setProperty("--p", pct);

    const today = todayNumber();
    const expected = today ? study.filter((d) => d.day <= today).length : null;
    let line = "Defina a data de início para ver em que dia você deveria estar.";
    if (today) {
      const diff = done - expected;
      const pace = diff >= 0 ? (diff === 0 ? "no ritmo" : `${diff} dia(s) adiantado`) : `${-diff} dia(s) atrasado`;
      line = `Hoje é o dia ${today} do plano — você está ${pace}.`;
    } else if (startDate) {
      line = new Date() < startDate ? "O plano ainda não começou." : "Período do plano encerrado.";
    }
    $("today-line").textContent = line;
    if (startDate) $("start-input").value = startDate.toISOString().slice(0, 10);
  }

  function renderPhases() {
    const box = $("phases");
    box.replaceChildren();
    for (const phase of plan.phases) {
      const days = plan.days.filter((d) => d.phase === phase.id && !d.rest);
      const done = days.filter((d) => stateOf(d) === "done").length;
      const pct = days.length ? (done / days.length) * 100 : 0;
      const bar = el("div", { class: "bar" }, el("i"));
      bar.firstChild.style.width = pct + "%";
      box.append(el("article", { class: "phase" }, [
        el("h3", { text: `Fase ${phase.id} · ${phase.name}` }),
        el("p", { text: `Dias ${phase.days[0]}–${phase.days[1]} · ${phase.result}` }),
        bar,
        el("div", { class: "count", text: `${done}/${days.length} dias` }),
      ]));
    }
  }

  let selected = null;

  function renderCalendar() {
    const cal = $("calendar");
    cal.replaceChildren();
    const today = todayNumber();
    for (const day of plan.days) {
      const date = dateOf(day);
      const classes = [stateOf(day)];
      if (day.day === today) classes.push("today");
      if (day.day === selected) classes.push("selected");
      const btn = el("button", { type: "button", "aria-label": `Dia ${day.day}: ${day.title}` }, [
        el("span", { class: "n", text: `Dia ${day.day}` }),
        el("span", { class: "t", text: day.title }),
        date ? el("span", { class: "d", text: fmt.format(date) }) : null,
      ]);
      btn.addEventListener("click", () => { selected = day.day; renderCalendar(); renderDetail(day); });
      cal.append(el("li", { class: classes.join(" ") }, btn));
    }
  }

  function renderDetail(day, scroll = true) {
    const box = $("detail");
    const state = stateOf(day);
    const labels = { done: "Concluído", doing: "Estudando", todo: "A fazer", rest: "Descanso" };
    const info = progress.days[String(day.day)];
    const phase = plan.phases.find((p) => p.id === day.phase);
    const date = dateOf(day);

    const parts = [
      el("span", { class: `status ${state}`, text: labels[state] }),
      el("h3", { text: `Dia ${day.day} · ${day.title}` }),
      el("p", { class: "muted", text: `Fase ${phase.id} – ${phase.name}${date ? " · " + fmt.format(date) : ""}` }),
    ];
    if (day.rest) {
      parts.push(el("p", { text: "Dia livre. Se quiser, revise as anotações da semana por 30 minutos." }));
    } else {
      parts.push(el("h4", { text: "Estudo" }), el("ul", {}, day.study.map((s) => el("li", { text: s }))));
      if (day.evidence) parts.push(el("h4", { text: "Evidência do dia" }), el("p", { text: day.evidence }));
      if (day.project) parts.push(el("h4", { text: "Projeto final" }), el("p", { text: day.project }));
      if (day.links.length) {
        parts.push(el("h4", { text: "Materiais" }), el("ul", {}, day.links.map((l) =>
          el("li", {}, el("a", { href: l.url, target: "_blank", rel: "noopener", text: l.title })))));
      }
      if (info && info.url) {
        parts.push(el("div", { class: "actions" },
          el("a", { class: "btn", href: info.url, target: "_blank", rel: "noopener",
                    text: state === "done" ? "Ver issue" : "Abrir issue para marcar" })));
      }
    }
    box.replaceChildren(...parts);
    if (scroll) box.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }

  $("start-input").addEventListener("change", (e) => {
    try { localStorage.setItem(STORAGE_KEY, e.target.value); } catch (_) {}
    startDate = e.target.value ? new Date(e.target.value + "T00:00:00") : null;
    renderAll();
  });

  function renderAll() {
    renderSummary();
    renderPhases();
    renderCalendar();
  }

  renderAll();
  const first = plan.days.find((d) => d.day === todayNumber())
    || plan.days.find((d) => !d.rest && stateOf(d) !== "done") || plan.days[0];
  selected = first.day;
  renderCalendar();
  renderDetail(first, false);

  const when = progress.generated_at ? new Date(progress.generated_at).toLocaleString("pt-BR") : "nunca";
  $("footer").textContent = `Progresso sincronizado das issues do GitHub em ${when}.`;
})();
