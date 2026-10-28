#!/usr/bin/env python3
"""Build and check one week's Canvas import file from a short spec.

  python3 tools/make_week.py spec.json OUT_DIR

spec.json:
{
  "class": "ess" | "astro",
  "week_id": "2026-11-09",              # Monday of the week; keep it the same when re-importing a fix
  "start": 12,                           # next notebook number
  "items": [
    {"type": "ticket", "date": "2026-11-10"},                                  # Astro Ticket In, 1 pt, text box
    {"type": "paper", "title": "Write the Algorithm", "date": "2026-11-10",
     "pdf": "pdf/Write the Algorithm (Student Copy).pdf", "body": "One or two sentences for students."},
    {"type": "mastery", "title": "Carbon Cycle Mastery Check", "date": "2026-10-29"},   # ESS quiz placeholder, no points
    {"type": "entry", "title": "Rock Cycle Put It Together", "date": "2026-10-27", "pdf": "..."}  # ESS entry ticket, 1 pt
  ]
}
Order items in the order things happen. Due = 11:59 PM that day. Everything on paper unless "submission" is given.
"links": [{"text": "...", "url": "..."}] adds links to a body (Eric's own Google files must use /copy links).
Writes week.json + bodies, builds <Class>_Week_of_MM-DD.imscc, validates it, and prints the table for Eric.
"""
import html, json, re, shutil, sys, zipfile
from datetime import date
from pathlib import Path
import xml.dom.minidom as md

sys.path.insert(0, str(Path(__file__).parent))
import build_week  # noqa: E402

CLASSES = {
    # "course" must never change: it is part of every Canvas ID (module, items), so re-imports update instead of duplicating.
    "astro": {"course": "Astro/Ocean", "nb": "astronomy-notebook", "nb_title": "Astronomy Notebook", "file": "Astro-Ocean"},
    "ess": {"course": "ESS", "nb": "ess-notebook", "nb_title": "ESS Notebook", "file": "ESS"},
}


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def md_(d):
    return f"{d.month}/{d.day}"


def main(spec_path, out_dir):
    spec_path = Path(spec_path)
    spec = json.loads(spec_path.read_text())
    c = CLASSES[spec["class"]]
    out = Path(out_dir); (out / "assignments").mkdir(parents=True, exist_ok=True); (out / "pdf").mkdir(exist_ok=True)
    assignments, items, files, table = [], [], [], []
    for it in spec["items"]:
        d = date.fromisoformat(it["date"])
        t = it["type"]
        if t == "ticket":
            title, key, pts, sub = f"{md_(d)} Ticket In", f"ticket-in-{d:%m-%d}", 1, ["online_text_entry"]
            body = "<p>Answer today's Ticket In question from the board.</p>\n"
        else:
            title = it["title"] + (" (Quiz)" if t == "mastery" and "(Quiz)" not in it["title"] else "")
            key = it.get("key") or slug(it["title"])
            pts = None if t == "mastery" else (1 if t == "entry" else it.get("points", 10))
            sub = it.get("submission", ["on_paper"])
            body = f"<p>{html.escape(it['body'])}</p>\n" if it.get("body") else ""
            for l in it.get("links", []):
                body += f'<p><a href="{html.escape(l["url"])}" target="_blank">{html.escape(l["text"])}</a></p>\n'
            if it.get("pdf"):
                src = (spec_path.parent / it["pdf"]).resolve()
                name = src.name
                shutil.copy(src, out / "pdf" / name)
                files.append({"src": f"pdf/{name}", "path": f"{c['nb']}/{name}"})
                body += (f'<p><a class="instructure_file_link instructure_scribd_file auto_open" title="{html.escape(name)}" '
                         f'href="$IMS-CC-FILEBASE$/{c["nb"]}/{html.escape(name)}">{html.escape(name)}</a></p>\n')
        bf = f"assignments/{key}.html"
        (out / bf).write_text(body or "<p></p>\n")
        assignments.append({"key": key, "title": title, "due": f"{d.isoformat()} 23:59", "points": pts,
                            "submission_types": sub, "body_file": bf})
        items.append({"type": "assignment", "ref": key})
        table.append((title, pts, d, sub[0], Path(it["pdf"]).name if it.get("pdf") else ""))
    week = {"course": c["course"], "week_id": spec["week_id"], "timezone": "America/New_York", "publish": True,
            "pages": [], "files": files, "assignments": assignments, "module_items": items,
            "notebook": {"key": c["nb"], "title": c["nb_title"], "start": spec["start"]}}
    (out / "week.json").write_text(json.dumps(week, indent=2))
    wk = date.fromisoformat(spec["week_id"])
    imscc = out / f"{c['file']}_Week_of_{wk:%m-%d}.imscc"
    build_week.build(out / "week.json", imscc)
    check(imscc)
    print(f"\n| # | Item | Points | Due | Type | File |\n|---|---|---|---|---|---|")
    for n, (title, pts, d, sub, pdf) in enumerate(table, spec["start"]):
        print(f"| {n} | {title} | {'none' if pts is None else pts} | {d:%a} {md_(d)} | {sub.replace('_', ' ')} | {pdf} |")
    print(f"\nNext {c['nb_title']} number: {spec['start'] + len(table)}")


def check(imscc):
    z = zipfile.ZipFile(imscc)
    names = set(z.namelist())
    problems = []
    for n in names:
        if n.endswith(".xml"):
            try:
                md.parseString(z.read(n))
            except Exception as e:
                problems.append(f"bad XML {n}: {e}")
    man = z.read("imsmanifest.xml").decode()
    problems += [f"manifest points to missing {h}" for h in re.findall(r'href="([^"]+)"', man) if html.unescape(h) not in names]
    for n in names:
        if n.endswith(".html"):
            t = z.read(n).decode()
            problems += [f"missing file {p}" for p in re.findall(r'\$IMS-CC-FILEBASE\$/([^"]+)"', t)
                         if "web_resources/" + html.unescape(p) not in names]
            problems += [f"Google link not /copy: {u}" for u in re.findall(r'https://docs\.google\.com/[^"\s<]+', t)
                         if not u.rstrip("/").endswith("/copy")]
    print("Check:", "OK" if not problems else "\n  " + "\n  ".join(problems))
    if problems:
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
