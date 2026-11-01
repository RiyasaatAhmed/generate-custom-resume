#!/usr/bin/env python3
"""Post-export QA for a tailored resume.

1. Parse QA: name, every contact, every job title and every date range survive in the .docx text.
2. Page check: page count, and where page 1 ends / page 2 starts (needs `pip install pypdf`).
3. Wrap check: screenshots the .html at A4 print width so wrapped bullets and skills lines are visible.

Usage: python3 scripts/qa.py applications/<slug>/resume.md
"""
from __future__ import annotations

import argparse
import re
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kit  # noqa: E402

NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
PRINT_WIDTH_PX = 680  # A4 width minus the PDF margins, at 96 dpi


def docx_text(path: Path) -> str:
    with zipfile.ZipFile(path) as z:
        root = ET.fromstring(z.read("word/document.xml"))
    lines = []
    for p in root.iter(NS + "p"):
        text = "".join(n.text for n in p.iter(NS + "t") if n.text)
        if text:
            lines.append(text)
    return "\n".join(lines)


def parse_qa(md_path: Path, docx_path: Path) -> list[str]:
    md = kit.load_module("md_to_docx", "md_to_docx.py")
    raw = re.sub(r"^<!--.*?-->\s*\n?", "", md_path.read_text(encoding="utf-8"), flags=re.MULTILINE)
    data = md.parse_md(raw)
    text = docx_text(docx_path)
    flat = re.sub(r"\s+", " ", text)
    expected = [("name", data["name"])]
    expected += [("contact", item["text"]) for item in kit.contact_items()]
    for role in data["roles"]:
        expected += [("job title", role["title"]), ("date range", role["dates"])]
    return [f"missing {kind}: {value!r}" for kind, value in expected if value and value not in flat]


def page_check(pdf_path: Path) -> str:
    try:
        from pypdf import PdfReader
    except ImportError:
        return "page check skipped (pip install pypdf to enable)"
    reader = PdfReader(str(pdf_path))
    report = [f"pages: {len(reader.pages)}"]
    if len(reader.pages) > 1:
        report.append(f"p1 ends:   {reader.pages[0].extract_text().strip()[-90:]!r}")
        report.append(f"p2 starts: {reader.pages[1].extract_text().strip()[:60]!r}")
    return "\n".join(report)


def wrap_screenshot(html_path: Path, out: Path, height: int) -> None:
    kit.run_chrome(
        "--hide-scrollbars",
        f"--screenshot={out.resolve()}",
        f"--window-size={PRINT_WIDTH_PX},{height}",
        html_path.resolve().as_uri(),
        output=out,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="QA an exported resume (.md with .docx/.pdf/.html beside it).")
    parser.add_argument("input", type=Path, help="Tailored resume .md")
    parser.add_argument("--height", type=int, default=1800, help="Screenshot height in px")
    parser.add_argument("--no-screenshot", action="store_true")
    args = parser.parse_args(argv)

    md_path = args.input
    docx_path, pdf_path, html_path = (md_path.with_suffix(s) for s in (".docx", ".pdf", ".html"))
    for path in (md_path, docx_path, pdf_path, html_path):
        if not path.exists():
            print(f"not found: {path} (run md_export.py first)", file=sys.stderr)
            return 1

    problems = parse_qa(md_path, docx_path)
    print("parse QA: " + ("passed" if not problems else "FAILED"))
    for problem in problems:
        print(f"  - {problem}")
    print(page_check(pdf_path))
    if not args.no_screenshot:
        shot = md_path.with_name(md_path.stem + "-wrap-check.png")
        try:
            wrap_screenshot(html_path, shot, args.height)
        except (RuntimeError, FileNotFoundError) as exc:
            print(f"wrap check screenshot failed: {exc}", file=sys.stderr)
            return 1
        print(f"wrap check screenshot: {shot}")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
