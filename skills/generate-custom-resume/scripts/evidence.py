#!/usr/bin/env python3
"""Validate evidence structure and references. This does not verify real-world truth."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys

STATUSES = {"candidate-stated", "context-confirmed", "artifact-supported", "needs-clarification"}
MATCHES = {"direct", "adjacent", "missing", "unknown"}


def nonempty(value) -> bool:
    return isinstance(value, str) and bool(value.strip())


def bank_errors(data: dict) -> list[str]:
    if not isinstance(data, dict) or data.get("schema_version") != 1 or not isinstance(data.get("achievements"), list):
        return ["Expected schema_version: 1 and an achievements array"]
    errors = []
    seen = set()
    for index, item in enumerate(data["achievements"]):
        prefix = f"achievement {index + 1}"
        if not isinstance(item, dict):
            errors.append(f"{prefix}: must be an object")
            continue
        for key in ("id", "employer", "claim", "source"):
            if not nonempty(item.get(key)):
                errors.append(f"{prefix}: {key} must be nonempty text")
        identifier = item.get("id")
        if nonempty(identifier):
            if identifier in seen:
                errors.append(f"Duplicate achievement ID: {identifier}")
            seen.add(identifier)
        if item.get("status") not in STATUSES:
            errors.append(f"{prefix}: invalid status")
        if item.get("status") == "context-confirmed" and not nonempty(item.get("confirmation")):
            errors.append(f"{prefix}: context-confirmed needs a dated confirmation reference")
        artifacts = item.get("artifacts", [])
        if not isinstance(artifacts, list) or any(not nonempty(a) for a in artifacts):
            errors.append(f"{prefix}: artifacts must be a list of references")
        if item.get("status") == "artifact-supported" and not artifacts:
            errors.append(f"{prefix}: artifact-supported needs an artifact reference")
        metrics = item.get("metrics", [])
        if not isinstance(metrics, list):
            errors.append(f"{prefix}: metrics must be an array")
            continue
        for metric in metrics:
            if not isinstance(metric, dict) or not nonempty(metric.get("name")) or not nonempty(metric.get("unit")):
                errors.append(f"{prefix}: each metric needs a name and unit")
            elif metric.get("derived") and not nonempty(metric.get("calculation")):
                errors.append(f"{prefix}: derived metric needs its calculation")
    return errors


def map_errors(data: dict, bank: dict | None = None) -> list[str]:
    if not isinstance(data, dict) or data.get("schema_version") != 1 or not isinstance(data.get("requirements"), list):
        return ["Expected schema_version: 1 and a requirements array"]
    errors = bank_errors(bank) if bank is not None else []
    if errors:
        return errors
    known = {item["id"]: item for item in bank["achievements"]} if bank else {}
    seen = set()
    for index, item in enumerate(data["requirements"]):
        prefix = f"requirement {index + 1}"
        if not isinstance(item, dict):
            errors.append(f"{prefix}: must be an object")
            continue
        for key in ("id", "requirement", "posting_source", "treatment"):
            if not nonempty(item.get(key)):
                errors.append(f"{prefix}: missing {key}")
        identifier = item.get("id")
        if nonempty(identifier):
            if identifier in seen:
                errors.append(f"Duplicate requirement ID: {identifier}")
            seen.add(identifier)
        if item.get("importance") not in ("required", "preferred", "responsibility"):
            errors.append(f"{prefix}: invalid importance")
        if item.get("match") not in MATCHES:
            errors.append(f"{prefix}: invalid match")
        sources = item.get("sources", [])
        if not isinstance(sources, list):
            errors.append(f"{prefix}: sources must be an array")
            continue
        if item.get("match") in ("direct", "adjacent") and not sources:
            errors.append(f"{prefix}: supported matches need a source")
        for source in sources:
            if not isinstance(source, dict):
                errors.append(f"{prefix}: source must be an object")
            elif "achievement_id" in source:
                achievement = known.get(source["achievement_id"]) if isinstance(source["achievement_id"], str) else None
                if achievement is None:
                    errors.append(f"{prefix}: unknown achievement ID; supply the matching --bank")
                elif achievement["status"] == "needs-clarification" and item.get("match") == "direct":
                    errors.append(f"{prefix}: unresolved achievement cannot be treated as direct proof")
            elif not (nonempty(source.get("reference")) and nonempty(source.get("excerpt"))):
                errors.append(f"{prefix}: legacy sources need reference and excerpt")
    eligibility = data.get("eligibility", [])
    if not isinstance(eligibility, list):
        errors.append("eligibility must be an array")
    else:
        for item in eligibility:
            if not isinstance(item, dict) or item.get("candidate_status") not in ("met", "not-met", "unknown"):
                errors.append("Each eligibility item needs candidate_status: met/not-met/unknown")
            elif not nonempty(item.get("requirement")) or not nonempty(item.get("posting_source")):
                errors.append("Eligibility needs requirement and posting_source")
            elif item["candidate_status"] != "unknown" and not nonempty(item.get("candidate_source")):
                errors.append("Known eligibility needs a candidate_source; do not infer authorization")
    recommendation = data.get("recommendation", {})
    if not isinstance(recommendation, dict) or recommendation.get("decision") not in ("pursue", "clarify-first", "lower-priority"):
        errors.append("Recommendation needs decision: pursue/clarify-first/lower-priority")
    elif not isinstance(recommendation.get("reasons"), list) or not recommendation["reasons"] or any(not nonempty(r) for r in recommendation["reasons"]):
        errors.append("Recommendation needs nonempty reasons")
    return errors


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("kind", choices=("bank", "map"))
    parser.add_argument("file", type=Path)
    parser.add_argument("--bank", type=Path)
    args = parser.parse_args(argv)
    try:
        data = json.loads(args.file.read_text(encoding="utf-8"))
        bank = json.loads(args.bank.read_text(encoding="utf-8")) if args.bank else None
        errors = bank_errors(data) if args.kind == "bank" else map_errors(data, bank)
        print(json.dumps({"valid_structure": not errors, "errors": errors,
                          "note": "Structure and references checked; claims still require source review."}, indent=2))
        return 1 if errors else 0
    except (OSError, ValueError) as exc:
        print(exc, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
