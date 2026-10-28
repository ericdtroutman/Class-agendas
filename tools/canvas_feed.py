#!/usr/bin/env python3
"""Download Eric's Canvas calendar feed with curl (the whole thing) and list items.

  python3 tools/canvas_feed.py FEED_URL [--course ess|astro] [--since 2026-11-01]

FEED_URL is in canvas-workflow-guide.md (treat it like a password: never commit it).
Never read the feed with a web-fetch tool: those stop at ~75,000 characters and hide the newest items.
Course 94292 (Arianna's class) is always ignored.
"""
import re, subprocess, sys, tempfile
from datetime import datetime, date
from zoneinfo import ZoneInfo

COURSES = {"ess": "94193", "astro": "94403"}
IGNORE = {"94292"}
ET = ZoneInfo("America/New_York")


def fetch(url):
    with tempfile.NamedTemporaryFile(suffix=".ics") as f:
        subprocess.run(["curl", "-sSfL", "-o", f.name, url], check=True)
        return open(f.name, encoding="utf-8").read()


def parse(text):
    text = text.replace("\r\n", "\n").replace("\n ", "")
    items = []
    for ev in text.split("BEGIN:VEVENT")[1:]:
        g = lambda k: (re.search(rf"^{k}[^:\n]*:(.*)$", ev, re.M) or [None, ""])[1].strip()
        url, summ, start = g("URL"), g("SUMMARY"), g("DTSTART")
        c = re.search(r"course_(\d+)", url)
        if not c or c.group(1) in IGNORE:
            continue
        a = re.search(r"#assignment_(\d+)", url)
        if re.fullmatch(r"\d{8}", start):
            due = datetime.strptime(start, "%Y%m%d").replace(tzinfo=ET)
            all_day = True
        else:
            due = datetime.strptime(start, "%Y%m%dT%H%M%SZ").replace(tzinfo=ZoneInfo("UTC")).astimezone(ET)
            all_day = False
        title = re.sub(r"\s*\[[^\]]*\]\s*$", "", summ).replace("\\,", ",").replace("\\;", ";").strip()
        items.append({"course": c.group(1), "title": title, "due": due, "all_day": all_day,
                      "id": a.group(1) if a else None, "kind": "assignment" if a else "event"})
    return items


def load(url):
    return parse(fetch(url))


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    url = args.pop(0)
    course = since = None
    while args:
        k = args.pop(0)
        if k == "--course":
            course = COURSES.get(args[0], args[0]); args.pop(0)
        elif k == "--since":
            since = date.fromisoformat(args.pop(0))
    for it in sorted(load(url), key=lambda i: (i["course"], i["due"])):
        if course and it["course"] != course:
            continue
        if since and it["due"].date() < since:
            continue
        when = it["due"].strftime("%a %m/%d") + ("" if it["all_day"] else it["due"].strftime(" %I:%M %p"))
        print(f"{it['course']} | {when} | {it['title']} | {('assignments/' + it['id']) if it['id'] else it['kind']}")
