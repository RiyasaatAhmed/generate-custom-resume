#!/usr/bin/env python3
"""Local application records, explicit submission snapshots, and outcome counts.

This helper never submits applications or sends messages.
"""
from __future__ import annotations
import argparse
from collections import defaultdict
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import uuid

STATES = ("drafted", "ready", "applied", "contacted", "replied", "screening",
          "technical-interview", "final", "offer", "rejected", "withdrawn")
AFTER_APPLY = {"screening", "technical-interview", "final", "offer"}


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def save(path: Path, record: dict) -> None:
    """Atomic replacement of the mutable record; snapshots use exclusive creation."""
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent, delete=False) as handle:
        temporary = Path(handle.name)
        json.dump(record, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    try:
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def load(directory: Path) -> dict:
    record = json.loads((directory / "application.json").read_text(encoding="utf-8"))
    if record.get("schema_version") != 1 or record.get("state") not in STATES or not isinstance(record.get("events"), list):
        raise ValueError("Unsupported/malformed application record")
    return record


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")[:70] or "application"


def initialize(root: Path, company: str, role: str, url: str = "", requisition: str = "",
               role_family: str = "unknown", geography: str = "unknown", channel: str = "unknown") -> Path:
    if not company.strip() or not role.strip():
        raise ValueError("Company and role cannot be empty")
    stamp = now()
    identifier = f"{slug(company)}-{slug(role)}-{slug(requisition) + '-' if requisition else ''}{stamp[:10]}-{uuid.uuid4().hex[:8]}"
    directory = root / identifier
    directory.mkdir(parents=True, exist_ok=False)
    record = {"schema_version": 1, "id": identifier, "company": company, "role": role,
              "job_url": url, "requisition_id": requisition or None, "created_at": stamp,
              "updated_at": stamp, "applied_at": None, "state": "drafted",
              "role_family": role_family, "geography": geography, "channel": channel,
              "events": [{"state": "drafted", "at": stamp, "note": "Materials not yet submitted"}], "submissions": []}
    save(directory / "application.json", record)
    return directory


def event(directory: Path, state: str, note: str = "") -> dict:
    if state not in STATES or state == "applied":
        raise ValueError("Use submit --confirm-submitted to record an application")
    record = load(directory)
    if record["state"] in ("rejected", "withdrawn"):
        raise ValueError("This application is closed; initialize a new record for a new process")
    if state in AFTER_APPLY and not record["applied_at"]:
        raise ValueError("Confirm submission before recording interview/offer stages")
    stamp = now()
    record.update(state=state, updated_at=stamp)
    record["events"].append({"state": state, "at": stamp, "note": note})
    save(directory / "application.json", record)
    return record


def submit(directory: Path, files: list[Path], confirmed: bool = False, note: str = "") -> dict:
    if not confirmed:
        raise ValueError("Submission is not inferred: use --confirm-submitted only after actual submission")
    if not files:
        raise ValueError("Name the exact files that were submitted")
    directory = directory.resolve()
    record = load(directory)
    if record["state"] in ("rejected", "withdrawn"):
        raise ValueError("Closed application: create a new record")
    artifacts = {}
    for file in files:
        candidate = file if file.is_absolute() else directory / file
        resolved = candidate.resolve()
        if not resolved.is_relative_to(directory) or resolved.is_relative_to(directory / "submitted"):
            raise ValueError("Submission artifacts must be inside this application, outside submitted/")
        if not resolved.is_file() or resolved.stat().st_size == 0:
            raise ValueError(f"Missing/empty submission file: {file}")
        relative = resolved.relative_to(directory)
        if relative.as_posix() == "manifest.json":
            raise ValueError("manifest.json is reserved for the submission record")
        artifacts[relative] = resolved.read_bytes()
    stamp = now()
    version = stamp.replace(":", "-") + "-" + uuid.uuid4().hex[:8]
    snapshot = directory / "submitted" / version
    snapshot.mkdir(parents=True, exist_ok=False)
    hashes = {}
    for relative, content in artifacts.items():
        target = snapshot / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("xb") as handle:
            handle.write(content)
        hashes[relative.as_posix()] = hashlib.sha256(content).hexdigest()
    manifest = {"schema_version": 1, "at": stamp, "application_id": record["id"], "sha256": hashes, "note": note}
    with (snapshot / "manifest.json").open("x", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=2)
        handle.write("\n")
    record["submissions"].append({"at": stamp, "snapshot": str(snapshot.relative_to(directory)), "sha256": hashes})
    record["applied_at"] = record["applied_at"] or stamp
    record["events"].append({"state": "applied", "at": stamp, "note": note})
    record.update(state="applied", updated_at=stamp)
    save(directory / "application.json", record)
    return record


def verify_snapshots(directory: Path) -> list[str]:
    problems = []
    for submission in load(directory)["submissions"]:
        folder = (directory / submission["snapshot"]).resolve()
        if not folder.is_relative_to(directory.resolve() / "submitted"):
            problems.append("Snapshot path escapes submitted/")
            continue
        try:
            manifest = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
            if manifest.get("sha256") != submission["sha256"] or manifest.get("at") != submission["at"]:
                problems.append(f"Modified submission manifest: {folder.name}")
        except (OSError, ValueError, AttributeError):
            problems.append(f"Missing/invalid submission manifest: {folder.name}")
        for relative, digest in submission["sha256"].items():
            target = (folder / relative).resolve()
            if not target.is_relative_to(folder) or not target.is_file() or hashlib.sha256(target.read_bytes()).hexdigest() != digest:
                problems.append(f"Missing/modified submitted artifact: {relative}")
    return problems


def summarize(root: Path, group_by: str | None = None) -> dict:
    groups = defaultdict(list)
    errors = []
    for path in sorted(root.glob("*/application.json")):
        try:
            record = load(path.parent)
            groups[str(record.get(group_by, "unknown")) if group_by else "all"].append(record)
        except (OSError, ValueError, KeyError) as exc:
            errors.append(f"{path}: {exc}")
    output = {}
    for name, records in groups.items():
        submitted = [r for r in records if r.get("applied_at")]
        def post_submit_events(record):
            for index, item in enumerate(record["events"]):
                if item["state"] == "applied":
                    return record["events"][index + 1:]
            return []
        counts = {stage: sum(any(e["state"] == stage for e in post_submit_events(r)) for r in submitted)
                  for stage in ("replied", "screening", "technical-interview", "final", "offer")}
        output[name] = {"prepared": len(records), "submitted": len(submitted), "counts_among_submitted": counts,
                        "rates_among_submitted": {key: value / len(submitted) if submitted else None for key, value in counts.items()},
                        "submitted_at": [r["applied_at"] for r in submitted]}
    return {"as_of": now(), "groups": output, "errors": errors,
            "note": "Rates use submitted applications and post-submission events only. Pre-application networking stays in event history. Small nonrandom samples do not establish causation."}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    init = sub.add_parser("init")
    init.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1] / "applications")
    for name in ("company", "role"):
        init.add_argument("--" + name, required=True)
    for name in ("url", "requisition"):
        init.add_argument("--" + name, default="")
    for name in ("role-family", "geography", "channel"):
        init.add_argument("--" + name, default="unknown")
    status = sub.add_parser("event")
    status.add_argument("directory", type=Path)
    status.add_argument("state", choices=STATES)
    status.add_argument("--note", default="")
    submitted = sub.add_parser("submit")
    submitted.add_argument("directory", type=Path)
    submitted.add_argument("files", nargs="+", type=Path, help="Paths relative to the application folder")
    submitted.add_argument("--confirm-submitted", action="store_true")
    submitted.add_argument("--note", default="")
    verify = sub.add_parser("verify")
    verify.add_argument("directory", type=Path)
    summary = sub.add_parser("summary")
    summary.add_argument("root", type=Path)
    summary.add_argument("--group-by", choices=("role_family", "geography", "channel"))
    args = parser.parse_args(argv)
    try:
        if args.command == "init":
            print(initialize(args.root, args.company, args.role, args.url, args.requisition, args.role_family, args.geography, args.channel))
        elif args.command == "event":
            print(json.dumps(event(args.directory, args.state, args.note), indent=2))
        elif args.command == "submit":
            print(json.dumps(submit(args.directory, args.files, args.confirm_submitted, args.note), indent=2))
        elif args.command == "verify":
            problems = verify_snapshots(args.directory)
            print(json.dumps({"problems": problems}, indent=2))
            return 1 if problems else 0
        else:
            report = summarize(args.root, args.group_by)
            print(json.dumps(report, indent=2))
            return 1 if report["errors"] else 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(exc, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
