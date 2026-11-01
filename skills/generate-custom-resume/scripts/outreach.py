#!/usr/bin/env python3
"""Outreach draft helpers. Nothing here sends a message.

  bold "Text"        print Text in Unicode mathematical bold (optional legacy style)
  check <file>       validate body, subjects, placeholders, submission wording, and length

Usage:
  python3 scripts/outreach.py bold "Design Systems"
  python3 scripts/outreach.py check ~/resume-kit/applications/<id>/outreach/email.txt --channel email
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SUBJECT_LIMIT = 120
# Editorial defaults, not claims about a platform's current limits.
CHANNEL_LIMITS = {"legacy": 899, "connection": 200, "recruiter": 1200,
                  "hiring-manager": 1200, "inmail": 1600, "email": 2400,
                  "referral": 1200, "follow-up": 1000}
PLACEHOLDER = re.compile(r"\[[A-Za-z][^\]\n]*\](?!\()|<[^<>\n]+>|\{\{.*?\}\}")
APPLIED_CLAIM = re.compile(r"\bI(?: have|['’]ve)?\s+(?:already\s+)?(?:applied|submitted)\b|\bmy application\b", re.I)


def bold(s: str) -> str:
    out = []
    for ch in s:
        if "A" <= ch <= "Z":
            out.append(chr(0x1D400 + ord(ch) - ord("A")))
        elif "a" <= ch <= "z":
            out.append(chr(0x1D41A + ord(ch) - ord("a")))
        elif "0" <= ch <= "9":
            out.append(chr(0x1D7CE + ord(ch) - ord("0")))
        else:
            out.append(ch)
    return "".join(out)


def split_file(text: str) -> tuple[list[str], str]:
    """Header block is everything up to the `// ---` line; the message is what follows."""
    lines = text.splitlines()
    for idx, line in enumerate(lines):
        if line.strip() == "// ---":
            return lines[:idx], "\n".join(lines[idx + 1 :]).strip("\n")
    return [], text.strip("\n")


def check(path: Path, channel: str = "legacy", limit: int | None = None,
          draft: bool = False, application: Path | None = None) -> int:
    header, message = split_file(path.read_text(encoding="utf-8"))
    subjects = [ln for ln in header if ln.strip() and not ln.lstrip().startswith("//")]
    problems = []
    budget = limit if limit is not None else CHANNEL_LIMITS[channel]
    if budget < 1:
        problems.append("Message budget must be positive")
    if not re.search(r"\w", message) or not any(ln.strip() and not ln.lstrip().startswith("//") for ln in message.splitlines()):
        problems.append("Message body is empty")
    if channel in ("email", "inmail") and not subjects:
        problems.append(f"{channel} requires a subject above // ---")
    if channel == "connection" and subjects:
        problems.append("Connection notes do not have subjects")
    placeholders = PLACEHOLDER.findall("\n".join(subjects + [message]))
    if placeholders and not draft:
        problems.append("Unresolved placeholders: " + ", ".join(placeholders))
    if APPLIED_CLAIM.search(message):
        record = json.loads(application.read_text(encoding="utf-8")) if application else {}
        if not record.get("applied_at"):
            problems.append("Post-application wording requires a confirmed applied_at in --application")
    for subject in subjects:
        n = len(subject)
        flag = "ok" if n <= SUBJECT_LIMIT else "OVER"
        if n > SUBJECT_LIMIT:
            problems.append(f"Subject exceeds {SUBJECT_LIMIT} characters")
        print(f"subject {n:>3} chars [{flag}]: {subject}")
    codepoints = len(message)
    utf8 = len(message.encode("utf-8"))
    if codepoints > budget:
        problems.append(f"Message exceeds {budget} codepoints")
    print(f"message: {codepoints} codepoints, {utf8} UTF-8 bytes; {channel} editorial budget: {budget}")
    print("These are local counts; verify the destination's current counter before sending.")
    for problem in problems:
        print(f"FAILED: {problem}")
    if not problems:
        print("Draft checks passed; unresolved details still need review." if draft else "Content checks passed; verify recipient and review before sending.")
    return 1 if problems else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("bold")
    b.add_argument("text", nargs="+")
    c = sub.add_parser("check")
    c.add_argument("file", type=Path)
    c.add_argument("--channel", choices=CHANNEL_LIMITS, default="legacy")
    c.add_argument("--limit", type=int, help="Maximum length in codepoints, replacing the channel default")
    c.add_argument("--draft", action="store_true", help="Allow unresolved placeholders; the message is not ready to send")
    c.add_argument("--application", type=Path, help="The application.json whose applied_at confirms submission; required for 'I have applied' wording")
    args = parser.parse_args(argv)
    if args.cmd == "bold":
        print(bold(" ".join(args.text)))
        return 0
    if not args.file.exists():
        print(f"not found: {args.file}", file=sys.stderr)
        return 1
    try:
        return check(args.file, args.channel, args.limit, args.draft, args.application)
    except (OSError, ValueError) as exc:
        print(exc, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
