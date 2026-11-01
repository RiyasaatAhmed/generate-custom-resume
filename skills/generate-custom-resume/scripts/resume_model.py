"""Strict, shared model for the supported resume Markdown dialect.

Unknown sections and unconsumed structural content are errors, never omissions.
Renderers own styling; this module owns input interpretation.
"""
from __future__ import annotations

import re

SECTION_NAMES = {
    "summary": "summary", "skills": "skills", "experience": "experience",
    "work experience": "experience", "education": "education",
    "honors": "honors", "honors & awards": "honors", "honors and awards": "honors",
    "projects": "projects", "certifications": "certifications", "publications": "publications",
}
EXTRA_SECTIONS = ("projects", "certifications", "publications")


def clean_source(text: str) -> str:
    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
    if "<!--" in text or "-->" in text:
        raise ValueError("Unclosed HTML comment in resume")
    return text.strip()


def plain(text: str) -> str:
    return re.sub(r"\*\*(.+?)\*\*", r"\1", text).strip()


# An email, URL, Markdown link, or bare domain marks a header row as contact details.
# ".js" is excluded so a technology like Next.js is not read as a website.
CONTACT_HINT = re.compile(r"@|https?://|\]\(|\b[\w-]+\.(?!js\b)[a-z]{2,}\b", re.I)


def is_contact_row(line: str) -> bool:
    return bool(CONTACT_HINT.search(line))


def parse(text: str) -> dict:
    lines = clean_source(text).splitlines()
    if not lines or not re.fullmatch(r"#\s+\S.*", lines[0]):
        raise ValueError("Resume must start with # Full Name")
    data = dict(name=lines[0][2:].strip(), headline="", relocation="", contacts=[],
                summary="", skills="", roles=[], education=[], honors=[], order=[],
                projects=[], certifications=[], publications=[])
    sections: dict[str, list[str]] = {}
    current = None
    for number, raw in enumerate(lines[1:], 2):
        line = raw.strip()
        if not line or line == "---":
            continue
        if line.startswith("## "):
            label = line[3:].strip().lower()
            if label not in SECTION_NAMES:
                raise ValueError(f"Line {number}: unsupported section {label!r}")
            current = SECTION_NAMES[label]
            if current in sections:
                raise ValueError(f"Line {number}: duplicate section {label!r}")
            sections[current] = []
            if current != "summary":
                data["order"].append(current)
        elif current is None:
            if re.fullmatch(r"\*\*.+\*\*", line) and not data["headline"]:
                data["headline"] = plain(line)
            elif is_contact_row(line):
                data["contacts"].append(line)
            elif not data["relocation"] and not line.startswith("#"):
                data["relocation"] = line  # may use | separators: "Lisbon | EU hours"
            elif "|" in line:
                data["contacts"].append(line)  # label-only row after the location: "LinkedIn | GitHub"
            else:
                raise ValueError(f"Line {number}: unrecognized header content {line!r}")
        else:
            if line.startswith(("|", "```", "####", "# ")):
                raise ValueError(f"Line {number}: unsupported Markdown structure {line!r}")
            sections[current].append(line)
    if not data["headline"]:
        raise ValueError("Resume needs a **headline** below the name")
    if not sections:
        raise ValueError("Resume needs at least one supported section")
    for key, body in sections.items():
        if not body:
            raise ValueError(f"Empty section: {key}")
        if key in ("summary", "skills"):
            if any(line.startswith(("#", "- ")) for line in body):
                raise ValueError(f"{key.title()} must contain plain paragraphs or category lines")
            data[key] = (" " if key == "summary" else "\n").join(body)
        elif key == "experience":
            data["roles"] = parse_roles(body)
        elif key == "education":
            data[key] = parse_education(body)
        else:
            data[key] = body
    return data


def parse_roles(lines: list[str]) -> list[dict]:
    roles: list[dict] = []
    role = None
    for line in lines:
        if line.startswith("### "):
            role = dict(title=line[4:].strip(), company="", company_name="", about="", dates="", bullets=[])
            if not role["title"]:
                raise ValueError("Empty experience title")
            roles.append(role)
        elif role is None:
            raise ValueError("Experience content must follow a ### Job Title")
        elif not role["company"]:
            match = re.fullmatch(r"\*\*(.+?)\*\*(?:,\s*(.+?))?\s*\|\s*(\S.*)", line)
            if not match:
                raise ValueError(f"Expected **Company**, Location | Dates after {role['title']!r}")
            name, location, dates = match.groups()
            role.update(company_name=name, company=name + (f", {location}" if location else ""), dates=dates)
        elif line.startswith("- "):
            if not line[2:].strip():
                raise ValueError("Empty experience bullet")
            role["bullets"].append(line[2:].strip())
        elif not role["about"] and not role["bullets"] and not line.startswith("#"):
            role["about"] = line
        else:
            raise ValueError(f"Unrecognized experience line: {line!r}; bullets must start with '- '")
    for item in roles:
        if not item["company"]:
            raise ValueError(f"Missing company/dates for {item['title']!r}")
    return roles


def parse_education(lines: list[str]) -> list[dict]:
    entries: list[dict] = []
    for line in lines:
        if not entries or line.startswith(("**", "### ")):
            header = line.removeprefix("### ")
            degree, sep, dates = header.partition("|")
            entries.append({"degree": plain(degree), "dates": dates.strip() if sep else "", "details": []})
        else:
            entries[-1]["details"].append(line)
    return entries
