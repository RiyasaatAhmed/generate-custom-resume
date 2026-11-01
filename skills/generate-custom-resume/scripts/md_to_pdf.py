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
        (f"<section><h2>Summary</h2><p class='summary'>{links.inline_to_html(data['summary'], skills=skills, kind='summary')}</p></section>" if data["summary"] else ""),
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
        education_parts.append("<section><h2>Education</h2>")
        for edu in data["education"]:
            education_parts.append(
                f"<div class='role'><div class='role-header'>"
                f"<span class='role-title'>{html.escape(edu['degree'])}</span>"
                f"<span class='role-date'>{html.escape(edu['dates'])}</span></div>"
            )
            for detail in edu["details"]:
                education_parts.append(f"<div>{links.inline_to_html(detail)}</div>")
            education_parts.append("</div>")
        education_parts.append("</section>")

    def extra_section(key: str, title: str) -> list[str]:
        if not data[key]:
            return []
        result = [f"<section><h2>{html.escape(title)}</h2>"]
        for line in data[key]:
            if line.startswith("### "):
                result.append(f"<div class='honor-title'>{links.inline_to_html(line[4:])}</div>")
            elif line.startswith("- "):
                result.append(f"<div>• {links.inline_to_html(line[2:])}</div>")
            else:
                result.append(f"<div>{links.inline_to_html(line)}</div>")
        return result + ["</section>"]

    blocks = {
        "skills": skills_parts if data["skills"] else [],
        "experience": experience_parts if data["roles"] else [],
        "education": education_parts,
        "honors": extra_section("honors", "Honors & Awards"),
        "projects": extra_section("projects", "Projects"),
        "certifications": extra_section("certifications", "Certifications"),
        "publications": extra_section("publications", "Publications"),
    }
    default_order = ["skills", "experience", "education", "honors", "projects", "certifications", "publications"]
    order = [k for k in data.get("order") or default_order if k in blocks]
    for key in default_order:
        if key not in order:
            order.append(key)
    for key in order:
        parts.extend(blocks[key])

    parts.append("</body></html>")
    return "".join(parts)


def print_pdf(html_path: Path, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    kit.run_chrome(
        "--no-pdf-header-footer", f"--print-to-pdf={output.resolve()}", html_path.resolve().as_uri(), output=output
    )


def convert(md_path: Path, output: Path) -> None:
    md_mod = kit.load_module("md_to_docx", "md_to_docx.py")
    links = kit.load_module("resume_links", "resume_links.py")
    text = md_path.read_text(encoding="utf-8")
    text = re.sub(r"^<!--.*?-->\s*\n?", "", text, flags=re.MULTILINE)
    data = md_mod.parse_md(text)
    output.parent.mkdir(parents=True, exist_ok=True)
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
