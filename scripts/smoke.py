#!/usr/bin/env python3
"""Export fictional resume/extended-resume/letter fixtures in a fresh temp folder."""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import tempfile

import kit
import md_export
import qa


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="Empty output directory; default is a new temporary folder")
    args = parser.parse_args(argv)
    root = args.output or Path(tempfile.mkdtemp(prefix="resume-kit-smoke-"))
    root.mkdir(parents=True, exist_ok=True)
    if any(root.iterdir()):
        parser.error("--output must be empty; smoke tests never overwrite existing files")
    os.environ["RESUME_PROFILE"] = str(kit.KIT_ROOT / "profile/profile.example.json")
    kit.load_profile.cache_clear()
    base = (kit.KIT_ROOT / "profile/base-resume.example.md").read_text(encoding="utf-8")
    extended = base + "\n## Projects\n### Accessible scheduling demo\n"
    extended += "\n".join(f"- Scenario {i}: built a keyboard-accessible appointment flow with clear validation and recovery states for testing." for i in range(1, 19))
    extended += "\n\n## Certifications\n**Example Credential** | 2024\nFictional testing credential.\n\n## Publications\n[Accessibility example](https://example.org/paper)\n"
    fixtures = [("resume", base, False), ("extended", extended, False),
                ("cover-letter", "Dear Engineering Team,\n\nAt Northwind Health, I built a keyboard-first note editor and smart templates that cut clinician charting time 35%.\n\nI would welcome a discussion of your clinical interface role.\n\nBest,\nJane Doe\n", True)]
    reports = {}
    for name, text, cover in fixtures:
        source = root / f"{name}.md"
        source.write_text(text, encoding="utf-8")
        md_export.export(source, None, None, kit.DEFAULT_TEMPLATE, False, False, cover)
        report = qa.run(source, max_pages=1 if cover else 2, cover=cover)
        (root / f"{name}-qa.json").write_text(json.dumps(report, indent=2) + "\n")
        reports[name] = report
        print(f"{name}: {report['overall']}")
        for check, value in report["checks"].items():
            if value["status"] != "pass":
                print(f"  {check}: {value['status']} — {'; '.join(value['details'])}")
    print(f"Artifacts: {root}")
    print("Rendering does not complete visual review; inspect PDF pages before recording a visual pass.")
    return 1 if any(r["overall"] == "failed" for r in reports.values()) else 0


if __name__ == "__main__":
    raise SystemExit(main())
