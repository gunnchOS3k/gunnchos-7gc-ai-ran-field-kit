#!/usr/bin/env python3
"""Validate Baseline V2 artifact pack integrity and semantic rules (Phase B.2)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "program" / "digital_ecosystem_baseline_v2"
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from baseline_v2_evidence_census import CANONICAL_CURRENT_LEVELS, END_GOAL_FAMILIES  # noqa: E402

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
    "ACCEPTED_MAIN_EVIDENCE_INDEX.json",
    "ACCEPTED_MAIN_EVIDENCE_INDEX.md",
    "REQUIREMENT_RECONCILIATION_AUDIT.json",
    "REQUIREMENT_RECONCILIATION_AUDIT.md",
    "FALSE_OPEN_PREVENTION_REPORT.json",
    "FALSE_OPEN_PREVENTION_REPORT.md",
]

WORK_STATES_COMPLETE = {"DIGITAL_IMPLEMENTATION_COMPLETE", "COMPLETE_AT_REQUIRED_LEVEL"}
WORK_STATES_OPEN = {"DIGITAL_IMPLEMENTATION_OPEN", "DIGITAL_VALIDATION_OPEN", "EVIDENCE_MAPPING_OPEN"}
PENDING = {
    "PHYSICAL_PENDING",
    "HUMAN_PENDING",
    "EXTERNAL_PENDING",
    "STANDARD_PENDING",
    "CERTIFICATION_PENDING",
    "CARRIER_PENDING",
    "VENDOR_PENDING",
    "OWNER_DECISION_PENDING",
    "DIGITAL_PREPARATION_COMPLETE_HUMAN_PENDING",
    "DIGITAL_PREPARATION_COMPLETE_PHYSICAL_PENDING",
    "DIGITAL_PREPARATION_COMPLETE_EXTERNAL_PENDING",
}

GENERIC_EVIDENCE_MARKERS = (":tests/", "required_evidence:", "see README", "TBD")


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
    audit = json.loads((OUT / "REQUIREMENT_RECONCILIATION_AUDIT.json").read_text(encoding="utf-8"))
    false_open = json.loads((OUT / "FALSE_OPEN_PREVENTION_REPORT.json").read_text(encoding="utf-8"))
    index = json.loads((OUT / "ACCEPTED_MAIN_EVIDENCE_INDEX.json").read_text(encoding="utf-8"))

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

    if end_goal.get("family_count") != 28:
        errors.append(f"end-goal family count != 28 (got {end_goal.get('family_count')})")

    for fam in END_GOAL_FAMILIES:
        rec = next((f for f in end_goal.get("families") or [] if f.get("id") == fam["id"]), None)
        if not rec or rec.get("requirement_count", 0) <= 0:
            errors.append(f"missing end-goal family coverage: {fam['name']}")

    if index.get("record_count", 0) < 100:
        errors.append("ACCEPTED_MAIN_EVIDENCE_INDEX too small (<100 records)")

    pending_total = sum(totals.get(k, 0) for k in (
        "HUMAN_PENDING", "PHYSICAL_PENDING", "EXTERNAL_PENDING", "STANDARD_PENDING",
        "CERTIFICATION_PENDING", "CARRIER_PENDING", "VENDOR_PENDING", "OWNER_DECISION_PENDING",
    ))
    if pending_total == 0:
        errors.append("all pending classes zero — under-classification alarm")

    impl_open = totals.get("DIGITAL_IMPLEMENTATION_OPEN", 0)
    atomic = totals.get("ATOMIC_TOTAL", 1) or 1
    if impl_open / atomic > 0.9:
        errors.append(f">{90}% DIGITAL_IMPLEMENTATION_OPEN ({impl_open}/{atomic}) sanity alarm")

    for row in resolutions:
        rid = row.get("requirement_id")
        if row.get("layer") is not None:
            errors.append(f"{rid}: layer field conflates program_gate with completion level")
        ws = row.get("work_state") or row.get("resolution") or ""
        cl = row.get("current_level") or ""
        if cl and cl not in CANONICAL_CURRENT_LEVELS:
            errors.append(f"{rid}: non-canonical current_level {cl}")
        if ws in WORK_STATES_COMPLETE:
            if not row.get("accepted_main_sha"):
                errors.append(f"{rid}: complete row lacks accepted_main_sha")
            ev = row.get("implementation_evidence") or row.get("validation_evidence") or ""
            if not ev or any(g in ev for g in GENERIC_EVIDENCE_MARKERS):
                errors.append(f"{rid}: complete row lacks specific evidence path")
            if not row.get("resolution_reason"):
                errors.append(f"{rid}: complete row lacks resolution_reason")
        if ws == "DIGITAL_IMPLEMENTATION_OPEN" and row.get("implementation_state") == "IMPLEMENTED":
            errors.append(f"{rid}: IMPLEMENTED classified as DIGITAL_IMPLEMENTATION_OPEN")
        passes = row.get("search_passes") or {}
        if ws == "DIGITAL_IMPLEMENTATION_OPEN" and not any(passes.values()):
            errors.append(f"{rid}: search miss classified DIGITAL_IMPLEMENTATION_OPEN not EVIDENCE_MAPPING_OPEN")
        if ws in PENDING and row.get("implementation_state") == "NOT_IMPLEMENTED" and not row.get("blocker_classes"):
            if ws not in ("OWNER_DECISION_PENDING",):
                pass  # allow owner-decision without impl

    audit_103 = gaps.get("device_os_103") or {}
    if audit_103.get("unique_capabilities_remaining", -1) > 0 and not audit_103.get("current_main_replacements"):
        errors.append("device-os #103 unique count without successor comparison evidence")

    stale = gaps.get("stale_preview_references") or result.get("STALE_PREVIEW_DETAIL") or []
    if result.get("STALE_PREVIEW_REFERENCES", 0) > 0 and not stale:
        errors.append("stale preview count not traceable to portal content rows")

    for row in ci.get("matrix") or []:
        detail = row.get("ci_detail") or {}
        if row.get("ci") == "PASS":
            for wf in detail.get("workflows") or []:
                if wf.get("state") == "UNKNOWN" and wf.get("workflow") in (detail.get("required_workflows") or []):
                    errors.append(f"{row.get('repository')}: CI PASS from UNKNOWN workflow {wf.get('workflow')}")

    if false_open.get("status") == "FAIL":
        for alarm in false_open.get("alarms") or []:
            if alarm.get("severity") == "CRITICAL":
                errors.append(f"false-open CRITICAL: {alarm.get('detail')}")

    if result.get("BASELINE_V2_READY_FOR_OWNER_MERGE") and totals.get("EVIDENCE_MAPPING_OPEN", 0) > 0:
        errors.append("BASELINE_V2_READY_FOR_OWNER_MERGE=true with EVIDENCE_MAPPING_OPEN>0")

    if len(audit.get("requirements") or []) != len(reqs):
        errors.append("REQUIREMENT_RECONCILIATION_AUDIT length mismatch")

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
