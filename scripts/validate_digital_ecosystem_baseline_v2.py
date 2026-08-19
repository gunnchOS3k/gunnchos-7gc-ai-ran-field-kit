#!/usr/bin/env python3
"""Validate Baseline V2 artifact pack integrity."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "program" / "digital_ecosystem_baseline_v2"

REQUIRED = [
    "README.md",
    "ACCEPTED_MAIN_BASELINE.json",
    "ACCEPTED_MAIN_BASELINE.md",
    "MASTER_COMPLETION_REGISTER.json",
    "MASTER_COMPLETION_REGISTER.md",
    "REMAINING_GAPS.json",
    "REMAINING_GAPS.md",
    "CI_AND_REPRODUCTION_MATRIX.json",
    "CI_AND_REPRODUCTION_MATRIX.md",
    "EVIDENCE_CLASSIFICATION.md",
    "SUPERSEDED_PR_DISPOSITION.md",
    "BASELINE_V2_RESULT.json",
]


def main() -> int:
    errors: list[str] = []
    for name in REQUIRED:
        if not (OUT / name).is_file():
            errors.append(f"missing {name}")

    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        return 1

    register = json.loads((OUT / "MASTER_COMPLETION_REGISTER.json").read_text(encoding="utf-8"))
    result = json.loads((OUT / "BASELINE_V2_RESULT.json").read_text(encoding="utf-8"))
    accepted = json.loads((OUT / "ACCEPTED_MAIN_BASELINE.json").read_text(encoding="utf-8"))

    totals = register.get("totals") or {}
    reqs = register.get("requirements") or []
    if totals.get("ATOMIC_TOTAL") != len(reqs):
        errors.append("ATOMIC_TOTAL mismatch vs requirements length")
    if accepted.get("canonical_repo_count") != 17:
        errors.append("expected 17 canonical repos")
    if result.get("PRE_ENGINEERING_HYGIENE_PASS") is True:
        errors.append("must not manufacture PRE_ENGINEERING_HYGIENE_PASS=true in Phase B draft")

    recomputed = {}
    for r in reqs:
        st = r.get("engineering_state")
        recomputed[st] = recomputed.get(st, 0) + 1
    if recomputed.get("DIGITAL_IMPLEMENTATION_COMPLETE", 0) != totals.get("DIGITAL_IMPLEMENTATION_COMPLETE"):
        errors.append("DIGITAL_IMPLEMENTATION_COMPLETE tally mismatch")

    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        return 1

    print("BASELINE_V2_VALIDATION_PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
