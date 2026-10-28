#!/usr/bin/env python3
"""Build a Canvas-importable Common Cartridge (.imscc) for one week of class.

Usage:  python3 build_week.py week.json OUTPUT.imscc

week.json describes one module made of daily agenda pages and assignments.
Each page also becomes a calendar event that links to that page, and each
assignment gets a due date, so it lands on the Canvas calendar and To-Do list.

Identifiers are derived from the course/week/item names, so re-importing an
edited file for the same week UPDATES the existing items instead of duplicating them.

Optional "files": [{"src": "local.pdf", "path": "ess-notebook/name.pdf"}] puts files
(for example Student Copy PDFs) into the course Files. Link them from an assignment
body with  $IMS-CC-FILEBASE$/ess-notebook/name.pdf  (add class
"instructure_file_link instructure_scribd_file auto_open" for an inline preview).

"points": null (or leaving points out with "no_points": true) leaves the points blank.
"""
import hashlib, json, sys, zipfile, html
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path

NS_CANVAS = 'xmlns="http://canvas.instructure.com/xsd/cccv1p0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://canvas.instructure.com/xsd/cccv1p0 https://canvas.instructure.com/xsd/cccv1p0.xsd"'


def gid(*parts):
    return "g" + hashlib.md5("|".join(parts).encode()).hexdigest()


def esc(s):
    return html.escape(s, quote=True)


def to_utc(local_str, tz):
    """'2026-10-28 23:59' in the course time zone -> Canvas UTC string."""
    dt = datetime.strptime(local_str, "%Y-%m-%d %H:%M").replace(tzinfo=ZoneInfo(tz))
    return dt.astimezone(ZoneInfo("UTC")).strftime("%Y-%m-%dT%H:%M:%S")


def page_html(title, ident, body, published):
    return f"""<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<title>{esc(title)}</title>
<meta name="identifier" content="{ident}">
<meta name="editing_roles" content="teachers">
<meta name="workflow_state" content="{'active' if published else 'unpublished'}">
</head>
<body>
{body}
</body>
</html>
"""


def assignment_html(title, body):
    return f"""<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<title>Assignment: {esc(title)}</title>
</head>
<body>
{body}
</body>
</html>
"""


