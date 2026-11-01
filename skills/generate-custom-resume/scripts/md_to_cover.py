#!/usr/bin/env python3
"""Convert a cover letter markdown to docx + linked pdf.

Reuses the resume docx as the style source (fonts, header, hyperlink runs) so the
cover letter matches the resume's styling. Body is plain prose: header block, then one
paragraph per blank-line-separated block, with soft line breaks inside a block.
"""
from __future__ import annotations

import argparse
import copy
import html
import re
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kit  # noqa: E402

md = kit.load_module("md_to_docx", "md_to_docx.py")
links = kit.load_module("resume_links", "resume_links.py")
pdf = kit.load_module("md_to_pdf", "md_to_pdf.py")

TEMPLATE = kit.DEFAULT_TEMPLATE

CSS = """
@page { size: A4; margin: 0.8in 0.9in; }
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: Arial, "Liberation Sans", Helvetica, sans-serif; font-size: 10.5pt; line-height: 1.5; color: #1a1a1a; }
header { text-align: center; margin-bottom: 18px; }
h1 { font-size: 20pt; font-weight: 700; letter-spacing: -0.02em; margin-bottom: 4px; }
.headline { font-size: 10pt; font-weight: 600; color: #333; margin-bottom: 3px; }
.contact { font-size: 9pt; color: #444; }
.contact a { color: #1155cc; text-decoration: underline; }
p { margin-bottom: 12px; }
p a { color: #1155cc; text-decoration: underline; }
"""


def parse_cover(text: str) -> dict:
    text = re.sub(r"^<!--.*?-->\s*\n?", "", text, flags=re.MULTILINE)
    lines = text.splitlines()
    i = 0
    while i < len(lines) and not lines[i].strip():
        i += 1
    name = kit.load_profile().get("name", "")
    headline = ""
    if i < len(lines) and lines[i].startswith("# "):
        name = lines[i][2:].strip()
        i += 1
        while i < len(lines) and lines[i].strip() != "---":
            s = lines[i].strip()
            if s.startswith("**") and not headline:
                headline = re.sub(r"\*\*(.+?)\*\*", r"\1", s).strip()
            i += 1
        if i == len(lines):
            raise ValueError("Cover letter header requires a --- separator before the body")
        i += 1
    blocks: list[list[str]] = []
    cur: list[str] = []
    for ln in lines[i:]:
        if ln.strip():
            cur.append(ln.rstrip())
        elif cur:
            blocks.append(cur)
            cur = []
    if cur:
        blocks.append(cur)
    if not blocks or not any(re.search(r"\w", line) for block in blocks for line in block):
        raise ValueError("Cover letter body is empty")
    if not name.strip():
        raise ValueError("Cover letter needs a name in the profile or # Name header")
    return {"name": name, "headline": headline, "blocks": blocks}


# --- docx ---------------------------------------------------------------


def _append_styled(p, text, rels, normal, bold, href) -> None:
    pos = 0
    for m in md.TOKEN.finditer(text):
        if m.start() > pos:
            md.add_run(p, text[pos : m.start()], normal)
        if m.group(1):
            md.add_run(p, m.group(1), bold)
        elif m.group(2):
            md.add_hyperlink(p, m.group(2), m.group(3), href, rels)
        else:
            label = m.group(4)
            url = links.resolve_link(label)
            if url:
                md.add_hyperlink(p, label, url, href, rels)
            else:
                md.add_run(p, f"[{label}]", normal)
        pos = m.end()
    if pos < len(text):
        md.add_run(p, text[pos:], normal)


def _add_break(p, rpr) -> None:
    r = ET.SubElement(p, md.w("r"))
    if rpr is not None:
        r.append(copy.deepcopy(rpr))
    ET.SubElement(r, md.w("br"))


def _set_contact(p, rels) -> None:
    # The cover letter puts every profile contact on one line.
    md.set_contact_line(p, kit.contact_items(), rels, sep="  |  ")


def _set_block(p, block, rels) -> None:
    normal = md.either(md.first_rpr(p, bold=False), md.first_rpr(p))
    bold = md.either(md.first_rpr(p, bold=True), normal)
    href = md.either(md.link_rpr(p), normal)
    md.clear_runs(p)
    for idx, line in enumerate(block):
        if idx:
            _add_break(p, normal)
        _append_styled(p, line, rels, normal, bold, href)


