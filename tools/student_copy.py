#!/usr/bin/env python3
"""Make a Student Copy PDF: drop teacher pages (answer key, teacher notes, TG, timing) and everything after.

  python3 tools/student_copy.py SOURCE "Handout Name" [OUT_DIR] [--keep 1-3]

SOURCE = a PDF, or the saved tool-result JSON from the Drive download tool (PDF export) or a Canva export.
Writes "<Handout Name> (Student Copy).pdf" and prints each page's first words plus what was dropped.
Teacher pages have always been at the end, starting on their own page. If one starts mid-page, stop and ask Eric.
"""
import base64, json, re, sys
from pathlib import Path
import pypdf, io

TRIGGER = re.compile(r"answer key|teacher (use|page|notes|guide)|\bTG\b|^timing\b|key for|how to run it", re.I)


def load(src):
    p = Path(src)
    raw = p.read_bytes()
    if raw[:4] == b"%PDF":
        return raw
    d = json.loads(raw)
    return base64.b64decode(d["content"])


def text(page):
    return " ".join((page.extract_text() or "").split())


if __name__ == "__main__":
    a = sys.argv[1:]
    keep = None
    if "--keep" in a:
        i = a.index("--keep"); lo, hi = map(int, a[i + 1].split("-")); keep = list(range(lo, hi + 1)); del a[i:i + 2]
    src, name = a[0], a[1]
    out_dir = Path(a[2]) if len(a) > 2 else Path(".")
    r = pypdf.PdfReader(io.BytesIO(load(src)))
    pages = [text(p) for p in r.pages]
    if keep is None:
        cut = next((i for i, t in enumerate(pages) if TRIGGER.search(t[:250])), len(pages))
        keep = list(range(1, cut + 1))
    w = pypdf.PdfWriter()
    for i, t in enumerate(pages, 1):
        status = "KEEP" if i in keep else "DROP"
        print(f"  p{i} {status}: {t[:90]}")
        if i in keep:
            w.add_page(r.pages[i - 1])
    leftover = [i for i in keep if TRIGGER.search(pages[i - 1])]
    if leftover:
        print(f"  WARNING: teacher words still inside kept page(s) {leftover}; check before using")
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"{name} (Student Copy).pdf"
    w.add_metadata({"/Title": f"{name} (Student Copy)"})
    w.write(out)
    print(f"Wrote {out} ({len(keep)} of {len(pages)} pages)")