def build(cfg_path, out_path):
    cfg_path = Path(cfg_path)
    cfg = json.loads(cfg_path.read_text())
    base = cfg_path.parent
    tz = cfg.get("timezone", "America/New_York")
    key = (cfg["course"], cfg["week_id"])
    published = cfg.get("publish", True)
    files = {}  # path in zip -> text
    binaries = {}  # path in zip -> bytes

    # ---- running notebook module: same module ID every week, so each import adds to it.
    nb = cfg.get("notebook")
    first_pos = 1
    if nb:
        first_pos = nb.get("start", 1)
        by_key = {a["key"]: a for a in cfg["assignments"]}
        n = first_pos
        for it in cfg["module_items"]:
            if it["type"] == "assignment":
                by_key[it["ref"]]["title"] = f"{n}. {by_key[it['ref']]['title']}"
            n += 1

    # ---- assignment groups
    group_ids = {}
    groups_xml = []
    for g in cfg.get("assignment_groups", []):
        g_id = gid(cfg["course"], "group", g["name"])
        group_ids[g["name"]] = g_id
        weight = f"\n    <group_weight>{float(g['weight'])}</group_weight>" if "weight" in g else ""
        groups_xml.append(f"""  <assignmentGroup identifier="{g_id}">
    <title>{esc(g['name'])}</title>{weight}
  </assignmentGroup>""")
    if groups_xml:
        files["course_settings/assignment_groups.xml"] = (
            f'<?xml version="1.0" encoding="UTF-8"?>\n<assignmentGroups {NS_CANVAS}>\n' + "\n".join(groups_xml) + "\n</assignmentGroups>\n")

    # ---- course files (Student Copy PDFs and similar)
    file_res = []
    for f in cfg.get("files", []):
        src = base / f["src"]
        if not src.exists():
            sys.exit(f"Missing file: {src}")
        zpath = "web_resources/" + f["path"]
        binaries[zpath] = src.read_bytes()
        file_res.append((gid(*key, "file", f["path"]), zpath))

    # ---- assignments
    assign_ids = {}
    for a in cfg["assignments"]:
        aid = gid(*key, "assignment", a["key"])
        assign_ids[a["key"]] = aid
        slug = a["key"]
        body = (base / a["body_file"]).read_text()
        files[f"{aid}/{slug}.html"] = assignment_html(a["title"], body)
        due = to_utc(a["due"], tz) if a.get("due") else ""
        unlock = to_utc(a["unlock"], tz) if a.get("unlock") else ""
        lock = to_utc(a["lock"], tz) if a.get("lock") else ""
        for label, v in (("unlock", a.get("unlock")), ("lock", a.get("lock"))):
            if v and a.get("due"):
                if label == "unlock" and v > a["due"]:
                    sys.exit(f"{a['title']}: unlock {v} is after the due date {a['due']}")
                if label == "lock" and v < a["due"]:
                    sys.exit(f"{a['title']}: lock {v} is before the due date {a['due']}")
        pts = a.get("points", 0)
        points_xml = "" if pts is None else f"  <points_possible>{float(pts)}</points_possible>\n"
        files[f"{aid}/assignment_settings.xml"] = f"""<?xml version="1.0" encoding="UTF-8"?>
<assignment identifier="{aid}" {NS_CANVAS}>
  <title>{esc(a['title'])}</title>
  <due_at>{due}</due_at>
  {f'<lock_at>{lock}</lock_at>' if lock else '<lock_at/>'}
  {f'<unlock_at>{unlock}</unlock_at>' if unlock else '<unlock_at/>'}
  <module_locked>false</module_locked>
  <workflow_state>{'published' if published else 'unpublished'}</workflow_state>
""" + (f"  <assignment_group_identifierref>{group_ids[a['group']]}</assignment_group_identifierref>\n" if a.get("group") else "") + """  <assignment_overrides>
  </assignment_overrides>
""" + points_xml + f"""  <grading_type>points</grading_type>
  <all_day>false</all_day>
  <submission_types>{','.join(a.get('submission_types', ['on_paper']))}</submission_types>
  <turnitin_enabled>false</turnitin_enabled>
  <vericite_enabled>false</vericite_enabled>
  <peer_reviews>false</peer_reviews>
  <automatic_peer_reviews>false</automatic_peer_reviews>
  <anonymous_peer_reviews>false</anonymous_peer_reviews>
  <grade_group_students_individually>false</grade_group_students_individually>
  <freeze_on_copy>false</freeze_on_copy>
  <omit_from_final_grade>false</omit_from_final_grade>
  <intra_group_peer_reviews>false</intra_group_peer_reviews>
  <only_visible_to_overrides>false</only_visible_to_overrides>
  <post_to_sis>false</post_to_sis>
  <moderated_grading>false</moderated_grading>
  <grader_count>0</grader_count>
  <anonymous_grading>false</anonymous_grading>
  <allowed_attempts>-1</allowed_attempts>
</assignment>
"""

    def resolve(text, page_slugs):
        for k, aid in assign_ids.items():
            text = text.replace("{{assignment:%s}}" % k, f"$CANVAS_OBJECT_REFERENCE$/assignments/{aid}")
        for k, slug in page_slugs.items():
            text = text.replace("{{page:%s}}" % k, f"$WIKI_REFERENCE$/pages/{slug}")
        return text

    # ---- pages
    page_ids, page_slugs = {}, {}
    for p in cfg.get("pages", []):
        page_ids[p["key"]] = gid(*key, "page", p["key"])
        page_slugs[p["key"]] = p["slug"]
    for p in cfg.get("pages", []):
        body = resolve((base / p["body_file"]).read_text(), page_slugs)
        files[f"wiki_content/{p['slug']}.html"] = page_html(p["title"], page_ids[p["key"]], body, published)
    for path in list(files):
        if path.endswith(".html") and not path.startswith("wiki_content/"):
            files[path] = resolve(files[path], page_slugs)

    # ---- calendar events (one per page that has a date)
    ev_xml = []
    for p in cfg.get("pages", []):
        if not p.get("date"):
            continue
        eid = gid(*key, "event", p["key"])
        start = to_utc(p["date"] + " 00:00", tz)
        desc = f'<p><a href="$WIKI_REFERENCE$/pages/{p["slug"]}">{esc(p["title"])}</a></p>'
        if p.get("event_note"):
            desc += f"<p>{esc(p['event_note'])}</p>"
        ev_xml.append(f"""  <event identifier="{eid}">
    <title>{esc(p.get('event_title', p['title']))}</title>
    <description>{esc(desc)}</description>
    <start_at>{start}</start_at>
    <end_at>{start}</end_at>
    <all_day>true</all_day>
    <all_day_date>{p['date']}</all_day_date>
    <workflow_state>active</workflow_state>
  </event>""")
    if ev_xml:
        files["course_settings/events.xml"] = (
            f'<?xml version="1.0" encoding="UTF-8"?>\n<events {NS_CANVAS}>\n' + "\n".join(ev_xml) + "\n</events>\n")

    # ---- module
    mod_id = gid(cfg["course"], "module", nb["key"]) if nb else gid(*key, "module")
    module_title = nb["title"] if nb else cfg["module_title"]
    items_xml, org_items = [], []
    for pos, it in enumerate(cfg["module_items"], start=first_pos):
        iid = gid(*key, "item", str(pos), it.get("ref", it.get("title", "")))
        if it["type"] == "header":
            items_xml.append(f"""      <item identifier="{iid}">
        <content_type>ContextModuleSubHeader</content_type>
        <workflow_state>{'active' if published else 'unpublished'}</workflow_state>
        <title>{esc(it['title'])}</title>
        <new_tab/>
        <position>{pos}</position>
        <indent>0</indent>
      </item>""")
            org_items.append(f'        <item identifier="{iid}">\n          <title>{esc(it["title"])}</title>\n        </item>')
            continue
        if it["type"] == "page":
            ref, ctype = page_ids[it["ref"]], "WikiPage"
            title = next(p["title"] for p in cfg.get("pages", []) if p["key"] == it["ref"])
        else:
            ref, ctype = assign_ids[it["ref"]], "Assignment"
            title = next(a["title"] for a in cfg["assignments"] if a["key"] == it["ref"])
        items_xml.append(f"""      <item identifier="{iid}">
        <content_type>{ctype}</content_type>
        <workflow_state>{'active' if published else 'unpublished'}</workflow_state>
        <title>{esc(title)}</title>
        <identifierref>{ref}</identifierref>
        <position>{pos}</position>
        <new_tab/>
        <indent>{it.get('indent', 0)}</indent>
      </item>""")
        org_items.append(f'        <item identifier="{iid}" identifierref="{ref}">\n          <title>{esc(title)}</title>\n        </item>')

    files["course_settings/module_meta.xml"] = f"""<?xml version="1.0" encoding="UTF-8"?>
<modules {NS_CANVAS}>
  <module identifier="{mod_id}">
    <title>{esc(module_title)}</title>
    <workflow_state>{'active' if published else 'unpublished'}</workflow_state>
""" + (f"    <position>{cfg['module_position']}</position>\n" if "module_position" in cfg else "") + f"""    <require_sequential_progress>false</require_sequential_progress>
    <locked>false</locked>
    <items>
{chr(10).join(items_xml)}
    </items>
  </module>
</modules>
"""
    files["course_settings/canvas_export.txt"] = "Weekly module built from the lesson plan doc.\n"

    # ---- manifest (no course_settings.xml on purpose: importing must never change course settings)
    cs_id = gid(*key, "course_settings")
    res = [f"""    <resource identifier="{cs_id}" type="associatedcontent/imscc_xmlv1p1/learning-application-resource" href="course_settings/canvas_export.txt">
      <file href="course_settings/module_meta.xml"/>
""" + ('      <file href="course_settings/assignment_groups.xml"/>\n' if groups_xml else "") + ('      <file href="course_settings/events.xml"/>\n' if ev_xml else "") + """      <file href="course_settings/canvas_export.txt"/>
    </resource>"""]
    for fid, zpath in file_res:
        res.append(f'    <resource identifier="{fid}" type="webcontent" href="{esc(zpath)}">\n      <file href="{esc(zpath)}"/>\n    </resource>')
    for p in cfg.get("pages", []):
        f = f"wiki_content/{p['slug']}.html"
        res.append(f'    <resource identifier="{page_ids[p["key"]]}" type="webcontent" href="{f}">\n      <file href="{f}"/>\n    </resource>')
    for a in cfg["assignments"]:
        aid = assign_ids[a["key"]]
        res.append(f"""    <resource identifier="{aid}" type="associatedcontent/imscc_xmlv1p1/learning-application-resource" href="{aid}/{a['key']}.html">
      <file href="{aid}/{a['key']}.html"/>
      <file href="{aid}/assignment_settings.xml"/>
    </resource>""")

    files["imsmanifest.xml"] = f"""<?xml version="1.0" encoding="UTF-8"?>
<manifest identifier="{gid(*key, 'manifest')}" xmlns="http://www.imsglobal.org/xsd/imsccv1p1/imscp_v1p1" xmlns:lom="http://ltsc.ieee.org/xsd/imsccv1p1/LOM/resource" xmlns:lomimscc="http://ltsc.ieee.org/xsd/imsccv1p1/LOM/manifest" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.imsglobal.org/xsd/imsccv1p1/imscp_v1p1 http://www.imsglobal.org/profile/cc/ccv1p1/ccv1p1_imscp_v1p2_v1p0.xsd http://ltsc.ieee.org/xsd/imsccv1p1/LOM/resource http://www.imsglobal.org/profile/cc/ccv1p1/LOM/ccv1p1_lomresource_v1p0.xsd http://ltsc.ieee.org/xsd/imsccv1p1/LOM/manifest http://www.imsglobal.org/profile/cc/ccv1p1/LOM/ccv1p1_lommanifest_v1p0.xsd">
  <metadata>
    <schema>IMS Common Cartridge</schema>
    <schemaversion>1.1.0</schemaversion>
    <lomimscc:lom>
      <lomimscc:general>
        <lomimscc:title>
          <lomimscc:string>{esc(module_title)}</lomimscc:string>
        </lomimscc:title>
      </lomimscc:general>
    </lomimscc:lom>
  </metadata>
  <organizations>
    <organization identifier="org_1" structure="rooted-hierarchy">
      <item identifier="LearningModules">
      <item identifier="{mod_id}">
        <title>{esc(module_title)}</title>
{chr(10).join(org_items)}
      </item>
      </item>
    </organization>
  </organizations>
  <resources>
{chr(10).join(res)}
  </resources>
</manifest>
"""

    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("imsmanifest.xml", files.pop("imsmanifest.xml"))
        for path, text in files.items():
            z.writestr(path, text)
        for path, data in binaries.items():
            z.writestr(path, data)
    print(f"Wrote {out_path}: {len(cfg.get('pages', []))} pages, {len(cfg['assignments'])} assignments, "
          f"{len(binaries)} files, {len(ev_xml)} calendar events")


if __name__ == "__main__":
    build(sys.argv[1], sys.argv[2])
