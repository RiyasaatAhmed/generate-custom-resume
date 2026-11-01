#!/usr/bin/env python3
"""Generate linked resume PDF from markdown via HTML + Chrome headless."""
from __future__ import annotations

import argparse
import html
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kit  # noqa: E402

CSS = """
@page { size: A4; margin: 0.55in 0.6in; }
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: "Helvetica Neue", Helvetica, Arial, sans-serif; font-size: 9.5pt; line-height: 1.35; color: #1a1a1a; }
h1 { font-size: 20pt; font-weight: 700; letter-spacing: -0.02em; margin-bottom: 4px; }
.headline { font-size: 10pt; font-weight: 600; color: #333; margin-bottom: 3px; text-align: center; }
.meta, .contact { font-size: 9pt; color: #444; text-align: center; }
.contact a, li a, .honor a, .company a { color: #1155cc; text-decoration: underline; }
section { margin-top: 10px; }
h2 { font-size: 10pt; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; border-bottom: 1px solid #ccc; padding-bottom: 2px; margin-bottom: 6px; }
.summary { text-align: justify; }
.skills { font-size: 9.5pt; line-height: 1.4; }
.role { margin-bottom: 8px; break-inside: avoid; }
.role-header { display: flex; justify-content: space-between; align-items: baseline; gap: 12px; margin-bottom: 2px; }
.role-title { font-weight: 700; font-size: 9.5pt; }
.role-date { font-size: 9pt; white-space: nowrap; color: #444; }
.company { font-size: 9pt; color: #333; margin-bottom: 2px; display: flex; justify-content: space-between; align-items: baseline; gap: 12px; }
.company-links { white-space: nowrap; }
.company-about { font-size: 8.5pt; color: #555; font-style: italic; margin-bottom: 3px; }
ul { list-style: none; padding-left: 0; margin: 0; }
li { display: flex; align-items: flex-start; margin-bottom: 2px; }
.bullet { flex: 0 0 auto; margin-right: 0.3em; }
.bullet-body { flex: 1; min-width: 0; }
.honor { margin-bottom: 4px; }
.honor-title { font-weight: 600; }
header { text-align: center; }
"""


def company_line_html(company: str, company_name: str, links) -> str:
    url = links.company_website_url(company_name)
    if not url:
        return html.escape(company)
    suffix = company[len(company_name) :]
    return links.anchor_tag(url, company_name) + html.escape(suffix)


def render_html(data: dict, links, parse_honor) -> str:
    skills = data["skills"]
    contact_lines = kit.load_profile()["contact_lines"]
    if contact_lines:
        contacts = [links.contact_line_html(line) for line in contact_lines]
    else:
        contacts = [links.inline_to_html(raw) for raw in data["contacts"]]
    meta = f"<div class='meta'>{html.escape(data['relocation'])}</div>" if data["relocation"] else ""
    parts = [
        "<!DOCTYPE html><html lang='en'><head><meta charset='UTF-8' />",
        f"<title>{html.escape(data['name'])} Resume</title>",
        '<base target="_blank" />',
        f"<style>{CSS}</style></head><body><header>",
        f"<h1>{html.escape(data['name'])}</h1>",
        f"<div class='headline'>{html.escape(data['headline'])}</div>",
        meta,
        *(f"<div class='contact'>{c}</div>" for c in contacts),
        "</header>",
        f"<section><h2>Summary</h2><p class='summary'>{links.inline_to_html(data['summary'], skills=skills, kind='summary')}</p></section>",
    ]

    skills_parts = [
        f"<section><h2>Skills</h2><p class='skills'>{'<br/>'.join(('<strong>' + html.escape(line.split(':', 1)[0]) + ':</strong>' + html.escape(line.split(':', 1)[1]) if ':' in line else html.escape(line)) for line in data['skills'].splitlines() if line.strip())}</p></section>",
    ]

    experience_parts = ["<section><h2>Experience</h2>"]
    for role in data["roles"]:
        about = links.company_about_text(role.get("company_name", ""), role.get("about", ""))
        company_html = f"<span>{company_line_html(role['company'], role.get('company_name', ''), links)}</span>"
        link_labels = role.get("links") or []
        if link_labels:
            rendered = []
            for label in link_labels:
                url = links.resolve_link(label, role["company"])
                display = f"[{label}]"
                rendered.append(links.anchor_tag(url, display) if url else html.escape(display))
            company_html += f"<span class='company-links'>{' '.join(rendered)}</span>"
        experience_parts.append(
            f"<div class='role'><div class='role-header'>"
            f"<span class='role-title'>{html.escape(role['title'])}</span>"
            f"<span class='role-date'>{html.escape(role['dates'])}</span></div>"
            f"<div class='company'>{company_html}</div>"
        )
        if about:
            experience_parts.append(f"<div class='company-about'>{html.escape(about)}</div>")
        experience_parts.append("<ul>")
        for bullet in role["bullets"]:
            body = bullet[1:].strip() if bullet.startswith("•") else bullet
            experience_parts.append(
                "<li><span class='bullet'>•</span>"
                f"<span class='bullet-body'>{links.inline_to_html(body, role['company'], skills)}</span></li>"
            )
        experience_parts.append("</ul></div>")
    experience_parts.append("</section>")

    education_parts = []
    if data["education"]:
        edu = data["education"]
        education_parts.append(
            f"<section><h2>Education</h2><div class='role-header'>"
            f"<span class='role-title'>{html.escape(edu['degree'])}</span>"
            f"<span class='role-date'>{html.escape(edu['dates'])}</span></div>"
            f"<div class='company'>{html.escape(edu['detail'])}</div></section>"
        )

    honors_parts = []
    if data["honors"]:
        honors_parts.append("<section><h2>Honors &amp; Awards</h2>")
    for entry in data["honors"]:
        title, year, rest = parse_honor(entry[0])
        suffix = f" ({year})" if year and year not in title else ""
        honors_parts.append(
            f"<div class='honor'><div class='honor-title'>"
            f"{links.inline_to_html(title, skills=skills)}{html.escape(suffix)}</div>"
        )
        if rest:
            honors_parts.append(f"<div>{links.inline_to_html(rest, skills=skills)}</div>")
        for extra in entry[1:]:
            honors_parts.append(f"<div>{links.inline_to_html(extra, skills=skills)}</div>")
        honors_parts.append("</div>")
    if data["honors"]:
        honors_parts.append("</section>")

    blocks = {
        "skills": skills_parts,
        "experience": experience_parts,
        "education": education_parts,
        "honors": honors_parts,
    }
    default_order = ["skills", "experience", "education", "honors"]
    order = [k for k in data.get("order") or default_order if k in blocks]
    for key in default_order:
        if key not in order:
            order.append(key)
    for key in order:
        parts.extend(blocks[key])

    parts.append("</body></html>")
    return "".join(parts)


