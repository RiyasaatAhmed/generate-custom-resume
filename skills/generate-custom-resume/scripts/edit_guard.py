#!/usr/bin/env python3
"""Compare a draft before and after a style edit and list facts that changed.

A writing skill may improve sentences but must not change numbers, units, links,
emails, quotations, names, or lines the candidate asked to keep verbatim. This script
finds those changes mechanically; the agent then checks each one against the evidence
and reverts anything the sources do not support. It cannot judge meaning: a reworded
claim with the same facts (for example "led" becoming "helped") still needs a read.

Usage:
  python3 scripts/edit_guard.py before.md after.md [--protect "verbatim line"]... [--json]

Exit 0 when nothing changed, 1 when something needs review.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
import re
import sys
import unicodedata
from pathlib import Path

UNITS = (r"%|x\b|×|\+|[kKMB]\b|ms\b|s\b|"
         r"\s(?:ms|seconds?|secs?|minutes?|mins?|min|hours?|hrs?|days?|weeks?|months?|years?|"
         r"pages?|people|engineers|users|clients|customers|squads|teams|countries|languages)\b")
NUMBER = re.compile(r"[$€£]?\d+(?:[.,]\d+)*(?:" + UNITS + r")?")
URL = re.compile(r"https?://[^\s)\]>\"']+")
EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
QUOTE = re.compile(r"[\"“]([^\"”\n]{3,})[\"”]")
NAME = re.compile(r"\b[A-Z][\w.&+-]*[\w+]")


def plain(text: str) -> str:
    """Drop Markdown emphasis and link syntax so formatting changes are not reported."""
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r"\[([^\]]*)\]\(([^)]+)\)", r"\1 \2", text)
    return re.sub(r"\*\*|__|(?<!\w)[*_](?!\s)|(?<!\s)[*_](?!\w)", "", text)


def numbers(text: str) -> Counter:
    return Counter(re.sub(r"\s+", " ", m.group(0)) for m in NUMBER.finditer(text))


SENTENCE_START = re.compile(r"(?:^|[.!?:]\s+|\n\s*(?:[-*•]\s+)?)$")
NAME_SHAPE = re.compile(r".[A-Z0-9.&+]")  # GitHub, HIPAA, Martlet.ai, Next.js, AT&T


def names(text: str) -> Counter:
    """Capitalized terms. At a sentence start only name-shaped ones count, so "See" or
    "The" are ignored; a plain name opening a sentence ("Stripe hired...") is missed."""
    found = Counter()
    for m in NAME.finditer(text):
        word = m.group(0).rstrip(".")
        if len(word) < 2:
            continue
        if SENTENCE_START.search(text[max(0, m.start() - 4):m.start()] if m.start() else "") and not NAME_SHAPE.search(word):
            continue
        found[word] += 1
    return found


def diff(before: Counter, after: Counter, ignore: set[str] = frozenset()) -> dict:
    return {"removed": sorted(k for k in before - after if k.lower() not in ignore),
            "added": sorted(k for k in after - before if k.lower() not in ignore)}


def compare(before: str, after: str, protect: list[str]) -> dict:
    b, a = plain(before), plain(after)
    # A capitalized word that also appears lowercase on the other side is a sentence
    # start ("At" vs "at"), not a name.
    lowercase_words = set(re.findall(r"\b[a-z][\w.&+-]*", b + "\n" + a))
    report = {
        "numbers": diff(numbers(b), numbers(a)),
        "urls": diff(Counter(m.rstrip(".,;") for m in URL.findall(b)), Counter(m.rstrip(".,;") for m in URL.findall(a))),
        "emails": diff(Counter(EMAIL.findall(b)), Counter(EMAIL.findall(a))),
        "quotes": diff(Counter(QUOTE.findall(b)), Counter(QUOTE.findall(a))),
        "names": diff(names(b), names(a), {w.lower() for w in lowercase_words}),
        "protected": [line for line in protect if line in before and line not in after],
    }
    report["ok"] = not report["protected"] and not any(
        value["removed"] or value["added"] for key, value in report.items() if isinstance(value, dict))
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("before", type=Path, help="Draft saved before the edit")
    parser.add_argument("after", type=Path, help="Draft after the edit")
    parser.add_argument("--protect", action="append", default=[],
                        help="A line that must survive verbatim, such as a preferred opener (repeatable)")
    parser.add_argument("--json", action="store_true", help="Print the report as JSON")
    args = parser.parse_args(argv)
    report = compare(args.before.read_text(encoding="utf-8"), args.after.read_text(encoding="utf-8"), args.protect)
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    elif report["ok"]:
        print("No facts changed. Still read the edit for changed meaning, such as led -> helped.")
    else:
        print("Review each change against the evidence; revert any the sources do not support:")
        for line in report["protected"]:
            print(f"  protected line altered or removed: {line!r}")
        for key, value in report.items():
            if isinstance(value, dict):
                for item in value["removed"]:
                    print(f"  {key} removed: {item!r}")
                for item in value["added"]:
                    print(f"  {key} added: {item!r}")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
