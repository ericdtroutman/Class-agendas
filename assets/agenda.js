/* Shared renderer for every class agenda page.
   Each class page defines window.CLASS = { name, updated, units: [...], days: [...] }
   before loading this file. Nothing in here needs to change from week to week. */
(function () {
  const C = window.CLASS;
  const PALETTE = ["#2f6fb3", "#8a4fb8", "#1f8a70", "#c0392b", "#b7791f", "#2b6cb0", "#6b46c1", "#2f855a"];
  const unitColor = {};
  C.units.forEach((u, i) => { unitColor[u] = PALETTE[i % PALETTE.length]; });

  function todayISO() {
    const p = new Intl.DateTimeFormat("en-CA", { timeZone: "America/New_York", year: "numeric", month: "2-digit", day: "2-digit" }).formatToParts(new Date());
    const get = t => p.find(x => x.type === t).value;
    return `${get("year")}-${get("month")}-${get("day")}`;
  }
  function parse(iso) { const [y, m, d] = iso.split("-").map(Number); return new Date(y, m - 1, d); }
  function fmt(iso, opts) { return parse(iso).toLocaleDateString("en-US", opts); }
  function weekBounds(iso) {
    const d = parse(iso); let dow = d.getDay();
    if (dow === 6) d.setDate(d.getDate() + 2); else if (dow === 0) d.setDate(d.getDate() + 1);
    dow = d.getDay();
    const mon = new Date(d); mon.setDate(d.getDate() - (dow - 1));
    const fri = new Date(mon); fri.setDate(mon.getDate() + 4);
    return [mon, fri];
  }
  function esc(s) { const el = document.createElement("span"); el.textContent = s; return el.innerHTML; }
  function safeUrl(u) { return /^https?:\/\//i.test(u) ? u : "#"; }

  function dayHTML(e, today) {
    const cls = ["day"];
    if (e.off) cls.push("off");
    if (e.date === today) cls.push("is-today");
    let body = `<p class="title">${esc(e.title)}</p>`;
    if (e.did && e.did.length) body += `<ul>${e.did.map(x => `<li>${esc(x)}</li>`).join("")}</ul>`;
    if (e.mats && e.mats.length) {
      body += `<div class="mats"><b>Materials:</b> ${e.mats.map(m => {
        // Canvas items open in the Canvas tab itself (the page is embedded there); other sites open a new tab
        if (m.canvas && C.canvasCourse) return `<a class="canvas-link" href="${esc(safeUrl(C.canvasCourse + "/" + m.canvas))}" target="_top">${esc(m.name)}</a>`;
        if (m.url) return `<a href="${esc(safeUrl(m.url))}" target="_blank" rel="noopener">${esc(m.name)}</a>`;
        return esc(m.name);
      }).join(" · ")}</div>`;
    }
    if (e.missed) body += `<div class="missed"><b>If you missed it:</b> ${esc(e.missed)}</div>`;
    return `<div class="${cls.join(" ")}" style="--unit:${unitColor[e.unit] || "#5d6779"}">
      <div class="date"><span class="dow">${fmt(e.date, { weekday: "short" })}</span>${fmt(e.date, { month: "numeric", day: "numeric" })}
        ${e.date === today ? '<br><span class="badge">TODAY</span>' : ""}</div>
      <div>${body}</div></div>`;
  }

  let mode = "week", offset = 0; // offset = weeks away from the current week

  function weekRange(today, off) {
    const [mon, fri] = weekBounds(today);
    mon.setDate(mon.getDate() + off * 7); fri.setDate(fri.getDate() + off * 7);
    return [mon, fri];
  }
  function render() {
    const today = todayISO();
    let rows = C.days.slice().sort((a, b) => a.date.localeCompare(b.date));
    const nav = document.getElementById("weeknav");
    if (mode === "week") {
      const [mon, fri] = weekRange(today, offset);
      rows = rows.filter(e => { const d = parse(e.date); return d >= mon && d <= fri; });
      const f = d => d.toLocaleDateString("en-US", { month: "short", day: "numeric" });
      const hasBefore = C.days.some(x => parse(x.date) < mon), hasAfter = C.days.some(x => parse(x.date) > fri);
      nav.style.display = "";
      nav.innerHTML = `<button class="navbtn" id="prevwk" aria-label="Previous week" ${hasBefore ? "" : "disabled"}>&#9664;</button>
        <span class="range">${offset === 0 ? "This week · " : ""}${f(mon)} to ${f(fri)}</span>
        <button class="navbtn" id="nextwk" aria-label="Next week" ${hasAfter ? "" : "disabled"}>&#9654;</button>
        ${offset !== 0 ? '<button class="navbtn back" id="thiswk">Back to this week</button>' : ""}`;
      nav.querySelector("#prevwk").onclick = () => { offset--; render(); };
      nav.querySelector("#nextwk").onclick = () => { offset++; render(); };
      const tw = nav.querySelector("#thiswk"); if (tw) tw.onclick = () => { offset = 0; render(); };
    } else {
      nav.style.display = "none"; nav.innerHTML = "";
    }
    const list = document.getElementById("list");
    if (!rows.length) { list.innerHTML = '<p class="empty">Nothing posted for this week.</p>'; return; }
    let html = "", lastUnit = null;
    for (const e of rows) {
      if (e.unit !== lastUnit) {
        html += `<div class="unit-head"><span class="dot" style="background:${unitColor[e.unit] || "#5d6779"}"></span>${esc(e.unit)}</div>`;
        lastUnit = e.unit;
      }
      html += dayHTML(e, today);
    }
    list.innerHTML = html;
  }

  function renderToday() {
    const today = todayISO();
    const card = document.getElementById("today");
    const days = C.days.slice().sort((a, b) => a.date.localeCompare(b.date));
    let e = days.find(x => x.date === today && !x.off), label = "Today";
    if (!e) { e = days.find(x => x.date > today && !x.off); label = "Next class"; }
    if (!e) { card.style.display = "none"; return; }
    card.innerHTML = `<div class="label">${label} · ${fmt(e.date, { weekday: "long", month: "long", day: "numeric" })}</div>
      <h2>${esc(e.title)}</h2>${e.did ? `<div>${e.did.map(esc).join(" ")}</div>` : ""}`;
  }

  document.title = C.name + " Daily Agenda";
  document.getElementById("heading").textContent = C.name + ": What We Did Each Day";
  const chips = document.getElementById("chips");
  const filters = [["week", "This week"], ["all", "Everything"]];
  chips.innerHTML = filters.map(([f, label], i) =>
    `<button class="chip" data-filter="${esc(f)}" aria-pressed="${i === 0}">${esc(label)}</button>`).join("");
  chips.querySelectorAll(".chip").forEach(btn => btn.addEventListener("click", () => {
    chips.querySelectorAll(".chip").forEach(b => b.setAttribute("aria-pressed", String(b === btn)));
    mode = btn.dataset.filter; offset = 0;
    render();
  }));
  document.getElementById("updated").textContent = fmt(C.updated, { month: "long", day: "numeric", year: "numeric" });
  renderToday();
  render();
})();
