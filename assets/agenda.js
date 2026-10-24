/* Seasonal look for the whole page. Follows the same Decor Calendar as the daily slides:
   the theme switches on its own on the first school day of each row.
   To check an upcoming theme, add ?date=2026-11-30 to the page address. */
(function () {
  const q = new URLSearchParams(location.search);
  const forced = /^\d{4}-\d{2}-\d{2}$/.test(q.get("date") || "") ? q.get("date") : null;
  if (forced) window.AGENDA_DATE = forced;
  const p = new Intl.DateTimeFormat("en-CA", { timeZone: "America/New_York", year: "numeric", month: "2-digit", day: "2-digit" }).formatToParts(new Date());
  const get = t => p.find(x => x.type === t).value;
  const today = forced || `${get("year")}-${get("month")}-${get("day")}`;

  // ---- looks. a/b: banner gradient, ink: banner text, acc: accent, soft: today tint,
  //      pg: page gradient, pink: text sitting on the page, card: card color,
  //      font: heading font, h1: title font, fall: what drifts down, ground: bottom scene
  const FALLFONT = "Grandstander", COOL = "Fredoka";
  const L = {
    gold:       { a: "#f7d58e", b: "#e59a4f", ink: "#3b2412", acc: "#c46a1a", soft: "#fff4e3", pg: ["#fdf3e1", "#f6dcb4"], pink: "#4a3220", card: "#fffdf8", font: FALLFONT, fall: "leaf", ground: "leaves" },
    autumn:     { a: "#f2a35a", b: "#b8492a", ink: "#fff", acc: "#c0521f", soft: "#fff0e5", pg: ["#fbe6d0", "#efc39c"], pink: "#4a2a18", card: "#fffaf4", font: FALLFONT, fall: "leaf", ground: "leaves" },
    spooky:     { a: "#2b1742", b: "#e07a2c", ink: "#fff", acc: "#d4651c", soft: "#fff1e6", pg: ["#1c1030", "#3b1f50"], pink: "#f3e9ff", card: "#fffaf5", font: FALLFONT, h1: "Creepster", fall: "leaf", ground: "pumpkins", dark: true },
    rainy:      { a: "#6f6258", b: "#a77b55", ink: "#fff", acc: "#a65a2b", soft: "#fbf1e8", pg: ["#ece6e0", "#d3c8bd"], pink: "#3d3128", card: "#fffdfb", font: FALLFONT, fall: "rain", ground: "leaves" },
    fallnight:  { a: "#141d38", b: "#3a3f6e", ink: "#fff", acc: "#c0521f", soft: "#fff0e5", pg: ["#111933", "#2b3060"], pink: "#eef0ff", card: "#fffaf4", font: FALLFONT, fall: null, ground: "hills", dark: true },
    harvest:    { a: "#efc36a", b: "#b0602a", ink: "#3b2412", acc: "#b0602a", soft: "#fff3e2", pg: ["#fbeacb", "#efcd94"], pink: "#4a3220", card: "#fffaf2", font: FALLFONT, fall: "leaf", ground: "pumpkins" },
    snow:       { a: "#dcebf7", b: "#8fb3d9", ink: "#15324d", acc: "#2f6fb3", soft: "#eef5fc", pg: ["#eaf2fb", "#c9dcf0"], pink: "#15324d", card: "#ffffff", font: COOL, fall: "snow", ground: "snow" },
    winternight:{ a: "#0f1c36", b: "#2c4f7c", ink: "#fff", acc: "#2f6fb3", soft: "#eef5fc", pg: ["#0d1830", "#22406a"], pink: "#eaf2ff", card: "#ffffff", font: COOL, fall: "snow", ground: "snow", dark: true },
    rosy:       { a: "#f9d4dc", b: "#e0849b", ink: "#4a1a2a", acc: "#c2416b", soft: "#fdeef2", pg: ["#fdf0f3", "#f6d2dc"], pink: "#4a1a2a", card: "#fffdfd", font: COOL, fall: "heart", ground: "snow" },
    clover:     { a: "#cfead0", b: "#4f9a5b", ink: "#13361c", acc: "#2f855a", soft: "#ebf7ee", pg: ["#eff8ef", "#cfe8d1"], pink: "#173d20", card: "#fdfffd", font: COOL, fall: "rain", ground: "grass" },
    sunrise:    { a: "#fde2b8", b: "#8fcb9b", ink: "#1f3a24", acc: "#2f855a", soft: "#ebf7ee", pg: ["#fff3e0", "#dcefd9"], pink: "#1f3a24", card: "#fffffd", font: COOL, fall: null, ground: "grass" },
    blossom:    { a: "#fde3ec", b: "#f2a7c3", ink: "#4a1a32", acc: "#b83b6b", soft: "#fdeef4", pg: ["#fff1f6", "#f8d3e2"], pink: "#4a1a32", card: "#fffdfe", font: COOL, fall: "blossom", ground: "grass" },
    springnight:{ a: "#16233f", b: "#3d5a80", ink: "#fff", acc: "#2f855a", soft: "#ebf7ee", pg: ["#121e38", "#2c4868"], pink: "#eef6ff", card: "#fdfffd", font: COOL, fall: null, ground: "grass", dark: true },
    sky:        { a: "#d4ecfb", b: "#7cc4ea", ink: "#123247", acc: "#2b7bb9", soft: "#ecf6fd", pg: ["#eff8fe", "#cde9f8"], pink: "#123247", card: "#ffffff", font: COOL, fall: null, ground: "grass" },
    summer:     { a: "#ffd57e", b: "#ff7f5c", ink: "#3d1d10", acc: "#d9632b", soft: "#fff1e8", pg: ["#fff4dc", "#ffdcbf"], pink: "#3d1d10", card: "#fffdfa", font: "Baloo 2", fall: null, ground: "beach" }
  };
  // ---- Decor Calendar 2026-27 (same rows as the slide guide)
  const ROWS = [
    ["2026-09-02", "Back to school",  "gold",        ["apple", "leaf", "pencil"]],
    ["2026-09-21", "Hello, fall",     "autumn",      ["leaf", "apple"]],
    ["2026-10-05", "Fall",            "autumn",      ["leaf", "pumpkin"]],
    ["2026-10-26", "Halloween week",  "spooky",      ["moon", "bat", "pumpkin", "star"]],
    ["2026-11-02", "November",        "rainy",       ["rain", "leaf"]],
    ["2026-11-16", "Leonid meteors",  "fallnight",   ["meteor", "star"]],
    ["2026-11-23", "Thanksgiving",    "harvest",     ["leaf", "pumpkin", "apple"]],
    ["2026-11-30", "Winter",          "snow",        ["snow"]],
    ["2026-12-14", "Geminid meteors", "winternight", ["lights", "snow", "meteor", "star"]],
    ["2027-01-04", "New year",        "snow",        ["snow", "star"]],
    ["2027-01-19", "Winter",          "winternight", ["star", "moon", "snow"]],
    ["2027-02-01", "February",        "rosy",        ["heart", "snow"]],
    ["2027-02-22", "Winter",          "snow",        ["snow"]],
    ["2027-03-08", "Spring",          "clover",      ["clover", "rain"]],
    ["2027-03-22", "Spring",          "sunrise",     ["sun", "sprout"]],
    ["2027-04-05", "Spring",          "blossom",     ["blossom"]],
    ["2027-04-19", "Lyrid meteors",   "springnight", ["meteor", "star", "blossom"]],
    ["2027-05-03", "Spring",          "springnight", ["meteor", "star"]],
    ["2027-05-17", "Spring",          "sky",         ["sun", "cloud", "sprout"]],
    ["2027-06-07", "Summer",          "summer",      ["sun", "wave"]]
  ];
  let row = null;
  for (const r of ROWS) if (r[0] <= today) row = r;
  if (!row) return; // summer break before 9/2: plain look
  const [, label, key, motifs] = row;
  const T = L[key];

  // ---- little pictures, drawn around (0,0)
  const SH = {
    leaf: c => `<path d="M0,-14C9,-8 10,6 0,14C-10,6-9,-8 0,-14Z" fill="${c || "#e8743b"}"/><path d="M0,-11V17" stroke="rgba(0,0,0,.25)" stroke-width="1.4" fill="none"/>`,
    apple: () => `<circle cx="-5" cy="2" r="9" fill="#d23a2f"/><circle cx="5" cy="2" r="9" fill="#d23a2f"/><path d="M0,-6V-13" stroke="#5b3a1e" stroke-width="2"/><path d="M1,-11C6,-16 11,-13 11,-11C7,-9 3,-9 1,-11Z" fill="#4f9a3b"/>`,
    pencil: () => `<g transform="rotate(-35)"><rect x="-18" y="-4" width="28" height="8" fill="#f3b72f"/><rect x="-22" y="-4" width="4" height="8" fill="#e58aa0"/><path d="M10,-4L18,0L10,4Z" fill="#f1d3a6"/><path d="M15,-1.5L18,0L15,1.5Z" fill="#333"/></g>`,
    pumpkin: () => `<ellipse cx="-6" cy="2" rx="8" ry="10" fill="#e07020"/><ellipse cx="6" cy="2" rx="8" ry="10" fill="#e07020"/><ellipse cx="0" cy="2" rx="7" ry="11" fill="#f28a2e"/><path d="M0,-8C0,-12 2,-14 4,-15" stroke="#4d6b2a" stroke-width="3" fill="none" stroke-linecap="round"/>`,
    jack: () => `<circle class="flicker" r="17" fill="#ffb347" opacity=".35"/>${SH.pumpkin()}<path d="M-7,-2L-3,-5L-3,0ZM7,-2L3,-5L3,0Z" fill="#3a1a05"/><path d="M-7,4Q0,10 7,4L4,6L2,4L0,7L-2,4L-4,6Z" fill="#3a1a05"/>`,
    bat: c => `<path d="M0,0C-4,-6-10,-6-15,-2C-11,-1-9,2-8,5C-6,2-3,2-2,4L0,1L2,4C3,2 6,2 8,5C9,2 11,-1 15,-2C10,-6 4,-6 0,0Z" fill="${c || "#1a0f26"}"/>`,
    moon: () => `<circle class="halo" r="30" fill="#ffd98a" opacity=".25"/><circle r="22" fill="#ffe6a8"/><circle cx="-7" cy="-5" r="4" fill="#f4cf84"/><circle cx="6" cy="7" r="3" fill="#f4cf84"/>`,
    star: c => `<path d="M0,-5L1.4,-1.4L5,0L1.4,1.4L0,5L-1.4,1.4L-5,0L-1.4,-1.4Z" fill="${c || "#fff8d6"}"/>`,
    meteor: () => `<path d="M0,0L-46,-22" stroke="url(#trail)" stroke-width="3" stroke-linecap="round"/><circle r="2.6" fill="#fff"/>`,
    rain: c => `<path d="M0,-8C4,-2 5,2 0,6C-5,2-4,-2 0,-8Z" fill="${c || "#dbe8f2"}"/>`,
    snow: c => `<g stroke="${c || "#fff"}" stroke-width="2" stroke-linecap="round" fill="none">${[0, 60, 120].map(a => `<path d="M0,-10V10M-3,-7L0,-10L3,-7M-3,7L0,10L3,7" transform="rotate(${a})"/>`).join("")}</g>`,
    lights: () => `<path d="M-60,-6Q0,22 60,-6" stroke="#2c3a2c" stroke-width="1.5" fill="none"/>${[["#ff6b6b", -44, 4], ["#ffd93d", -22, 10], ["#6bcb77", 0, 12], ["#4d96ff", 22, 10], ["#ff6b6b", 44, 4]].map(([c, x, y], i) => `<g class="bulb" style="animation-delay:-${(i * 0.7).toFixed(1)}s"><ellipse cx="${x}" cy="${y + 4}" rx="3.2" ry="4.5" fill="${c}"/><circle cx="${x}" cy="${y + 4}" r="8" fill="${c}" opacity=".3"/></g>`).join("")}`,
    heart: c => `<path d="M0,7C-13,-2-9,-13 0,-6C9,-13 13,-2 0,7Z" fill="${c || "#e8738f"}"/>`,
    clover: () => `<g fill="#3f8f4a">${[0, 120, 240].map(a => `<path d="M0,0C-9,-6-7,-14 0,-10C7,-14 9,-6 0,0Z" transform="rotate(${a})"/>`).join("")}</g><path d="M0,0Q4,8 2,14" stroke="#3f8f4a" stroke-width="2" fill="none"/>`,
    blossom: () => `<g fill="#f7b6cf">${[0, 72, 144, 216, 288].map(a => `<ellipse cy="-6" rx="4.5" ry="6" transform="rotate(${a})"/>`).join("")}</g><circle r="3" fill="#f6d66b"/>`,
    sprout: () => `<path d="M0,12V-2" stroke="#3f8f4a" stroke-width="2.4"/><path d="M0,0C-12,-2-12,-12-2,-10Z" fill="#5fae5a"/><path d="M0,-3C10,-6 12,-14 2,-13Z" fill="#76c06b"/>`,
    sun: () => `<circle class="halo" r="34" fill="#fff3b0" opacity=".35"/><circle r="20" fill="#ffd34d"/>`,
    cloud: () => `<g fill="#fff" opacity=".9"><circle cx="-10" r="9"/><circle cx="2" cy="-5" r="11"/><circle cx="13" r="8"/><rect x="-19" y="0" width="40" height="8" rx="4"/></g>`,
    wave: () => `<path d="M-30,0Q-22,-8 -15,0T0,0T15,0T30,0" stroke="#fff" stroke-width="2.5" fill="none" opacity=".8"/>`,
    flower: c => `<path d="M0,14V0" stroke="#3f8f4a" stroke-width="2"/><g fill="${c || "#fff"}">${[0, 72, 144, 216, 288].map(a => `<circle cy="-4" r="3.2" transform="rotate(${a})"/>`).join("")}</g><circle r="2.4" fill="#f6c94b"/>`,
    tree: () => `<path d="M0,-26L14,0H6L18,16H-18L-6,0H-14Z" fill="#2f6b4a"/><rect x="-3" y="16" width="6" height="8" fill="#5b3a1e"/>`,
    shell: () => `<path d="M-9,4Q0,-14 9,4Z" fill="#f6b8a0"/><path d="M0,4V-8M-4,4L-2,-6M4,4L2,-6" stroke="#e08a6e" stroke-width="1"/>`
  };
  const LEAF = ["#e8743b", "#f2b134", "#b5452a", "#d9822b"];
  const svgUrl = s => `url("data:image/svg+xml,${encodeURIComponent(s)}")`;
  const one = (m, c, size = 40) => `<svg xmlns="http://www.w3.org/2000/svg" viewBox="-20 -20 40 40" width="${size}" height="${size}">${SH[m](c)}</svg>`;
  let seed = today.split("-").reduce((a, b) => a + +b, 0) * 7 + label.length;
  const rnd = () => { seed = (seed * 9301 + 49297) % 233280; return seed / 233280; };

  // ---- 1) banner art
  const HERO = { moon: [722, 52, 1], sun: [728, 40, 1], lights: [640, 18, 1.2] };
  let art = "";
  // each picture gets a gentle loop: m-<name> in agenda.css says how it moves
  const wrap = (m, inner, x, y) => {
    const d = (rnd() * 8).toFixed(1);
    if (m === "bat") return `<g transform="translate(${x},${y})"><g class="m m-batfly" style="animation-delay:-${d}s"><g class="m m-flap" style="animation-delay:-${(rnd()).toFixed(2)}s">${inner}</g></g></g>`;
    return `<g transform="translate(${x},${y})"><g class="m m-${m}" style="animation-delay:-${d}s">${inner}</g></g>`;
  };
  motifs.forEach(m => { if (HERO[m]) { const [x, y, s] = HERO[m]; art += wrap(m, `<g transform="scale(${s})">${SH[m]()}</g>`, x, y); } });
  const small = motifs.filter(m => !HERO[m]);
  const spots = [[575, 34], [612, 92], [650, 22], [668, 64], [700, 104], [742, 96], [790, 28], [598, 62], [765, 62], [632, 112], [800, 100], [712, 14]];
  spots.forEach(([x, y], i) => {
    const m = small[i % small.length]; if (!m) return;
    if (motifs.includes("moon") && Math.hypot(x - 722, y - 52) < 36) return;
    if (motifs.includes("sun") && Math.hypot(x - 728, y - 40) < 34) return;
    const s = (m === "star" ? 0.9 : 0.8) + rnd() * 0.5, r = Math.round(rnd() * 70 - 35);
    const c = m === "leaf" ? LEAF[i % 4] : m === "heart" ? ["#c2416b", "#fff", "#e8738f"][i % 3] : "";
    art += wrap(m, `<g transform="rotate(${m === "meteor" || m === "bat" ? 0 : r}) scale(${s.toFixed(2)})">${SH[m](c)}</g>`, x + Math.round(rnd() * 14 - 7), y);
  });
  const bannerSvg = `<svg class="season-art" viewBox="0 0 820 120" preserveAspectRatio="xMaxYMid slice" aria-hidden="true">
    <defs><linearGradient id="trail" x1="0" y1="0" x2="1" y2=".5"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset="1" stop-color="#fff" stop-opacity=".9"/></linearGradient></defs>${art}</svg>`;

  // ---- 2) faint wallpaper of little pictures behind the whole page
  const tileM = { moon: "star", sun: "sun", lights: "star", meteor: "star", cloud: "cloud", wave: "wave" };
  const tileList = [...new Set(motifs.map(m => tileM[m] || m))];
  const ink = T.dark ? "#ffffff" : T.pink;
  let tile = "";
  [[30, 34], [120, 18], [196, 70], [70, 112], [160, 150], [24, 190], [110, 210], [210, 200]].forEach(([x, y], i) => {
    const m = tileList[i % tileList.length];
    const c = m === "leaf" ? LEAF[i % 4] : (m === "snow" || m === "star" || m === "rain") ? ink : "";
    tile += `<g transform="translate(${x},${y}) rotate(${Math.round(rnd() * 60 - 30)}) scale(${(0.6 + rnd() * 0.4).toFixed(2)})">${SH[m](c)}</g>`;
  });
  const tileSvg = `<svg xmlns="http://www.w3.org/2000/svg" width="240" height="240" viewBox="0 0 240 240"><g opacity="${T.dark ? 0.16 : 0.13}">${tile}</g></svg>`;

  // ---- 3) ground scene at the bottom of the page
  const G = {
    leaves:   { fill: "#c9773d", top: "#e0954f", things: ["leaf", "leaf", "pumpkin", "leaf", "apple", "leaf"] },
    pumpkins: { fill: T.dark ? "#3a2250" : "#8a5a2e", top: T.dark ? "#55306e" : "#a8723c", things: ["jack", "leaf", "pumpkin", "jack", "leaf", "pumpkin"] },
    hills:    { fill: "#1b2348", top: "#2a3466", things: ["star", "star", "star"] },
    snow:     { fill: "#ffffff", top: "#e3eef9", things: ["tree", "snow", "tree", "tree", "snow"] },
    grass:    { fill: "#5fa85a", top: "#78bf6b", things: ["flower", "sprout", "flower", "flower", "sprout", "flower"] },
    beach:    { fill: "#f2d39a", top: "#7cc4ea", things: ["shell", "shell", "shell"] }
  }[T.ground];
  let gArt = "";
  const gPos = [70, 190, 300, 430, 545, 660, 760];
  gPos.forEach((x, i) => {
    const m = G.things[i % G.things.length];
    const c = m === "leaf" ? LEAF[i % 4] : m === "flower" ? ["#fff", "#f7b6cf", "#ffd34d"][i % 3] : m === "star" ? "#fff8d6" : m === "snow" ? "#cfe0f1" : "";
    const y = m === "star" ? 14 + (i % 3) * 10 : m === "tree" ? 46 : 62;
    gArt += `<g transform="translate(${x},${y})"><g class="m g-${m}" style="animation-delay:-${(i * 1.3).toFixed(1)}s"><g transform="scale(${m === "tree" ? 1.3 : 1.15})">${SH[m](c)}</g></g></g>`;
  });
  const groundSvg = `<svg class="season-ground-art" viewBox="0 0 820 100" preserveAspectRatio="xMidYMax slice" aria-hidden="true">
    ${T.ground === "beach" ? `<path d="M0,52Q100,40 205,52T410,52T615,52T820,52V100H0Z" fill="#7cc4ea"/>` : ""}
    <path d="M0,70Q120,52 240,66T480,64T820,62V100H0Z" fill="${G.top}"/>
    <path d="M0,78Q140,64 280,76T560,74T820,72V100H0Z" fill="${G.fill}"/>${gArt}</svg>`;

  // ---- apply
  const root = document.documentElement;
  const cornerM = motifs.includes("bat") ? "jack" : (small[0] || "star");
  const cornerC = cornerM === "leaf" ? "#e8743b" : (cornerM === "snow" || cornerM === "star") ? "#7fa7cf" : "";
  const v = { "--today": T.acc, "--today-soft": T.soft, "--band-a": T.a, "--band-b": T.b, "--band-ink": T.ink,
    "--pg1": T.pg[0], "--pg2": T.pg[1], "--page-ink": T.pink, "--card": T.card,
    "--head-font": `"${T.font}", system-ui, sans-serif`, "--h1-font": `"${T.h1 || T.font}", system-ui, sans-serif`,
    "--wallpaper": svgUrl(tileSvg), "--corner": svgUrl(one(cornerM, cornerC, 64)) };
  for (const k in v) root.style.setProperty(k, v[k]);
  root.dataset.season = key;
  if (T.dark) root.dataset.dark = "1";
  const fam = f => "family=" + f.replace(/ /g, "+") + (f === "Creepster" ? "" : ":wght@400;600;700");
  const link = document.createElement("link");
  link.rel = "stylesheet";
  link.href = "https://fonts.googleapis.com/css2?" + [...new Set([T.font, T.h1].filter(Boolean))].map(fam).join("&") + "&display=swap";
  document.head.appendChild(link);

  function build() {
    const h1 = document.getElementById("heading") || document.querySelector("h1");
    if (!h1 || document.querySelector(".season-band")) return;
    const sub = h1.nextElementSibling && h1.nextElementSibling.classList.contains("sub") ? h1.nextElementSibling : null;
    const band = document.createElement("header");
    band.className = "season-band";
    band.innerHTML = `<div class="season-glow"></div>` + bannerSvg + `<div class="season-text"><span class="season-tag">${label}</span></div>`;
    h1.parentNode.insertBefore(band, h1);
    const txt = band.querySelector(".season-text");
    txt.appendChild(h1); if (sub) txt.appendChild(sub);
    // ground scene at the very bottom
    const ground = document.createElement("div");
    ground.className = "season-ground"; ground.innerHTML = groundSvg;
    document.body.appendChild(ground);
    // a few things drifting down (off for anyone who has "reduce motion" turned on)
    if (T.fall) {
      const box = document.createElement("div");
      box.className = "season-fall"; box.setAttribute("aria-hidden", "true");
      for (let i = 0; i < 12; i++) {
        const s = document.createElement("span");
        const c = T.fall === "leaf" ? LEAF[i % 4] : T.fall === "heart" ? ["#e8738f", "#c2416b", "#f7b6cf"][i % 3] : T.fall === "snow" ? (T.dark ? "#fff" : "#9fc0e3") : T.fall === "rain" ? "#9fb7cc" : "";
        const size = Math.round(14 + rnd() * 12);
        s.style.cssText = `left:${(i * 8.3 + rnd() * 6).toFixed(1)}%;width:${size}px;height:${size}px;` +
          `animation-duration:${(14 + rnd() * 12).toFixed(1)}s;animation-delay:-${(rnd() * 20).toFixed(1)}s;background-image:${svgUrl(one(T.fall, c))}`;
        box.appendChild(s);
      }
      document.body.prepend(box);
    }
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", build); else build();
})();

/* Shared renderer for every class agenda page.
   Each class page defines window.CLASS = { name, updated, units: [...], days: [...] }
   before loading this file. Nothing in here needs to change from week to week. */
(function () {
  const C = window.CLASS;
  const PALETTE = ["#2f6fb3", "#8a4fb8", "#1f8a70", "#c0392b", "#b7791f", "#2b6cb0", "#6b46c1", "#2f855a"];
  const unitColor = {};
  C.units.forEach((u, i) => { unitColor[u] = PALETTE[i % PALETTE.length]; });

  function todayISO() {
    if (window.AGENDA_DATE) return window.AGENDA_DATE;
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
    if (e.li) body += `<p class="li"><b>Learning intention:</b> ${esc(e.li)}</p>`;
    if (e.did && e.did.length) body += `<ul>${e.did.map(x => `<li>${esc(x)}</li>`).join("")}</ul>`;
    if (e.mats && e.mats.length) {
      body += `<div class="mats"><b>Materials:</b> ${e.mats.map(m => {
        // Canvas items open in the Canvas tab itself (the page is embedded there); other sites open a new tab
        if (m.canvas && C.canvasCourse) return `<a class="canvas-link" href="${esc(safeUrl(C.canvasCourse + "/" + m.canvas))}" target="_top">${esc(m.name)}</a>`;
        if (m.url) return `<a href="${esc(safeUrl(m.url))}" target="_blank" rel="noopener">${esc(m.name)}</a>`;
        return esc(m.name);
      }).join(" · ")}</div>`;
    }
    if (C.solveNote && !e.off && !(e.mats || []).some(m => /SOLVE/i.test(m.name))) body += `<div class="mats"><b>SOLVE:</b> <span class="solvenote">${esc(C.solveNote)}</span></div>`;
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
      <h2>${esc(e.title)}</h2>${e.li ? `<p class="li"><b>Learning intention:</b> ${esc(e.li)}</p>` : ""}${e.did ? `<div>${e.did.map(esc).join(" ")}</div>` : ""}`;
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
