"""Source-driven export checks independent of the renderer's content model."""
from __future__ import annotations
from collections import Counter
from pathlib import Path
import re
import unicodedata
import xml.etree.ElementTree as ET
import zipfile
import kit
import resume_links
import resume_model

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
R = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", text)).strip()


def visible(text: str) -> str:
    return resume_links.TOKEN.sub(lambda m: m.group(1) or m.group(2) or "", text).strip()


def source_inventory(path: Path, cover: bool = False) -> tuple[list[str], set[tuple[str, str]]]:
    """Inventory raw source lines, not fields returned by the export parser.

    Profile contacts replace source header contact rows. Bare link labels can move
    to company rows and are therefore checked separately from bullet sentences.
    """
    raw = resume_model.clean_source(path.read_text(encoding="utf-8"))
    fragments: list[str] = []
    targets: set[tuple[str, str]] = set()
    contact_rows: set[str] = set()
    profile = kit.load_profile()
    for item in kit.contact_items():
        fragments.append(item["text"])
        if item.get("url"):
            targets.add((item["text"], item["url"]))
    if cover:
        parser = kit.load_module("md_to_cover", "md_to_cover.py")
        data = parser.parse_cover(raw)
        fragments.extend([data["name"], data["headline"]])
        lines = [line for block in data["blocks"] for line in block]
    else:
        # Profile contacts replace exactly the rows the parser classed as contacts; every
        # other header line, including a location written with | separators, must survive.
        contact_rows = set(resume_model.parse(raw)["contacts"])
        lines = raw.splitlines()
    in_header = not cover
    company = ""
    for raw_line in lines:
        line = raw_line.strip()
        if not line or line == "---":
            continue
        if line.startswith("## "):
            in_header = False
            company = ""
            continue
        if in_header and not cover and line in contact_rows and profile["contact_lines"]:
            continue
        if line.startswith("### "):
            company = ""
        company_match = re.match(r"\*\*(.+?)\*\*(?:,.*?)?\s*\|", line)
        if company_match and not in_header:
            company = company_match.group(1)
            url = resume_links.company_website_url(company)
            if url:
                targets.add((company, url))
            about = resume_links.company_about_text(company)
            if about:
                fragments.append(about)
        for match in resume_links.TOKEN.finditer(line):
            if match.group(2):
                targets.add((match.group(2), match.group(3)))
            elif match.group(4):
                label = match.group(4)
                url = resume_links.resolve_link(label, company)
                if not url:
                    raise ValueError(f"Unresolved link token [{label}]; add its URL to the profile")
                targets.add((label, url))
                fragments.append(f"[{label}]")
        line = re.sub(r"^(?:#{1,3}\s+|-\s+)", "", line)
        fragments.extend(part.strip() for part in visible(line).split("|") if part.strip())
    return [fragment for fragment in fragments if fragment], targets


def missing_content(expected: list[str], actual: str, ignore_spaces: bool = False) -> list[str]:
    """Report expected fragments that `actual` does not contain often enough.

    PDF text extraction can insert spaces inside a word: pypdf reads some bold digits as
    "9 2%" although the page shows "92%". `ignore_spaces` compares with all whitespace
    removed, so a missing or changed character still fails but stray spacing does not.
    """
    key = (lambda text: re.sub(r"\s+", "", normalize(text))) if ignore_spaces else normalize
    flat = key(actual)
    counts = Counter(key(item) for item in expected)
    shown = {key(item): normalize(item) for item in expected}
    return [f"missing content ({count} occurrence(s)): {shown[text]!r}"
            for text, count in counts.items() if flat.count(text) < count]


def docx_text(path: Path) -> str:
    with zipfile.ZipFile(path) as z:
        root = ET.fromstring(z.read("word/document.xml"))
    rows = []
    for paragraph in root.iter(W + "p"):
        rows.append("".join((node.text or "") if node.tag == W + "t" else " "
                            for node in paragraph.iter() if node.tag in (W + "t", W + "tab", W + "br")))
    return "\n".join(rows)


def docx_links(path: Path) -> set[tuple[str, str]]:
    with zipfile.ZipFile(path) as z:
        document = ET.fromstring(z.read("word/document.xml"))
        rels = ET.fromstring(z.read("word/_rels/document.xml.rels"))
    urls = {rel.get("Id"): rel.get("Target", "") for rel in rels}
    return {(normalize("".join(n.text or "" for n in link.iter(W + "t"))).strip("[]"),
             urls.get(link.get(R + "id"), "")) for link in document.iter(W + "hyperlink")}


def check_docx(source: Path, output: Path, cover: bool = False) -> tuple[list[str], list[str]]:
    fragments, expected_links = source_inventory(source, cover)
    content = missing_content(fragments, docx_text(output))
    actual = docx_links(output)
    links = [f"missing/wrong link: {label!r} -> {url}" for label, url in sorted(expected_links)
             if (normalize(label).strip("[]"), url) not in actual]
    return content, links
