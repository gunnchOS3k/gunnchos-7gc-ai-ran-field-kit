#!/usr/bin/env python3
"""Validate evaluation preregistration lock integrity."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCK = ROOT / "evaluation" / "PRIMARY_OUTCOME_LOCK.json"
HASH_FILE = ROOT / "evaluation" / "preregistration-lock.sha256"
PREREG = ROOT / "evaluation" / "EVALUATION_PREREGISTRATION.md"


def digest_without_embedded_hash(obj: dict) -> str:
    copy = {k: v for k, v in obj.items() if k != "lock_sha256"}
    blob = json.dumps(copy, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(blob).hexdigest()


def validate() -> dict:
    errors: list[str] = []
    for path in (LOCK, HASH_FILE, PREREG):
        if not path.is_file():
            errors.append(f"missing {path.relative_to(ROOT)}")
    if errors:
        return {"ok": False, "errors": errors}

    lock = json.loads(LOCK.read_text(encoding="utf-8"))
    expected = HASH_FILE.read_text(encoding="utf-8").strip().split()[0]
    computed = digest_without_embedded_hash(lock)
    embedded = lock.get("lock_sha256")
    if computed != expected:
        errors.append(f"hash file mismatch: file={expected} computed={computed}")
    if embedded and embedded != computed:
        errors.append(f"embedded lock_sha256 mismatch: {embedded} != {computed}")
    if lock.get("inspection_of_complete_pilot_results") is True:
        errors.append(
            "inspection_of_complete_pilot_results=true before Gate 3 complete is invalid"
        )
    if not lock.get("primary_outcome"):
        errors.append("primary_outcome missing")
    if not lock.get("primary_claim"):
        errors.append("primary_claim missing")
    for req in (
        "evaluation/PREREGISTRATION_MANIFEST.json",
        "evaluation/PREREGISTRATION_CHECKSUMS.sha256",
        "evaluation/PREREGISTRATION_FREEZE_REPORT.md",
        "scripts/compute_recovery_time.py",
    ):
        if not (ROOT / req).is_file():
            errors.append(f"missing freeze artifact: {req}")
    defn = lock.get("definition") or {}
    # Support nested amendment_001 definition shape and flat legacy shape.
    flat_sources = [defn]
    if isinstance(defn.get("primary"), dict):
        flat_sources.append(defn["primary"])
    if isinstance(defn.get("secondary"), dict):
        flat_sources.append(defn["secondary"])
    required_keys = {
        "start_event": False,
        "recovery_event": False,
        "units": False,
        "lower_is_better": False,
        "timeout_behavior": False,
    }
    aliases = {
        "timeout_behavior": ("timeout_behavior", "right_censoring"),
        "start_event": ("start_event",),
        "recovery_event": ("recovery_event",),
        "units": ("units",),
        "lower_is_better": ("lower_is_better",),
    }
    for src in flat_sources:
        for key, alts in aliases.items():
            if any(a in src for a in alts):
                required_keys[key] = True
    # Primary units/lower_is_better may live only under definition.primary
    if required_keys["units"] is False and defn.get("primary", {}).get("units"):
        required_keys["units"] = True
    if required_keys["lower_is_better"] is False and (
        "lower_is_better" in (defn.get("primary") or {})
    ):
        required_keys["lower_is_better"] = True
    # Map secondary start/recovery + right_censoring into required set
    sec = defn.get("secondary") or {}
    if sec.get("start_event"):
        required_keys["start_event"] = True
    if sec.get("recovery_event"):
        required_keys["recovery_event"] = True
    if sec.get("right_censoring") or defn.get("timeout_behavior"):
        required_keys["timeout_behavior"] = True
    for key, ok in required_keys.items():
        if not ok:
            errors.append(f"definition missing {key}")

    return {
        "ok": not errors,
        "errors": errors,
        "primary_outcome": lock.get("primary_outcome"),
        "lock_sha256": computed,
        "inspection_of_complete_pilot_results": lock.get(
            "inspection_of_complete_pilot_results"
        ),
    }


def main(argv=None) -> int:
    argparse.ArgumentParser().parse_args(argv)
    result = validate()
    print(json.dumps(result, indent=2))
    return 0 if result["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