def _build(paras, data, rels) -> list:
    out = []
    name_p = md.clone(paras, "name")
    md.set_name(name_p, data["name"])
    out.append(name_p)
    if data["headline"]:
        h = md.clone(paras, "headline")
        md.set_plain(h, data["headline"])
        out.append(h)
    contact_p = md.clone(paras, "contact1")
    _set_contact(contact_p, rels)
    out.append(contact_p)
    out.append(md.clone(paras, "spacer"))
    for block in data["blocks"]:
        p = md.clone(paras, "summary")
        _set_block(p, block, rels)
        out.append(p)
        out.append(md.clone(paras, "spacer"))
    return out


def convert_docx(template: Path, md_path: Path, output: Path) -> None:
    data = parse_cover(md_path.read_text(encoding="utf-8"))
    with zipfile.ZipFile(template, "r") as zin:
        root = ET.fromstring(zin.read("word/document.xml"))
        rel_root = ET.fromstring(zin.read("word/_rels/document.xml.rels"))
        body = root.find(f".//{md.W}body")
        assert body is not None
        sect_pr = body.find(md.w("sectPr"))
        paras = body.findall(md.w("p"))
        rels = md.RelManager(rel_root)
        new = _build(paras, data, rels)
        for child in list(body):
            body.remove(child)
        for p in new:
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


# --- pdf ----------------------------------------------------------------


def _inline_html(text: str) -> str:
    out: list[str] = []
    pos = 0
    for m in links.TOKEN.finditer(text):
        if m.start() > pos:
            out.append(html.escape(text[pos : m.start()]))
        if m.group(1):
            out.append(f"<strong>{html.escape(m.group(1))}</strong>")
        elif m.group(2):
            out.append(links.anchor_tag(m.group(3), m.group(2)))
        else:
            label = m.group(4)
            url = links.resolve_link(label)
            out.append(links.anchor_tag(url, label) if url else html.escape(f"[{label}]"))
        pos = m.end()
    if pos < len(text):
        out.append(html.escape(text[pos:]))
    return "".join(out)


def render_html(data: dict) -> str:
    contact = links.contact_line_html(kit.contact_items(), sep="  |  ")
    parts = [
        "<!DOCTYPE html><html lang='en'><head><meta charset='UTF-8' />",
        '<base target="_blank" />',
        f"<style>{CSS}</style></head><body><header>",
        f"<h1>{html.escape(data['name'])}</h1>",
        f"<div class='headline'>{html.escape(data['headline'])}</div>",
        f"<div class='contact'>{contact}</div></header>",
    ]
    for block in data["blocks"]:
        parts.append("<p>" + "<br>".join(_inline_html(ln) for ln in block) + "</p>")
    parts.append("</body></html>")
    return "".join(parts)


def convert_pdf(md_path: Path, output: Path) -> None:
    data = parse_cover(md_path.read_text(encoding="utf-8"))
    output.parent.mkdir(parents=True, exist_ok=True)
    html_path = output.with_suffix(".html")
    html_path.write_text(render_html(data), encoding="utf-8")
    pdf.print_pdf(html_path, output)


def _self_check() -> None:
    data = parse_cover(
        "<!-- x -->\n# A B\n**Head**\ncontact\n\n---\n\nDate\n\nHi,\n\nP1 with **bold**.\n\nBye,\nA B"
    )
    assert data["name"] == "A B"
    assert data["headline"] == "Head"
    assert data["blocks"][0] == ["Date"]
    assert data["blocks"][-1] == ["Bye,", "A B"]
    assert "<strong>bold</strong>" in render_html(data)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Convert cover letter markdown to docx + pdf.")
    parser.add_argument("input", type=Path)
    parser.add_argument("--docx", type=Path)
    parser.add_argument("--pdf", type=Path)
    parser.add_argument("-t", "--template", type=Path, default=TEMPLATE)
    parser.add_argument("--docx-only", action="store_true")
    parser.add_argument("--pdf-only", action="store_true")
    args = parser.parse_args(argv)
    if not args.input.exists() or not args.template.exists():
        return 1
    docx_out = args.docx or args.input.with_suffix(".docx")
    pdf_out = args.pdf or args.input.with_suffix(".pdf")
    if not args.pdf_only:
        convert_docx(args.template, args.input, docx_out)
        print(docx_out)
    if not args.docx_only:
        convert_pdf(args.input, pdf_out)
        print(pdf_out)
    return 0


if __name__ == "__main__":
    _self_check()
    raise SystemExit(main())
