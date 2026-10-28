#!/usr/bin/env python3
"""Print Arianna's plan rows for Eric's ESS days, already shifted, with handout links.

  python3 tools/ess_plan.py PLAN_EXPORT 2026-11-09 2026-11-13

PLAN_EXPORT = the LESSON PLANS 26/27 doc exported as text/html with the Drive download tool
(the saved tool-result JSON, or a plain .html file). Only rows inside the "Week" tables
(header row Date / Day / Unit # / Lesson Plan) for the requested days are printed, so the
student names and birthdays at the top of the doc never come out.
Links whose label looks like a teacher file (key, TG, annotated, guided edition) are marked TEACHER:
never attach or link those.
"""
import base64, html, json, re, sys, urllib.parse
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import ess_dates  # noqa: E402

TEACHER = re.compile(r"key|\bTG\b|teacher|annotat|guided edition|how to find|answers", re.I)


def load_html(path):
    raw = Path(path).read_text(encoding="utf-8", errors="replace")
    if raw.lstrip().startswith("{"):
        c = json.loads(raw)["content"]
        try:
            return base64.b64decode(c).decode("utf-8", errors="replace")
        except Exception:
            return c
    return raw


def cell_text(c):
    c = re.sub(r"<br\s*/?>|</p>|</li>", "\n", c)
    t = html.unescape(re.sub(r"<[^>]+>", "", c))
    return "\n".join(l.strip() for l in t.split("\n") if l.strip())


def cell_links(c):
    out = []
    for h, t in re.findall(r'<a [^>]*href="([^"]+)"[^>]*>(.*?)</a>', c, re.S):
        h = html.unescape(h)
        m = re.search(r"[?&]q=([^&]+)", h)
        if m and "google.com/url" in h:
            h = urllib.parse.unquote(m.group(1))
        out.append((cell_text(t), h))
    return out


def plan_rows(src):
    """{ 'M/D': {'lesson','materials','notes','links'} } from the Week tables only."""
    rows = {}
    for table in re.findall(r"<table.*?</table>", src, re.S):
        trs = re.findall(r"<tr.*?</tr>", table, re.S)
        if not trs:
            continue
        head = [cell_text(c).lower() for c in re.findall(r"<td.*?</td>", trs[0], re.S)]
        if not (head and head[0].startswith("date") and any("lesson" in h for h in head)):
            continue
        for tr in trs[1:]:
            cells = re.findall(r"<td.*?</td>", tr, re.S)
            if len(cells) < 4:
                continue
            d = cell_text(cells[0])
            if not re.fullmatch(r"\d{1,2}/\d{1,2}", d):
                continue
            rows[d] = {
                "lesson": cell_text(cells[3]),
                "materials": cell_text(cells[4]) if len(cells) > 4 else "",
                "notes": cell_text(cells[5]) if len(cells) > 5 else "",
                "links": [l for c in cells[3:6] for l in cell_links(c)],
            }
    return rows


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    rows = plan_rows(load_html(sys.argv[1]))
    a = date.fromisoformat(sys.argv[2])
    b = date.fromisoformat(sys.argv[3]) if len(sys.argv) > 3 else a + timedelta(days=4)
    d = a
    while d <= b:
        if d.weekday() < 5:
            r = ess_dates.off_reason(d)
            print(f"\n=== Eric {d:%a} {ess_dates.md(d)}", end="")
            if r:
                print(f": {r}")
            else:
                her = ess_dates.her_date(d)
                swap = ess_dates.SWAPS.get(d.isoformat())
                print(f"  <- her {her:%a} {ess_dates.md(her)}" if her else "  <- no plan day", end="")
                print(f"   SWAP: {swap}" if swap else "")
                row = rows.get(ess_dates.md(her)) if her else None
                if not row:
                    print("   (no row in her plan for that day yet)")
                else:
                    for k in ("lesson", "materials", "notes"):
                        if row[k]:
                            print(f"   {k.upper()}: " + row[k].replace("\n", "\n      "))
                    for label, url in row["links"]:
                        tag = "TEACHER " if TEACHER.search(label) else ""
                        print(f"   {tag}LINK: {label} -> {url}")
        d += timedelta(days=1)
