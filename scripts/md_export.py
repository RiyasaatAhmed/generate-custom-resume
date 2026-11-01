#!/usr/bin/env python3
"""Export resume markdown to styled docx and linked pdf."""
from __future__ import annotations

import argparse
import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kit  # noqa: E402

_load = kit.load_module
DEFAULT_TEMPLATE = kit.DEFAULT_TEMPLATE


def count_docx_links(docx_path: Path) -> int:
    ns_w = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
    ns_r = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
    with zipfile.ZipFile(docx_path) as z:
        root = ET.fromstring(z.read("word/document.xml"))
    return sum(1 for _ in root.iter(f"{ns_w}hyperlink"))


def count_pdf_links(html_path: Path) -> int:
    text = html_path.read_text(encoding="utf-8")
    return text.count('href="')


def export(
    md_path: Path,
    docx_path: Path | None,
    pdf_path: Path | None,
    template: Path,
    skip_docx: bool,
    skip_pdf: bool,
    cover: bool = False,
) -> tuple[Path | None, Path | None]:
    docx_out = docx_path or md_path.with_suffix(".docx")
    pdf_out = pdf_path or md_path.with_suffix(".pdf")
    # Every profile contact with a url must survive as a hyperlink.
    min_links = sum(1 for item in kit.contact_items() if item.get("url"))

    if not skip_docx:
        mod = _load("md_to_cover", "md_to_cover.py") if cover else _load("md_to_docx", "md_to_docx.py")
        (mod.convert_docx if cover else mod.convert)(template, md_path, docx_out)
        links = count_docx_links(docx_out)
        if links < min_links:
            raise RuntimeError(f"docx link check failed: expected {min_links}+ hyperlinks, got {links}")

    if not skip_pdf:
        mod = _load("md_to_cover", "md_to_cover.py") if cover else _load("md_to_pdf", "md_to_pdf.py")
        (mod.convert_pdf if cover else mod.convert)(md_path, pdf_out)
        html_path = pdf_out.with_suffix(".html")
        links = count_pdf_links(html_path)
        if links < min_links:
            raise RuntimeError(f"pdf/html link check failed: expected {min_links}+ hrefs, got {links}")

    return (docx_out if not skip_docx else None, pdf_out if not skip_pdf else None)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Export resume markdown to docx (template styling) and linked pdf."
    )
    parser.add_argument("input", type=Path, help="Resume .md file")
    parser.add_argument("--docx", type=Path, help="Output .docx path")
    parser.add_argument("--pdf", type=Path, help="Output .pdf path")
    parser.add_argument(
        "-t",
        "--template",
        type=Path,
        default=DEFAULT_TEMPLATE,
        help=f"Base docx template (default: {DEFAULT_TEMPLATE})",
    )
    parser.add_argument("--cover", action="store_true", help="Export a cover letter (not a resume)")
    parser.add_argument("--docx-only", action="store_true")
    parser.add_argument("--pdf-only", action="store_true")
    args = parser.parse_args(argv)

    if not args.input.exists():
        print(f"Input not found: {args.input}", file=sys.stderr)
        return 1

    template = args.template
    if not template.exists():
        print(f"Template not found: {template}", file=sys.stderr)
        return 1

    try:
        docx_path, pdf_path = export(
            args.input,
            args.docx,
            args.pdf,
            template,
            skip_docx=args.pdf_only,
            skip_pdf=args.docx_only,
            cover=args.cover,
        )
    except (RuntimeError, FileNotFoundError) as exc:
        print(exc, file=sys.stderr)
        return 1

    if docx_path:
        print(docx_path)
    if pdf_path:
        print(pdf_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
