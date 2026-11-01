#!/usr/bin/env python3
"""Convert tailored resume markdown to docx using base template OOXML formatting."""
from __future__ import annotations

import argparse
import copy
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kit  # noqa: E402

_links = kit.load_module("resume_links", "resume_links.py")
TOKEN = _links.TOKEN
resolve_link = _links.resolve_link
company_website_url = _links.company_website_url
company_about_text = _links.company_about_text
auto_bold = _links.auto_bold

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
R = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"

DEFAULT_TEMPLATE = kit.DEFAULT_TEMPLATE

# Paragraph index of each style prototype in templates/resume-template.docx.
# A custom template must keep this exact paragraph order.
PROTO = {
    "name": 0,
    "headline": 1,
    "relocation": 2,
    "contact1": 3,
    "contact2": 4,
    "spacer": 5,
    "summary": 6,
    "section": 7,
    "skills": 8,
    "role_header": 9,
    "company": 10,
    "bullet": 11,
    "edu_header": 12,
    "edu_detail": 13,
    "company_about": 13,
    "honor_header": 14,
    "honor_sub": 15,
    "honor_body": 16,
}


def w(tag: str) -> str:
    return f"{W}{tag}"


def clone(paras: list[ET.Element], key: str) -> ET.Element:
    return copy.deepcopy(paras[PROTO[key]])


def clear_runs(p: ET.Element) -> None:
    for child in list(p):
        if child.tag in (w("r"), w("hyperlink")):
            p.remove(child)


def first_rpr(p: ET.Element, bold: bool = False) -> ET.Element | None:
    for node in p.iter():
        if node.tag != w("rPr"):
            continue
        b = node.find(w("b"))
        if bold and b is None:
            continue
        if not bold and b is not None:
            continue
        return copy.deepcopy(node)
    rpr = p.find(f".//{w('rPr')}")
    return copy.deepcopy(rpr) if rpr is not None else None


def either(a: ET.Element | None, b: ET.Element | None) -> ET.Element | None:
    """`a or b` for XML elements: a childless element is falsy, so `or` would skip it."""
    return a if a is not None else b


def strip_md(text: str) -> str:
    return re.sub(r"\*\*(.+?)\*\*", r"\1", text).strip()


def add_run(p: ET.Element, text: str, rpr: ET.Element | None) -> None:
    r = ET.SubElement(p, w("r"))
    if rpr is not None:
        r.append(copy.deepcopy(rpr))
    t = ET.SubElement(r, w("t"))
    if text.startswith(" ") or text.endswith(" "):
        t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    t.text = text


def set_plain(p: ET.Element, text: str) -> None:
    clear_runs(p)
    add_run(p, text, first_rpr(p))


def set_skill_line(p: ET.Element, text: str) -> None:
    clear_runs(p)
    if ":" in text:
        label, rest = text.split(":", 1)
        add_run(p, label + ":", either(first_rpr(p, bold=True), first_rpr(p)))
        add_run(p, rest, first_rpr(p))
    else:
        add_run(p, text, first_rpr(p))


BULLET_HANGING_TWIPS = 210


def set_hanging_bullet_indent(p: ET.Element, twips: int = BULLET_HANGING_TWIPS) -> None:
    pPr = p.find(w("pPr"))
    if pPr is None:
        pPr = ET.SubElement(p, w("pPr"))
    ind = pPr.find(w("ind"))
    if ind is None:
        ind = ET.SubElement(pPr, w("ind"))
    ind.set(w("left"), str(twips))
    ind.set(w("hanging"), str(twips))


def set_bullet_line(
    p: ET.Element, text: str, rels: RelManager, company: str, skills: str
) -> None:
    set_hanging_bullet_indent(p)
    bullet = text if text.startswith("•") else f"• {text}"
    set_styled_text(p, auto_bold(bullet, skills, "bullet"), rels, company)


