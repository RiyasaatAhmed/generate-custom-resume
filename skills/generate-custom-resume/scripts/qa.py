#!/usr/bin/env python3
"""Validate content, links, page budget and PDF previews; write explicit QA results."""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kit
from document_checks import check_docx, docx_text, missing_content, source_inventory

NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
PRINT_WIDTH_PX = 680


def parse_qa(md_path: Path, docx_path: Path, cover: bool = False) -> list[str]:
    content, links = check_docx(md_path, docx_path, cover)
    return content + links


def result(problems: list[str]) -> dict:
    return {"status": "fail" if problems else "pass", "details": problems}


def same_url(url: str) -> str:
    """Equivalence Chrome applies when printing: lowercase scheme/host, empty web path -> "/".

    Paths, queries, and fragments are compared exactly; a different destination still fails.
    """
    parts = urlsplit(url)
    if parts.scheme.lower() not in ("http", "https"):
        return url
    return urlunsplit((parts.scheme.lower(), parts.netloc.lower(), parts.path or "/", parts.query, parts.fragment))


def pdf_checks(source: Path, pdf_path: Path, max_pages: int, cover: bool = False) -> dict:
    if not pdf_path.is_file():
        raise FileNotFoundError(f"Missing PDF: {pdf_path}")
    try:
        from pypdf import PdfReader
    except ImportError:
        return {key: {"status": "skipped", "details": ["Install pypdf for PDF validation"]}
                for key in ("pdf_content", "pdf_links", "pages")}
    reader = PdfReader(str(pdf_path), strict=True)
    fragments, expected_links = source_inventory(source, cover)
    texts = [page.extract_text() or "" for page in reader.pages]
    urls = set()
    for page in reader.pages:
        for ref in page.get("/Annots", []):
            action = ref.get_object().get("/A")
            if action:
                url = action.get_object().get("/URI")
                if url:
                    urls.add(same_url(str(url)))
    pages = len(reader.pages)
    return {
        "pdf_content": result(missing_content(fragments, "\n".join(texts))),
        "pdf_links": result([f"missing PDF destination: {url}" for url in sorted({url for _, url in expected_links if same_url(url) not in urls})]),
        "pages": {**result([] if 0 < pages <= max_pages else [f"{pages} pages violates policy (1–{max_pages})"]), "count": pages, "limit": max_pages},
    }


def wrap_screenshot(html_path: Path, out: Path, height: int) -> None:
    """Optional HTML preview, not evidence of PDF pagination."""
    kit.run_chrome("--hide-scrollbars", f"--screenshot={out.resolve()}",
                   f"--window-size={PRINT_WIDTH_PX},{height}", html_path.resolve().as_uri(), output=out)


def render_pdf(pdf_path: Path) -> list[Path]:
    digest = hashlib.sha256(pdf_path.read_bytes()).hexdigest()[:12]
    directory = pdf_path.parent / f"{pdf_path.stem}-pages-{digest}"
    renderer = shutil.which("pdftoppm")
    if renderer:
        directory.mkdir(exist_ok=True)
        subprocess.run([renderer, "-scale-to", "1600", "-png", str(pdf_path.resolve()), str(directory / "page")],
                       check=True, capture_output=True, timeout=60)
    else:
        try:
            import pypdfium2
        except ImportError:
            return []
        directory.mkdir(exist_ok=True)
        with pypdfium2.PdfDocument(str(pdf_path)) as document:
            for index in range(len(document)):
                page = document[index]
                bitmap = page.render(scale=1.5)
                try:
                    bitmap.to_pil().save(directory / f"page-{index + 1}.png")
                finally:
                    bitmap.close()
                    page.close()
    return sorted(directory.glob("page-*.png"), key=lambda p: int(re.search(r"(\d+)\.png$", p.name).group(1)))


def run(source: Path, max_pages: int = 2, cover: bool = False, render: bool = True,
        visual_review: str | None = None) -> dict:
    checks = {}
    try:
        content, links = check_docx(source, source.with_suffix(".docx"), cover)
        checks.update(docx_content=result(content), docx_links=result(links))
    except Exception as exc:
        # Malformed ZIP/XML/PDF inputs must produce a report, not a silent pass.
        checks["docx_content"] = result([str(exc)])
    pdf = source.with_suffix(".pdf")
    try:
        checks.update(pdf_checks(source, pdf, max_pages, cover))
    except Exception as exc:
        checks["pdf_content"] = result([str(exc)])
    if render and pdf.exists():
        try:
            images = render_pdf(pdf)
            checks["pdf_render"] = {"status": "pass" if images else "skipped", "details":
                [str(p) for p in images] or ["Install pdftoppm or pypdfium2 + Pillow for actual PDF previews"]}
        except Exception as exc:
            checks["pdf_render"] = result([str(exc)])
    else:
        checks["pdf_render"] = {"status": "skipped", "details": ["PDF rendering not requested or file missing"]}
    reviewed = bool(visual_review and visual_review.strip() and pdf.exists())
    checks["visual_review"] = {"status": "pass" if reviewed else "skipped", "details":
        [visual_review] if reviewed else ["Inspect actual PDF pages for clipping, wrapping, and page breaks"]}
    statuses = {value["status"] for value in checks.values()}
    overall = "failed" if "fail" in statuses else "incomplete" if "skipped" in statuses else "passed"
    return {"schema_version": 1, "source": str(source), "pdf_sha256": hashlib.sha256(pdf.read_bytes()).hexdigest() if pdf.exists() else None,
            "overall": overall, "checks": checks}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--cover", action="store_true")
    parser.add_argument("--max-pages", type=int, default=kit.load_profile().get("resume_max_pages", 2))
    parser.add_argument("--json", type=Path, help="Report path (default: qa.json next to the source)")
    parser.add_argument("--no-screenshot", action="store_true", help="Skip optional PDF rendering")
    parser.add_argument("--html-preview", action="store_true", help="Also screenshot the HTML version; this does not check PDF page breaks")
    parser.add_argument("--height", type=int, default=1800)
    parser.add_argument("--visual-reviewed", help="Record a review you actually did: who looked at every page and what they saw")
    parser.add_argument("--require-complete", action="store_true", help="Exit 2 when any check is skipped")
    args = parser.parse_args(argv)
    if args.max_pages < 1:
        parser.error("--max-pages must be positive")
    report = run(args.input, args.max_pages, args.cover, not args.no_screenshot, args.visual_reviewed)
    if args.html_preview:
        try:
            wrap_screenshot(args.input.with_suffix(".html"), args.input.with_name(args.input.stem + "-html-preview.png"), args.height)
        except Exception as exc:
            report["checks"]["html_preview"] = result([str(exc)])
            report["overall"] = "failed"
    output = args.json or args.input.with_name("qa.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"QA: {report['overall']} ({output})")
    for key, value in report["checks"].items():
        print(f"  {key}: {value['status']}")
        for detail in value["details"]:
            print(f"    {detail}")
    return 1 if report["overall"] == "failed" else 2 if args.require_complete and report["overall"] != "passed" else 0


if __name__ == "__main__":
    raise SystemExit(main())
