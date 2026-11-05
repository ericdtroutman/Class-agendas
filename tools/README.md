# Tools for Mr. Troutman's weekly Canvas work

Run from the repo root. Python 3 with pypdf. The feed link lives only in the project guide; never commit it.

| Tool | What it does |
|---|---|
| `ess_dates.py START END` | Her plan day for each of Eric's ESS days (the one-day shift, overrides, swaps). The only place the shift is worked out. |
| `canvas_feed.py FEED [--course ess\|astro] [--since DATE]` | Downloads the whole Canvas feed with curl and lists items with their `assignments/ID`. |
| `ess_plan.py PLAN_EXPORT START END` | Her LESSON PLANS rows for Eric's days, shifted, with handout links (teacher files marked). Never prints the top of the doc. |
| `student_copy.py SOURCE "Name" OUT_DIR` | Student Copy PDF: drops the answer key / teacher pages and everything after. |
| `make_week.py spec.json OUT_DIR` | Builds and checks a week's .imscc from a short spec; prints the table for Eric and the next notebook number. Re-lists every earlier imported notebook item from `notebook_ledger.json` (Canvas drops module items missing from a new import) and adds this week's. Commit the ledger after every build. |
| `link_agenda.py FEED [--write]` | Links Canvas items, SOLVEs and Ticket Ins on both agenda pages; lists anything it couldn't place. |
| `build_week.py` | The Common Cartridge builder `make_week.py` uses. |