def set_company_line(p: ET.Element, role: dict, rels: RelManager) -> None:
    company = role["company"]
    name = role.get("company_name") or company
    url = company_website_url(name)
    normal = either(first_rpr(p, bold=False), first_rpr(p))
    href_style = either(link_rpr(p), normal)
    clear_runs(p)
    if url:
        add_hyperlink(p, name, url, href_style, rels)
        suffix = company[len(name) :]
        if suffix:
            add_run(p, suffix, normal)
    else:
        add_run(p, company, normal)
    links = role.get("links") or []
    if not links:
        return
    tab_run = ET.SubElement(p, w("r"))
    if normal is not None:
        tab_run.append(copy.deepcopy(normal))
    ET.SubElement(tab_run, w("tab"))
    for j, label in enumerate(links):
        if j:
            add_run(p, " ", normal)
        target = resolve_link(label, company)
        display = f"[{label}]"
        if target:
            add_hyperlink(p, display, target, href_style, rels)
        else:
            add_run(p, display, normal)


def set_name(p: ET.Element, full_name: str) -> None:
    parts = full_name.rsplit(" ", 1)
    first = parts[0] if len(parts) == 2 else full_name
    last = parts[1] if len(parts) == 2 else ""
    bold = first_rpr(p, bold=True)
    if bold is None:
        bold = first_rpr(p)
    normal = first_rpr(p, bold=False)
    if normal is None:
        normal = first_rpr(p)
    clear_runs(p)
    add_run(p, first, bold)
    if last:
        add_run(p, " ", normal)
        add_run(p, last, bold)


def set_tabbed_header(p: ET.Element, left: str, right: str) -> None:
    runs = [c for c in p if c.tag == w("r")]
    clear_runs(p)
    bold = None
    normal = None
    for r in runs:
        rpr = r.find(w("rPr"))
        if rpr is not None and rpr.find(w("b")) is not None:
            bold = copy.deepcopy(rpr)
        elif rpr is not None:
            normal = copy.deepcopy(rpr)
    add_run(p, left, bold if bold is not None else normal)
    tab_run = ET.SubElement(p, w("r"))
    if normal is not None:
        tab_run.append(copy.deepcopy(normal))
    ET.SubElement(tab_run, w("tab"))
    add_run(p, right, normal)


class RelManager:
    REL_PKG = "http://schemas.openxmlformats.org/package/2006/relationships"

    def __init__(self, root: ET.Element):
        self.root = root
        self._url_to_rid: dict[str, str] = {}
        self._next = 1
        for rel in root:
            rid, target = rel.get("Id"), rel.get("Target")
            if rid and target:
                self._url_to_rid[target] = rid
                self._next = max(self._next, int(rid.replace("rId", "") or "0") + 1)

    def rid_for(self, url: str) -> str:
        if url in self._url_to_rid:
            return self._url_to_rid[url]
        rid = f"rId{self._next}"
        self._next += 1
        rel = ET.SubElement(self.root, f"{{{self.REL_PKG}}}Relationship")
        rel.set("Id", rid)
        rel.set(
            "Type",
            "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink",
        )
        rel.set("Target", url)
        rel.set("TargetMode", "External")
        self._url_to_rid[url] = rid
        return rid


def link_rpr(p: ET.Element) -> ET.Element | None:
    for h in p.iter(w("hyperlink")):
        rpr = h.find(f".//{w('rPr')}")
        if rpr is not None:
            return copy.deepcopy(rpr)
    return None


def add_hyperlink(
    p: ET.Element, text: str, url: str, rpr: ET.Element | None, rels: RelManager
) -> None:
    h = ET.SubElement(p, w("hyperlink"))
    h.set(f"{R}id", rels.rid_for(url))
    r = ET.SubElement(h, w("r"))
    if rpr is not None:
        r.append(copy.deepcopy(rpr))
    t = ET.SubElement(r, w("t"))
    if text.startswith(" ") or text.endswith(" "):
        t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    t.text = text


def set_contact_line(p: ET.Element, line: list[dict], rels: RelManager, sep: str = " | ") -> None:
    """Render one profile contact line: optional icon, then a hyperlink (or plain text) per item."""
    normal = either(first_rpr(p, bold=False), first_rpr(p))
    href_style = either(link_rpr(p), normal)
    clear_runs(p)
    for idx, item in enumerate(line):
        prefix = (sep if idx else "") + (f"{item['icon']} " if item.get("icon") else "")
        if prefix:
            add_run(p, prefix, normal)
        if item.get("url"):
            add_hyperlink(p, item["text"], item["url"], href_style, rels)
        else:
            add_run(p, item["text"], normal)


