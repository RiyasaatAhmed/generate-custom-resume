#!/usr/bin/env python3
"""Create the resume data folder if needed and report what is ready.

Safe to run every time: existing files are never overwritten. The data folder is
$RESUME_KIT_HOME, or ~/resume-kit when unset; it lives outside the installed skill
so agent/plugin updates never touch a candidate's profile or applications.

Usage: python3 scripts/init_kit.py [--json]
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kit  # noqa: E402

STARTER_FILES = {
    "profile.example.json": "profile.json",
    "base-resume.example.md": "base-resume.md",
    "candidate-notes.example.md": "candidate-notes.md",
}
EXAMPLE_NAME = "Jane Doe"


def has_module(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def initialize() -> dict:
    home = kit.data_home()
    profile = kit.profile_dir()
    profile.mkdir(parents=True, exist_ok=True)
    kit.applications_dir().mkdir(parents=True, exist_ok=True)
    created = []
    for source, target in STARTER_FILES.items():
        dest = profile / target
        if not dest.exists():
            shutil.copy(kit.EXAMPLE_PROFILE_DIR / source, dest)
            created.append(str(dest))
    texts = [(profile / name).read_text(encoding="utf-8") for name in STARTER_FILES.values()]
    try:
        chrome = kit.find_chrome()
    except (FileNotFoundError, RuntimeError):
        chrome = None
    return {
        "data_home": str(home),
        "profile_dir": str(profile),
        "applications_dir": str(kit.applications_dir()),
        "skill_dir": str(kit.SKILL_DIR),
        "created": created,
        "profile_is_example": any(EXAMPLE_NAME in text for text in texts),
        "python": sys.version.split()[0],
        "chrome": chrome,
        "pypdf": has_module("pypdf"),
        "pdf_renderer": bool(shutil.which("pdftoppm")) or (has_module("pypdfium2") and has_module("PIL")),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--json", action="store_true", help="Print machine-readable status")
    args = parser.parse_args(argv)
    if sys.version_info < (3, 9):
        print("Python 3.9+ is required", file=sys.stderr)
        return 1
    status = initialize()
    if args.json:
        print(json.dumps(status, indent=2))
        return 0
    print(f"Data folder: {status['data_home']}")
    for path in status["created"]:
        print(f"  created {path}")
    if status["profile_is_example"]:
        print("  profile still contains the fictional example (Jane Doe): replace it with your details")
    print(f"PDF export: {'Chrome at ' + status['chrome'] if status['chrome'] else 'unavailable (install Chrome/Chromium or set CHROME_PATH); DOCX export still works'}")
    print(f"PDF content checks: {'on' if status['pypdf'] else 'off (python3 -m pip install pypdf)'}")
    print(f"PDF page previews: {'on' if status['pdf_renderer'] else 'off (install poppler, or python3 -m pip install pypdfium2 pillow)'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
