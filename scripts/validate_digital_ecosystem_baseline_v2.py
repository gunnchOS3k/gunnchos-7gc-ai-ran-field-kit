#!/usr/bin/env python3
"""Validate Baseline V2 artifact pack integrity and semantic rules."""

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
    "EVIDENCE_RESOLUTION.json",
    "EVIDENCE_RESOLUTION.md",
    "END_GOAL_COVERAGE_MATRIX.json",
    "END_GOAL_COVERAGE_MATRIX.md",
    "SUPERSEDED_PR_DISPOSITION.md",
    "BASELINE_V2_RESULT.json",
]

COMPLETE = {
    "ACCEPTED_MAIN_PROVEN",
    "ACCEPTED_MAIN_IMPLEMENTED_VERIFIED",
    "SUPERSEDED_BY_ACCEPTED_MAIN",
}

PENDING = {
    "PHYSICAL_PENDING",
    "HUMAN_PENDING",
    "EXTERNAL_PENDING",
    "STANDARD_PENDING",
    "CERTIFICATION",
    "CARRIER",
    "VENDOR",
    "OWNER_DECISION_PENDING",
}

END_GOAL_FAMILIES = {
    "ecosystem",
    "connectivity",
    "os",
    "ai",
    "applications",
    "rings",
    "7gc",
    "evidence",
    "standards",
    "device",
    "games",
    "carrier_grade",
    "gates",
}


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
    evidence = json.loads((OUT / "EVIDENCE_RESOLUTION.json").read_text(encoding="utf-8"))
    end_goal = json.loads((OUT / "END_GOAL_COVERAGE_MATRIX.json").read_text(encoding="utf-8"))
    gaps = json.loads((OUT / "REMAINING_GAPS.json").read_text(encoding="utf-8"))
    ci = json.loads((OUT / "CI_AND_REPRODUCTION_MATRIX.json").read_text(encoding="utf-8"))

    totals = register.get("totals") or {}
    reqs = register.get("requirements") or []
    resolutions = evidence.get("resolutions") or []

    if totals.get("ATOMIC_TOTAL") != len(reqs):
        errors.append("ATOMIC_TOTAL mismatch vs requirements length")
    if len(reqs) != len(resolutions):
        errors.append("MASTER register length != EVIDENCE_RESOLUTION length")
    if accepted.get("canonical_repo_count") != 17:
        errors.append("expected 17 canonical repos")
    if result.get("PRE_ENGINEERING_HYGIENE_PASS") is True:
        errors.append("must not manufacture PRE_ENGINEERING_HYGIENE_PASS=true in Phase B draft")

    gate_78 = register.get("gates_7_8_included") or result.get("PROGRAM_GATE_7_8_REQUIREMENTS_RETAINED") or 0
    if gate_78 <= 0:
        errors.append("Gate 7/8 requirements dropped from register")

    recomputed: dict[str, int] = {}
    for r in reqs:
        st = r.get("resolution") or r.get("engineering_state")
        recomputed[st] = recomputed.get(st, 0) + 1
    if recomputed.get("DIGITAL_IMPLEMENTATION_COMPLETE", 0) != totals.get("DIGITAL_IMPLEMENTATION_COMPLETE"):
        if sum(1 for r in reqs if (r.get("resolution") in COMPLETE)) != totals.get("DIGITAL_IMPLEMENTATION_COMPLETE"):
            errors.append("DIGITAL_IMPLEMENTATION_COMPLETE tally mismatch")

    for row in resolutions:
        rid = row.get("requirement_id")
        if row.get("layer") is not None:
            errors.append(f"{rid}: layer field conflates program_gate with completion level")
        res = row.get("resolution") or ""
        if res in COMPLETE:
            if not row.get("accepted_main_sha"):
                errors.append(f"{rid}: complete row lacks accepted_main_sha")
            if not (row.get("implementation_evidence") or row.get("validation_evidence")):
                errors.append(f"{rid}: complete row lacks evidence path")
            if not row.get("resolution_reason"):
                errors.append(f"{rid}: complete row lacks resolution_reason")
        if res in PENDING and row.get("implementation_state") in ("NOT_STARTED", "IN_PROGRESS", "PARTIAL"):
            errors.append(f"{rid}: {res} with automatable digital work underneath")

    audit = gaps.get("device_os_103") or {}
    if audit.get("unique_capabilities_remaining", -1) > 0 and not audit.get("current_main_replacements"):
        errors.append("device-os #103 unique count without successor comparison evidence")

    stale = gaps.get("stale_preview_references") or result.get("STALE_PREVIEW_DETAIL") or []
    if result.get("STALE_PREVIEW_REFERENCES", 0) > 0 and not stale:
        errors.append("stale preview count not traceable to portal content rows")

    for fam in END_GOAL_FAMILIES:
        rec = next((f for f in end_goal.get("families") or [] if f.get("family") == fam), None)
        if not rec or rec.get("requirement_count", 0) <= 0:
            errors.append(f"missing end-goal family coverage: {fam}")

    for rec in accepted.get("repos") or {}:
        pass
    for row in ci.get("matrix") or []:
        detail = row.get("ci_detail") or {}
        if row.get("ci") == "PASS":
            for wf in detail.get("workflows") or []:
                if wf.get("state") == "UNKNOWN" and wf.get("workflow") in (detail.get("required_workflows") or []):
                    errors.append(f"{row.get('repository')}: CI PASS from UNKNOWN workflow {wf.get('workflow')}")

    if result.get("BASELINE_V2_READY_FOR_OWNER_MERGE") and totals.get("EVIDENCE_UNRESOLVED", 0) > 0:
        errors.append("BASELINE_V2_READY_FOR_OWNER_MERGE=true with EVIDENCE_UNRESOLVED>0")

    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        print("BASELINE_V2_SEMANTIC_VALIDATION_FAIL", file=sys.stderr)
        return 1

    print("BASELINE_V2_VALIDATION_PASS")
    print("BASELINE_V2_SEMANTIC_VALIDATION_PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