def patch_pdf_links_new_tab(pdf_path: Path) -> None:
    # ponytail: regex patch on Chrome headless URI actions; breaks if print format changes
    pattern = rb"/A <</Type /Action\n/S /URI\n/URI \(([^)]+)\)>>"

    def repl(m: re.Match[bytes]) -> bytes:
        url = m.group(1)
        if not url.startswith((b"http://", b"https://")):
            return m.group(0)
        return b"/A <</Type /Action\n/S /URI\n/URI (" + url + b")\n/NewWindow true>>"

    data = pdf_path.read_bytes()
    patched = re.sub(pattern, repl, data)
    if re.search(pattern, data) and b"NewWindow" not in patched:
        raise RuntimeError("PDF link patch failed: no NewWindow flags written")
    pdf_path.write_bytes(rebuild_xref(patched))


def rebuild_xref(data: bytes) -> bytes:
    """Recompute the xref table after the link patch shifted object offsets.

    Chrome writes one classic xref table with a single subsection, so every object
    offset can be re-read from its `N 0 obj` header. Without this, strict PDF parsers
    (some ATS uploads among them) see a broken file.
    """
    xref_at = data.rfind(b"\nxref\n")
    if xref_at < 0:
        return data
    xref_at += 1
    header = re.match(rb"xref\n0 (\d+)\n", data[xref_at:])
    trailer_at = data.find(b"trailer", xref_at)
    if not header or trailer_at < 0:
        return data
    size = int(header.group(1))
    offsets = {int(m.group(1)): m.start() for m in re.finditer(rb"(?m)^(\d+) 0 obj\b", data[:xref_at])}
    rows = [b"0000000000 65535 f \n"]
    for num in range(1, size):
        rows.append(b"%010d 00000 n \n" % offsets[num] if num in offsets else b"0000000000 65535 f \n")
    trailer = data[trailer_at:]
    trailer = re.sub(rb"startxref\n\d+", b"startxref\n%d" % xref_at, trailer)
    return data[:xref_at] + b"xref\n0 %d\n" % size + b"".join(rows) + trailer


def print_pdf(html_path: Path, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    kit.run_chrome(
        "--no-pdf-header-footer", f"--print-to-pdf={output.resolve()}", html_path.resolve().as_uri(), output=output
    )
    patch_pdf_links_new_tab(output)


def convert(md_path: Path, output: Path) -> None:
    md_mod = kit.load_module("md_to_docx", "md_to_docx.py")
    links = kit.load_module("resume_links", "resume_links.py")
    text = md_path.read_text(encoding="utf-8")
    text = re.sub(r"^<!--.*?-->\s*\n?", "", text, flags=re.MULTILINE)
    data = md_mod.parse_md(text)
    html_path = output.with_suffix(".html")
    html_path.write_text(render_html(data, links, md_mod.parse_honor), encoding="utf-8")
    print_pdf(html_path, output)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Convert resume markdown to linked PDF.")
    parser.add_argument("input", type=Path)
    parser.add_argument("-o", "--output", type=Path)
    args = parser.parse_args(argv)
    output = args.output or args.input.with_suffix(".pdf")
    if not args.input.exists():
        return 1
    convert(args.input, output)
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
