#!/usr/bin/env python3
"""ESS date map: Arianna's plan date -> Eric's teaching date (one school day later).

This file is the single source of truth for the ESS shift. Never work the shift out by hand.

  python3 tools/ess_dates.py 2026-11-02 2026-11-13     # Eric's days in that range, with her day for each

Change OVERRIDES when Eric keeps a day in place or moves one; change SWAPS when he teaches
something else on purpose (the agenda/slide then follow his plan, not hers).
"""
import sys
from datetime import date, timedelta

FIRST, LAST = date(2026, 9, 2), date(2027, 6, 25)

# Ken-Ton 2026-27 no-school days (inclusive ranges) and Regents weeks (no regular class).
NO_SCHOOL = [("2026-09-04", "2026-09-04"), ("2026-09-07", "2026-09-07"), ("2026-10-12", "2026-10-12"),
             ("2026-11-03", "2026-11-03"), ("2026-11-11", "2026-11-11"), ("2026-11-25", "2026-11-27"),
             ("2026-12-24", "2027-01-01"), ("2027-01-18", "2027-01-18"), ("2027-02-15", "2027-02-19"),
             ("2027-03-12", "2027-03-12"), ("2027-03-26", "2027-04-02"), ("2027-05-31", "2027-05-31"),
             ("2027-06-18", "2027-06-18")]
REGENTS = [("2027-01-25", "2027-01-29"), ("2027-06-14", "2027-06-25")]

# her date -> his date, where Eric changed the normal shift (Eric, 10/27-10/28).
OVERRIDES = {
    "2026-10-29": "2026-11-02",  # her Cluster/Test Review moved to his Monday
    "2026-10-30": "2026-10-30",  # Halloween Carbon Cycle Activity stays on 10/30
}

# his date -> what he did instead of her lesson (on purpose).
SWAPS = {
    "2026-10-26": "Rock Odyssey (film) in place of her In Class Lab 3 (crayon rock cycle)",
}


def _expand(ranges):
    out = set()
    for a, b in ranges:
        d, e = date.fromisoformat(a), date.fromisoformat(b)
        while d <= e:
            out.add(d)
            d += timedelta(days=1)
    return out


OFF = _expand(NO_SCHOOL)
REG = _expand(REGENTS)


def is_class_day(d):
    return FIRST <= d <= LAST and d.weekday() < 5 and d not in OFF and d not in REG


def next_class_day(d):
    d += timedelta(days=1)
    while not is_class_day(d):
        d += timedelta(days=1)
        if d > LAST:
            return None
    return d


def his_date(her):
    """Her plan date (date or 'YYYY-MM-DD') -> Eric's date."""
    her = her if isinstance(her, date) else date.fromisoformat(her)
    if her.isoformat() in OVERRIDES:
        return date.fromisoformat(OVERRIDES[her.isoformat()])
    return next_class_day(her)


def her_date(his):
    """Eric's date -> her plan date (None if no plan day maps there)."""
    his = his if isinstance(his, date) else date.fromisoformat(his)
    d = his - timedelta(days=14)
    while d <= his:
        if is_class_day(d) and his_date(d) == his:
            return d
        d += timedelta(days=1)
    return None


def off_reason(d):
    if d in OFF:
        return "no school"
    if d in REG:
        return "Regents"
    if d.weekday() >= 5:
        return "weekend"
    return None


def md(d):
    return f"{d.month}/{d.day}"


if __name__ == "__main__":
    a = date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else date.today()
    b = date.fromisoformat(sys.argv[2]) if len(sys.argv) > 2 else a + timedelta(days=6)
    d = a
    print("Eric's day      | her plan day | note")
    while d <= b:
        if d.weekday() < 5:
            r = off_reason(d)
            if r:
                print(f"{d:%a} {md(d):<10} | {'-':<12} | {r}")
            else:
                h = her_date(d)
                note = SWAPS.get(d.isoformat(), "")
                if h and h.isoformat() in OVERRIDES:
                    note = (note + " " if note else "") + "(override)"
                print(f"{d:%a} {md(d):<10} | {(f'{h:%a} ' + md(h)) if h else 'none':<12} | {note}")
        d += timedelta(days=1)