def set_styled_text(
    p: ET.Element, text: str, rels: RelManager | None = None, company: str = ""
) -> None:
    normal = first_rpr(p, bold=False)
    if normal is None:
        normal = first_rpr(p)
    bold = first_rpr(p, bold=True)
    if bold is None:
        bold = normal
    href_style = link_rpr(p)
    if href_style is None:
        href_style = normal
    clear_runs(p)
    pos = 0
    for m in TOKEN.finditer(text):
        if m.start() > pos:
            add_run(p, text[pos : m.start()], normal)
        if m.group(1):
            add_run(p, m.group(1), bold)
        elif m.group(2):
            label, url = m.group(2), m.group(3)
            if rels:
                add_hyperlink(p, label, url, href_style, rels)
            else:
                add_run(p, label, normal)
        else:
            label = m.group(4)
            display = f"[{label}]"
            url = resolve_link(label, company) if rels else None
            if url:
                add_hyperlink(p, display, url, href_style, rels)
            else:
                add_run(p, display, normal)
        pos = m.end()
    if pos < len(text):
        add_run(p, text[pos:], normal)


def parse_company_line(line: str) -> tuple[str, str, str]:
    line = line.strip()
    dates = ""
    if "|" in line:
        line, dates = [x.strip() for x in line.rsplit("|", 1)]
    m = re.match(r"\*\*(.+?)\*\*,\s*(.+)", line)
    if m:
        return m.group(1), m.group(2), dates
    return line.strip("* "), line, dates


def is_company_line(line: str) -> bool:
    line = line.strip()
    return "|" in line or re.match(r"\*\*(.+?)\*\*,\s*(.+)", line) is not None


def parse_honor(line: str) -> tuple[str, str, str]:
    year = ""
    ym = re.search(r"\((\d{4})\)", line)
    if ym:
        year = ym.group(1)
        line = line.replace(ym.group(0), "").strip()
    if " - " in line:
        title, rest = line.split(" - ", 1)
    else:
        title, rest = line, ""
    title = strip_md(title.strip("* "))
    ym2 = re.search(r"(\d{4})\s*$", title)
    if ym2 and not year:
        year = ym2.group(1)
        title = title[: ym2.start()].strip()
    return title, year, rest.strip()


def extract_role_links(role: dict) -> None:
    """Move bare [Label] tokens out of bullets onto the role, for the company line."""
    links: list[str] = []
    new_bullets: list[str] = []
    for bullet in role["bullets"]:
        out: list[str] = []
        pos = 0
        for m in TOKEN.finditer(bullet):
            if m.group(4):
                out.append(bullet[pos : m.start()])
                pos = m.end()
                if m.group(4) not in links:
                    links.append(m.group(4))
        out.append(bullet[pos:])
        new_bullets.append(re.sub(r"\s{2,}", " ", "".join(out)).strip())
    role["bullets"] = new_bullets
    role["links"] = links


def parse_md(text: str) -> dict:
    model = kit.load_module("resume_model", "resume_model.py")
    data = model.parse(text)
    for role in data["roles"]:
        extract_role_links(role)
    return data


