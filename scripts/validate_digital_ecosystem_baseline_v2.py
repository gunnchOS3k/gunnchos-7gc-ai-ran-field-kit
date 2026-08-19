#!/usr/bin/env python3
"""Validate Baseline V2 artifact pack integrity and B.3 semantic rules."""

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
    "ACCEPTED_MAIN_EVIDENCE_INDEX_SUMMARY.json",
    "ACCEPTED_MAIN_EVIDENCE_INDEX_SUMMARY.md",
    "REQUIREMENT_RECONCILIATION_AUDIT.json",
    "REQUIREMENT_RECONCILIATION_AUDIT.md",
    "FALSE_OPEN_PREVENTION_REPORT.json",
    "FALSE_OPEN_PREVENTION_REPORT.md",
    "PRECISION_SAMPLE_AUDIT.md",
    "PRECISION_SAMPLE_AUDIT.json",
]

BLOATED = OUT / "ACCEPTED_MAIN_EVIDENCE_INDEX.json"

WORK_STATES_COMPLETE = {"DIGITAL_IMPLEMENTATION_COMPLETE", "COMPLETE_AT_REQUIRED_LEVEL"}
WORK_STATES_OPEN = {"DIGITAL_IMPLEMENTATION_OPEN", "DIGITAL_VALIDATION_OPEN", "EVIDENCE_MAPPING_OPEN"}
PENDING = {
    "PHYSICAL_PENDING", "HUMAN_PENDING", "EXTERNAL_PENDING", "STANDARD_PENDING",
    "CERTIFICATION_PENDING", "CARRIER_PENDING", "VENDOR_PENDING", "OWNER_DECISION_PENDING",
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

    if BLOATED.is_file() and BLOATED.stat().st_size > 500_000:
        errors.append("bloated ACCEPTED_MAIN_EVIDENCE_INDEX.json still tracked (>500KB)")

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
    index_summary = json.loads((OUT / "ACCEPTED_MAIN_EVIDENCE_INDEX_SUMMARY.json").read_text(encoding="utf-8"))
    precision = json.loads((OUT / "PRECISION_SAMPLE_AUDIT.json").read_text(encoding="utf-8"))

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
    if result.get("phase") != "PRE_ENGINEERING_HYGIENE_PHASE_B.3":
        errors.append(f"expected phase B.3, got {result.get('phase')}")

    gate_78 = register.get("gates_7_8_included") or result.get("PROGRAM_GATE_7_8_REQUIREMENTS_RETAINED") or 0
    if gate_78 <= 0:
        errors.append("Gate 7/8 requirements dropped from register")

    if end_goal.get("family_count") != 28:
        errors.append(f"end-goal family count != 28 (got {end_goal.get('family_count')})")

    for fam in END_GOAL_FAMILIES:
        rec = next((f for f in end_goal.get("families") or [] if f.get("id") == fam["id"]), None)
        if not rec or rec.get("requirement_count", 0) <= 0:
            errors.append(f"missing end-goal family coverage: {fam['name']}")
        if rec and "family_release_level" not in rec:
            errors.append(f"family {fam['name']} missing family_release_level")

    if index_summary.get("record_count", 0) < 100:
        errors.append("evidence index summary too small (<100 records)")

    pending_total = sum(
        totals.get(k, 0)
        for k in (
            "HUMAN_PENDING_DIMENSION", "PHYSICAL_PENDING_DIMENSION", "EXTERNAL_PENDING_DIMENSION",
            "STANDARD_PENDING_DIMENSION", "CERTIFICATION_PENDING_DIMENSION", "CARRIER_PENDING_DIMENSION",
            "VENDOR_PENDING_DIMENSION", "OWNER_DECISION_PENDING_DIMENSION",
        )
    )
    if pending_total == 0:
        errors.append("all pending dimension counts zero — under-classification alarm")

    impl_open = totals.get("DIGITAL_IMPLEMENTATION_OPEN", 0)
    atomic = totals.get("ATOMIC_TOTAL", 1) or 1
    if impl_open / atomic > 0.9:
        errors.append(f">{90}% DIGITAL_IMPLEMENTATION_OPEN ({impl_open}/{atomic}) sanity alarm")

    low_complete = totals.get("LOW_CONFIDENCE_COMPLETE_ROWS", 0)
    if low_complete > 0:
        errors.append(f"{low_complete} LOW confidence rows counted complete")

    if precision.get("sample_count", 0) < 50:
        errors.append(f"PRECISION_SAMPLE_AUDIT has {precision.get('sample_count')} samples (<50)")

    for row in resolutions:
        rid = row.get("requirement_id")
        if row.get("layer") is not None:
            errors.append(f"{rid}: layer field conflates program_gate with completion level")
        ws = row.get("work_state") or row.get("resolution") or ""
        cl = row.get("current_level") or ""
        if cl and cl not in CANONICAL_CURRENT_LEVELS:
            errors.append(f"{rid}: non-canonical current_level {cl}")
        if not row.get("primary_end_goal_family"):
            errors.append(f"{rid}: missing primary_end_goal_family")
        if not row.get("admissible_repositories"):
            errors.append(f"{rid}: missing admissible_repositories")
        if ws in WORK_STATES_COMPLETE:
            if row.get("evidence_confidence") == "LOW":
                errors.append(f"{rid}: LOW confidence complete row")
            if not row.get("accepted_main_sha"):
                errors.append(f"{rid}: complete row lacks accepted_main_sha")
            ev = row.get("implementation_evidence") or row.get("validation_evidence") or ""
            if not ev or any(g in ev for g in GENERIC_EVIDENCE_MARKERS):
                errors.append(f"{rid}: complete row lacks specific evidence path")
            if not row.get("resolution_reason"):
                errors.append(f"{rid}: complete row lacks resolution_reason")
            if row.get("evidence_repo") and row["evidence_repo"] not in (row.get("admissible_repositories") or []):
                errors.append(f"{rid}: evidence from non-admissible repo {row.get('evidence_repo')}")
        if ws == "DIGITAL_IMPLEMENTATION_OPEN" and row.get("implementation_state") == "IMPLEMENTED":
            errors.append(f"{rid}: IMPLEMENTED classified as DIGITAL_IMPLEMENTATION_OPEN")
        passes = row.get("search_passes") or {}
        if ws == "DIGITAL_IMPLEMENTATION_OPEN" and not any(
            passes.get(k) for k in ("pass1_exact_id", "pass2_proof_identifiers", "pass4_implementation")
        ):
            errors.append(f"{rid}: search miss should be EVIDENCE_MAPPING_OPEN not DIGITAL_IMPLEMENTATION_OPEN")
        if ws in WORK_STATES_COMPLETE and not passes.get("pass1_exact_id") and not passes.get("pass2_proof_identifiers"):
            if passes.get("pass6_discovery_only"):
                errors.append(f"{rid}: complete based on discovery terms only")
        if cl == "L3_USER_READY_DIGITAL_RC" and row.get("verification_state") == "INDEPENDENTLY_VERIFIED_DIGITAL":
            verif = (row.get("validation_evidence") or "").lower()
            if not any(m in verif for m in ("product_use", "digital_rc", "user_ready", "rc_")):
                errors.append(f"{rid}: L3 inferred without user-ready evidence path")

    pv = result.get("BASELINE_V2_PRECISION_VALIDATION") or {}
    if not pv.get("BASELINE_V2_PRECISION_VALIDATION_PASS"):
        for k, v in (pv.get("checks") or {}).items():
            if not v:
                errors.append(f"precision validation failed: {k}")

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
        print("BASELINE_V2_PRECISION_VALIDATION_FAIL", file=sys.stderr)
        return 1

    print("BASELINE_V2_VALIDATION_PASS")
    print("BASELINE_V2_SEMANTIC_VALIDATION_PASS")
    print("BASELINE_V2_PRECISION_VALIDATION_PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
