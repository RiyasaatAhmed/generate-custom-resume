#!/usr/bin/env python3
"""Helpers for the Phase 4 LinkedIn outreach message.

  bold "Text"        print Text in Unicode mathematical bold (for block headers)
  check <file>       count the message and verify every InMail subject line is <= 120 chars

Usage:
  python3 scripts/outreach.py bold "Design Systems"
  python3 scripts/outreach.py check applications/<slug>/outreach.txt
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

MESSAGE_LIMIT = 900
SUBJECT_LIMIT = 120


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


def check(path: Path) -> int:
    header, message = split_file(path.read_text(encoding="utf-8"))
    subjects = [ln for ln in header if ln.strip() and not ln.lstrip().startswith("//")]
    ok = True
    for subject in subjects:
        n = len(subject)
        flag = "ok" if n <= SUBJECT_LIMIT else "OVER"
        ok &= n <= SUBJECT_LIMIT
        print(f"subject {n:>3} chars [{flag}]: {subject}")
    codepoints = len(message)
    utf8 = len(message.encode("utf-8"))
    flag = "ok" if codepoints < MESSAGE_LIMIT else "OVER"
    ok &= codepoints < MESSAGE_LIMIT
    print(f"message: {codepoints} codepoints [{flag}, limit {MESSAGE_LIMIT}], {utf8} UTF-8 bytes")
    return 0 if ok else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("bold")
    b.add_argument("text", nargs="+")
    c = sub.add_parser("check")
    c.add_argument("file", type=Path)
    args = parser.parse_args(argv)
    if args.cmd == "bold":
        print(bold(" ".join(args.text)))
        return 0
    if not args.file.exists():
        print(f"not found: {args.file}", file=sys.stderr)
        return 1
    return check(args.file)


if __name__ == "__main__":
    raise SystemExit(main())
