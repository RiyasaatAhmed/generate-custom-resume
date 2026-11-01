#!/usr/bin/env python3
"""Print the plain text of one or more .docx files (for reading an existing resume).

Usage: python3 scripts/docx_text.py path/to/resume.docx [more.docx ...]
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kit  # noqa: E402

qa = kit.load_module("qa", "qa.py")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__.strip(), file=sys.stderr)
        raise SystemExit(1)
    for arg in sys.argv[1:]:
        print(f"=== {arg} ===\n{qa.docx_text(Path(arg))}\n")
