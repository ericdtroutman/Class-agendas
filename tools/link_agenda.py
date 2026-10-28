#!/usr/bin/env python3
"""Link Canvas items on both agenda pages from the calendar feed.

  python3 tools/link_agenda.py FEED_URL            # dry run: shows what it would change
  python3 tools/link_agenda.py FEED_URL --write    # edits earth-space/ and astro-ocean/index.html

Run from the repo root. It:
  * links any material on a day that has no link yet when its name matches a Canvas item in that class
    (numbers like "5." and codes like "3.1a" are ignored when matching);
  * adds each ESS "MM/DD SOLVE" and Astro "MM/DD Ticket In" to the day in its name, if missing;
  * lists Canvas items from --since (default 14 days ago) that aren't linked anywhere, so they can be placed.
It never moves or rewrites days, and never touches off days. Then: set `updated`, commit, push.
"""
import re, sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import canvas_feed  # noqa: E402

PAGES = {"earth-space/index.html": "94193", "astro-ocean/index.html": "94403"}


def norm(s):
    s = s.lower()
    s = re.sub(r"^\d+\.\s*", "", s)              # "5. Title"
    s = re.sub(r"^\d+\.\d+[a-z]?\s+", "", s)      # "3.1a Title"
    s = re.sub(r"\([^)]*\)", "", s)               # drop any "(...)" note, e.g. "(Canvas)", "(on paper)"
    s = re.sub(r"[^a-z0-9]+", " ", s)
    return s.strip()


def dated_kind(title):
    m = re.match(r"^(?:\d+\.\s*)?(\d{1,2})/(\d{1,2})\s+(SOLVE|Ticket In|Tix In)", title, re.I)
    if not m:
        return None
    mo, dy = int(m.group(1)), int(m.group(2))
    yr = 2026 if mo >= 8 else 2027
    kind = "SOLVE" if m.group(3).upper() == "SOLVE" else "Ticket In"
    return date(yr, mo, dy), kind


def day_blocks(s):
    for m in re.finditer(r'\n  \{ date: "([\d-]+)".*?(?=\n  \{ date: |\n  \]\n)', s, re.S):
        yield m.group(1), m.start(), m.end()


def main(url, write, since):
    feed = [i for i in canvas_feed.load(url) if i["id"]]
    unplaced_report = []
    for page, course in PAGES.items():
        s = Path(page).read_text()
        items = [i for i in feed if i["course"] == course]
        changes = []
        # work from the end so offsets stay valid
        for d, a, b in reversed(list(day_blocks(s))):
            block = s[a:b]
            if "off: true" in block:
                continue
            new = block
            # 1) link unlinked materials by name
            day = date.fromisoformat(d)
            for m in list(re.finditer(r'\{ name: "([^"]+)" \}', new)):
                # exact name only, and only an item due within 10 days of this day (so the
                # Gravity "Segment 2 Quiz" can never land on a Hidden Figures day)
                hits = [i for i in items if norm(i["title"]) == norm(m.group(1))
                        and abs((i["due"].date() - day).days) <= 10 and dated_kind(i["title"]) is None]
                hit = min(hits, key=lambda i: abs((i["due"].date() - day).days)) if hits else None
                if hit:
                    new = new.replace(m.group(0), f'{{ name: "{m.group(1)}", canvas: "assignments/{hit["id"]}" }}', 1)
                    changes.append(f"{d}: linked {m.group(1)} -> {hit['id']}")
            # 2) SOLVE / Ticket In on the date in their name
            for i in items:
                dk = dated_kind(i["title"])
                if not dk or dk[0].isoformat() != d or f'assignments/{i["id"]}' in new:
                    continue
                mat = f'{{ name: "{dk[0].month}/{dk[0].day} {dk[1]}", canvas: "assignments/{i["id"]}" }}'
                if "mats: [" in new:
                    new = re.sub(r"(mats: \[.*?)(\])", lambda mm: mm.group(1) + ", " + mat + mm.group(2), new, count=1, flags=re.S)
                else:
                    did = re.search(r'did: \[.*?\]', new, re.S)
                    if not did:
                        continue
                    new = new[:did.end()] + f",\n    mats: [{mat}]" + new[did.end():]
                changes.append(f"{d}: added {dk[0].month}/{dk[0].day} {dk[1]} -> {i['id']}")
            if new != block:
                s = s[:a] + new + s[b:]
        linked = set(re.findall(r"assignments/(\d+)", s))
        for i in items:
            if i["id"] not in linked and i["due"].date() >= since:
                unplaced_report.append(f"{page.split('/')[0]}: {i['title']} (due {i['due']:%a %m/%d}) -> assignments/{i['id']}")
        print(f"== {page}: {len(changes)} change(s)")
        for c in reversed(changes):
            print("  " + c)
        if write and changes:
            s = re.sub(r'updated: "[\d-]+"', f'updated: "{date.today().isoformat()}"', s, count=1)
            Path(page).write_text(s)
    print("\nCanvas items not linked on any day (place these by hand, by the plan, not by due date):")
    print("  " + "\n  ".join(unplaced_report) if unplaced_report else "  none")
    if not write:
        print("\n(dry run; add --write to save)")


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        sys.exit(__doc__)
    since = date.today() - timedelta(days=14)
    if "--since" in a:
        i = a.index("--since"); since = date.fromisoformat(a[i + 1]); del a[i:i + 2]
    main(a[0], "--write" in a, since)