def build_body(paras: list[ET.Element], data: dict, rels: RelManager) -> list[ET.Element]:
    out: list[ET.Element] = []
    skills = data["skills"]

    def add(key: str, mutator) -> None:
        p = clone(paras, key)
        mutator(p)
        out.append(p)

    def spacer() -> None:
        out.append(clone(paras, "spacer"))

    add("name", lambda p: set_name(p, data["name"]))
    add("headline", lambda p: set_plain(p, data["headline"]))
    if data["relocation"]:
        add("relocation", lambda p: set_plain(p, data["relocation"]))
    contact_lines = kit.load_profile()["contact_lines"]
    if contact_lines:
        for idx, line in enumerate(contact_lines):
            add("contact1" if idx == 0 else "contact2", lambda p, l=line: set_contact_line(p, l, rels))
    else:
        for idx, raw in enumerate(data["contacts"]):
            add("contact1" if idx == 0 else "contact2", lambda p, t=raw: set_styled_text(p, t, rels))
    if data["summary"]:
        spacer()
        add("summary", lambda p: set_styled_text(p, auto_bold(data["summary"], skills, "summary"), rels))
        spacer()
    def render_skills() -> None:
        if not data["skills"]:
            return
        add("section", lambda p: set_plain(p, "SKILLS"))
        for skill_line in (l for l in data["skills"].splitlines() if l.strip()):
            add("skills", lambda p, s=skill_line: set_skill_line(p, s))
        spacer()

    def render_experience() -> None:
        if not data["roles"]:
            return
        add("section", lambda p: set_plain(p, "EXPERIENCE"))
        for role in data["roles"]:
            add("role_header", lambda p, r=role: set_tabbed_header(p, r["title"], r["dates"]))
            add("company", lambda p, r=role: set_company_line(p, r, rels))
            about = company_about_text(role.get("company_name", ""), role.get("about", ""))
            if about:
                add("company_about", lambda p, a=about: set_plain(p, a))
            for bullet in role["bullets"]:
                add(
                    "bullet",
                    lambda p, t=bullet, r=role: set_bullet_line(p, t, rels, r["company"], skills),
                )
        spacer()

    def render_education() -> None:
        if not data["education"]:
            return
        add("section", lambda p: set_plain(p, "EDUCATION"))
        for edu in data["education"]:
            add("edu_header", lambda p, d=edu: set_tabbed_header(p, d["degree"], d["dates"]))
            for detail in edu["details"]:
                add("edu_detail", lambda p, t=detail: set_styled_text(p, t, rels))

    def render_extra(key: str, title: str) -> None:
        if not data[key]:
            return
        spacer()
        add("section", lambda p: set_plain(p, title.upper()))
        for line in data[key]:
            if line.startswith("### "):
                add("honor_header", lambda p, t=line[4:]: set_styled_text(p, t, rels))
            elif line.startswith("- "):
                add("bullet", lambda p, t=line[2:]: set_bullet_line(p, t, rels, "", skills))
            else:
                add("honor_body", lambda p, t=line: set_styled_text(p, t, rels))

    renderers = {
        "skills": render_skills,
        "experience": render_experience,
        "education": render_education,
        "honors": lambda: render_extra("honors", "Honors & Awards"),
        "projects": lambda: render_extra("projects", "Projects"),
        "certifications": lambda: render_extra("certifications", "Certifications"),
        "publications": lambda: render_extra("publications", "Publications"),
    }
    default_order = ["skills", "experience", "education", "honors", "projects", "certifications", "publications"]
    order = [k for k in data.get("order") or default_order if k in renderers]
    for key in default_order:
        if key not in order:
            order.append(key)
    for key in order:
        renderers[key]()
    return out


def convert(template: Path, md_path: Path, output: Path) -> None:
    md_text = md_path.read_text(encoding="utf-8")
    md_text = re.sub(r"^<!--.*?-->\s*\n?", "", md_text, flags=re.MULTILINE)
    data = parse_md(md_text)
    with zipfile.ZipFile(template, "r") as zin:
        root = ET.fromstring(zin.read("word/document.xml"))
        rel_root = ET.fromstring(zin.read("word/_rels/document.xml.rels"))
        body = root.find(f".//{W}body")
        assert body is not None
        sect_pr = body.find(w("sectPr"))
        paras = body.findall(w("p"))
        rels = RelManager(rel_root)
        new_paras = build_body(paras, data, rels)
        for child in list(body):
            body.remove(child)
        for p in new_paras:
            body.append(p)
        if sect_pr is not None:
            body.append(sect_pr)
        new_doc = ET.tostring(root, encoding="utf-8", xml_declaration=True)
        new_rels = ET.tostring(rel_root, encoding="utf-8", xml_declaration=True)
        output.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                if item.filename == "word/document.xml":
                    blob = new_doc
                elif item.filename == "word/_rels/document.xml.rels":
                    blob = new_rels
                else:
                    blob = zin.read(item.filename)
                zout.writestr(item, blob)


def _self_check() -> None:
    sample = parse_md("# Test\n**Headline**\n\nOpen to X\n\n---\n\n## Summary\n\nHi.")
    assert sample["name"] == "Test"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Convert resume markdown to formatted docx.")
    parser.add_argument("input", type=Path)
    parser.add_argument("-o", "--output", type=Path)
    parser.add_argument("-t", "--template", type=Path, default=DEFAULT_TEMPLATE)
    args = parser.parse_args(argv)
    output = args.output or args.input.with_suffix(".docx")
    if not args.template.exists() or not args.input.exists():
        return 1
    convert(args.template, args.input, output)
    print(output)
    return 0


if __name__ == "__main__":
    _self_check()
    raise SystemExit(main())
