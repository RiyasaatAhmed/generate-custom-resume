"""Hyperlink registry and auto-bold rules, driven by profile/profile.json."""
from __future__ import annotations

import html
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kit  # noqa: E402

TOKEN = re.compile(r"\*\*(.+?)\*\*|\[([^\]]+)\]\(([^)]+)\)|\[([^\]]+)\]")

METRIC_PATTERNS = [
    r"\d+\.?\d*\s*%",
    r"\d+,\d+\+",
    r"\d+\+",
    r"\d+x\b",
    r"\d+K(?:-page)?\b",
    r"\d+\s*minutes?",
    r"\d+\s*→\s*\d+",
]


def _lookup(table: dict, company: str) -> str | None:
    for key, value in table.items():
        if key in company:
            return value
    return None


def company_project_url(company: str) -> str | None:
    return _lookup(kit.load_profile()["company_projects"], company)


def company_website_url(company: str) -> str | None:
    return _lookup(kit.load_profile()["company_websites"], company)


def company_about_text(company: str, override: str = "") -> str:
    if override:
        return override
    return _lookup(kit.load_profile()["company_about"], company) or ""


def contact_url(label: str) -> str | None:
    for item in kit.contact_items():
        if item.get("text") == label:
            return item.get("url")
    return None


def resolve_link(label: str, company: str = "") -> str | None:
    if label == "View Project":
        return company_project_url(company)
    return kit.load_profile()["link_labels"].get(label) or contact_url(label)


def _merge_spans(spans: list[tuple[int, int]]) -> list[tuple[int, int]]:
    if not spans:
        return []
    spans = sorted(spans)
    merged = [spans[0]]
    for start, end in spans[1:]:
        prev_start, prev_end = merged[-1]
        if start <= prev_end:
            merged[-1] = (prev_start, max(prev_end, end))
        else:
            merged.append((start, end))
    return merged


def _skill_terms(skills: str) -> list[str]:
    terms: list[str] = []
    for line in skills.splitlines():
        # "Frontend: react, next.js" -> only the items, never the label
        items = line.split(":", 1)[1] if ":" in line else line
        terms.extend(t.strip() for t in items.split(",") if len(t.strip()) > 2)
    return terms


def _boldify_plain(text: str, skills: str = "", kind: str = "bullet") -> str:
    profile = kit.load_profile()
    patterns: list[str] = list(METRIC_PATTERNS)
    if kind == "summary":
        patterns.extend(profile["summary_bold_phrases"])
    terms = list(profile["bold_terms"]) + _skill_terms(skills)
    for term in sorted(set(terms), key=len, reverse=True):
        # word-boundary lookarounds stop short terms (rag, sql, git)
        # from matching inside larger words (pragmatic, postgresql, digital)
        pat = re.escape(term).replace(r"\ ", r"\s+")
        patterns.append(rf"(?<!\w){pat}(?!\w)")
    spans: list[tuple[int, int]] = []
    for pat in patterns:
        for m in re.finditer(pat, text, re.IGNORECASE):
            spans.append((m.start(), m.end()))
    if not spans:
        return text
    out: list[str] = []
    cursor = 0
    for start, end in _merge_spans(spans):
        if start > cursor:
            out.append(text[cursor:start])
        out.append(f"**{text[start:end]}**")
        cursor = end
    out.append(text[cursor:])
    return "".join(out)


def auto_bold(text: str, skills: str = "", kind: str = "bullet") -> str:
    """Wrap metrics, stack terms, and summary phrases in ** for styled export.

    Disabled with `"auto_bold": false` in the profile; manual **bold** in the .md always renders.
    """
    if not kit.load_profile()["auto_bold"]:
        return text
    parts: list[str] = []
    pos = 0
    for m in TOKEN.finditer(text):
        if m.start() > pos:
            parts.append(_boldify_plain(text[pos : m.start()], skills, kind))
        if m.group(1):
            parts.append(f"**{m.group(1)}**")
        else:
            parts.append(m.group(0))
        pos = m.end()
    if pos < len(text):
        parts.append(_boldify_plain(text[pos:], skills, kind))
    return "".join(parts)


def anchor_tag(url: str, label: str) -> str:
    attrs = (
        ' target="_blank" rel="noopener noreferrer"'
        if url.startswith(("http://", "https://"))
        else ""
    )
    return f'<a href="{html.escape(url, quote=True)}"{attrs}>{html.escape(label)}</a>'


def contact_line_html(line: list[dict], sep: str = " | ") -> str:
    parts = []
    for item in line:
        icon = f"{item['icon']} " if item.get("icon") else ""
        text = item["text"]
        parts.append(icon + (anchor_tag(item["url"], text) if item.get("url") else html.escape(text)))
    return sep.join(parts)


def inline_to_html(text: str, company: str = "", skills: str = "", kind: str = "bullet") -> str:
    text = auto_bold(text, skills, kind)
    out: list[str] = []
    pos = 0
    for m in TOKEN.finditer(text):
        if m.start() > pos:
            out.append(html.escape(text[pos : m.start()]))
        if m.group(1):
            out.append(f"<strong>{html.escape(m.group(1))}</strong>")
        elif m.group(2):
            label, url = m.group(2), m.group(3)
            out.append(anchor_tag(url, label))
        else:
            label = m.group(4)
            display = f"[{label}]"
            url = resolve_link(label, company)
            if url:
                out.append(anchor_tag(url, display))
            else:
                out.append(html.escape(display))
        pos = m.end()
    if pos < len(text):
        out.append(html.escape(text[pos:]))
    return "".join(out)
