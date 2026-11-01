"""Shared paths, profile loading, and Chrome discovery for the export scripts."""
from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
from functools import lru_cache
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
KIT_ROOT = SCRIPT_DIR.parent
DEFAULT_TEMPLATE = KIT_ROOT / "templates" / "resume-template.docx"
PROFILE_DIR = KIT_ROOT / "profile"

CHROME_CANDIDATES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
]
CHROME_COMMANDS = ["google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "microsoft-edge"]


def load_module(name: str, filename: str):
    """Import a sibling script by filename so the scripts run from any directory."""
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, SCRIPT_DIR / filename)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def profile_path() -> Path:
    """`RESUME_PROFILE` env var wins, then profile/profile.json, then the bundled example."""
    env = os.environ.get("RESUME_PROFILE")
    if env:
        return Path(env).expanduser()
    real = PROFILE_DIR / "profile.json"
    return real if real.exists() else PROFILE_DIR / "profile.example.json"


@lru_cache(maxsize=1)
def load_profile() -> dict:
    path = profile_path()
    if not path.exists():
        raise FileNotFoundError(f"Profile not found: {path}. Run ./setup.sh first.")
    data = json.loads(path.read_text(encoding="utf-8"))
    data.setdefault("contact_lines", [])
    data.setdefault("link_labels", {})
    data.setdefault("company_projects", {})
    data.setdefault("company_websites", {})
    data.setdefault("company_about", {})
    data.setdefault("bold_terms", [])
    data.setdefault("summary_bold_phrases", [])
    data.setdefault("auto_bold", True)
    return data


def contact_items() -> list[dict]:
    return [item for line in load_profile()["contact_lines"] for item in line]


def find_chrome() -> str:
    env = os.environ.get("CHROME_PATH")
    if env:
        return env
    for path in CHROME_CANDIDATES:
        if Path(path).exists():
            return path
    for cmd in CHROME_COMMANDS:
        found = shutil.which(cmd)
        if found:
            return found
    raise FileNotFoundError(
        "Chrome/Chromium not found. Install Google Chrome or set CHROME_PATH to a Chromium-based browser."
    )


def run_chrome(*args: str, output: Path) -> None:
    """Run headless Chrome with a throwaway profile, so it never touches (or waits on) the user's.

    Success means `output` was written: headless Chrome sometimes crashes during teardown
    after the file is already complete, and that exit code is noise.
    """
    output.unlink(missing_ok=True)
    with tempfile.TemporaryDirectory(prefix="resume-kit-chrome-") as profile:
        result = subprocess.run(
            [find_chrome(), "--headless=new", "--disable-gpu", f"--user-data-dir={profile}", *args],
            capture_output=True,
            text=True,
        )
    if not (output.exists() and output.stat().st_size > 0):
        tail = "\n".join((result.stderr or result.stdout).strip().splitlines()[-5:])
        raise RuntimeError(f"Chrome exited with status {result.returncode}:\n{tail}")
