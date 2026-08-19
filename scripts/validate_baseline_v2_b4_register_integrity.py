#!/usr/bin/env python3
"""B.4.1 register integrity semantic gate — fail-closed on row/register invariants."""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "program" / "digital_ecosystem_baseline_v2"
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from baseline_v2_evidence_census import (  # noqa: E402
    IMPLEMENTATION_ROLES,
    WORK_STATES_COMPLETE,
    WORK_STATES_OPEN,
    WORK_STATES_PENDING,
    WORK_STATES_PREP,
    validation_open_impl_admissible,
)

PENDING_WORK_STATES = WORK_STATES_PENDING | WORK_STATES_PREP | {
    "PHYSICAL_PENDING",
    "HUMAN_PENDING",
    "EXTERNAL_PENDING",
    "STANDARD_PENDING",
    "CERTIFICATION_PENDING",
    "CARRIER_PENDING",
    "VENDOR_PENDING",
    "OWNER_DECISION_PENDING",
}

GENERIC_EVIDENCE_MARKERS = (":tests/", "required_evidence:", "see README", "TBD")
ALL_ACCOUNTED_STATES = (
    WORK_STATES_COMPLETE | WORK_STATES_OPEN | PENDING_WORK_STATES
)


def main() -> int:
    errors: list[str] = []

    register_path = OUT / "MASTER_COMPLETION_REGISTER.json"
    result_path = OUT / "BASELINE_V2_RESULT.json"
    impl_reg_path = OUT / "NEXT_DIGITAL_IMPLEMENTATION_WORK.json"
    val_reg_path = OUT / "NEXT_DIGITAL_VALIDATION_WORK.json"
    pending_reg_path = OUT / "NON_DIGITAL_PENDING_REGISTER.json"

    for p in (register_path, result_path, impl_reg_path, val_reg_path, pending_reg_path):
        if not p.is_file():
            errors.append(f"missing {p.name}")
    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        return 1

    register = json.loads(register_path.read_text(encoding="utf-8"))
    result = json.loads(result_path.read_text(encoding="utf-8"))
    impl_reg = json.loads(impl_reg_path.read_text(encoding="utf-8"))
    val_reg = json.loads(val_reg_path.read_text(encoding="utf-8"))
    pending_reg = json.loads(pending_reg_path.read_text(encoding="utf-8"))

    totals = register.get("totals") or {}
    rows = register.get("requirements") or []
    atomic = totals.get("ATOMIC_TOTAL", 0)

    # --- validation-open invariants ---
    for row in rows:
        rid = row.get("requirement_id")
        ws = row.get("work_state")
        if ws != "DIGITAL_VALIDATION_OPEN":
            continue
        if row.get("implementation_state") != "IMPLEMENTED":
            errors.append(f"{rid}: DIGITAL_VALIDATION_OPEN but implementation_state≠IMPLEMENTED")
        impl = (row.get("implementation_evidence") or "").strip()
        if not impl:
            errors.append(f"{rid}: DIGITAL_VALIDATION_OPEN without implementation_evidence")
        elif any(g in impl for g in GENERIC_EVIDENCE_MARKERS):
            errors.append(f"{rid}: DIGITAL_VALIDATION_OPEN with generic implementation_evidence")
        if not validation_open_impl_admissible(row):
            errors.append(f"{rid}: DIGITAL_VALIDATION_OPEN without admissible pass4 IMPLEMENTATION_* proof")
        if not row.get("accepted_main_sha"):
            errors.append(f"{rid}: DIGITAL_VALIDATION_OPEN missing accepted_main_sha")

    # --- implementation-open invariants ---
    for row in rows:
        rid = row.get("requirement_id")
        if row.get("work_state") != "DIGITAL_IMPLEMENTATION_OPEN":
            continue
        if row.get("implementation_state") == "IMPLEMENTED":
            errors.append(f"{rid}: IMPLEMENTED classified as DIGITAL_IMPLEMENTATION_OPEN")
        for field in ("specific_missing_implementation", "searched_repositories", "why_paths_insufficient"):
            if not row.get(field):
                errors.append(f"{rid}: DIGITAL_IMPLEMENTATION_OPEN missing {field}")

    # --- complete-row invariants ---
    for row in rows:
        rid = row.get("requirement_id")
        ws = row.get("work_state") or ""
        if ws not in WORK_STATES_COMPLETE:
            continue
        if row.get("evidence_confidence") == "LOW":
            errors.append(f"{rid}: LOW confidence complete row")
        if not row.get("accepted_main_sha"):
            errors.append(f"{rid}: complete row lacks accepted_main_sha")
        ev = row.get("implementation_evidence") or row.get("validation_evidence") or ""
        if not ev or any(g in ev for g in GENERIC_EVIDENCE_MARKERS):
            errors.append(f"{rid}: complete row lacks specific evidence path")
        if not row.get("resolution_reason"):
            errors.append(f"{rid}: complete row lacks resolution_reason")

    # --- pending-row invariants ---
    pending_rows = [r for r in rows if r.get("work_state") in PENDING_WORK_STATES]
    for row in pending_rows:
        rid = row.get("requirement_id")
        if not row.get("pending_dimensions"):
            errors.append(f"{rid}: pending work_state without pending_dimensions")

    # --- register-completeness invariants ---
    impl_open_count = totals.get("DIGITAL_IMPLEMENTATION_OPEN", 0)
    val_open_count = totals.get("DIGITAL_VALIDATION_OPEN", 0)
    impl_all = impl_reg.get("all_items") or []
    val_all = val_reg.get("all_items") or []
    pending_all = pending_reg.get("all_items") or []

    if impl_reg.get("total_open") != impl_open_count:
        errors.append(
            f"NEXT_DIGITAL_IMPLEMENTATION_WORK total_open={impl_reg.get('total_open')} != register {impl_open_count}"
        )
    if len(impl_all) != impl_open_count:
        errors.append(f"NEXT_DIGITAL_IMPLEMENTATION_WORK all_items={len(impl_all)} != {impl_open_count}")
    if len(impl_reg.get("top_priority_items") or []) > 25:
        errors.append("NEXT_DIGITAL_IMPLEMENTATION_WORK top_priority_items exceeds 25")

    if val_reg.get("total_open") != val_open_count:
        errors.append(
            f"NEXT_DIGITAL_VALIDATION_WORK total_open={val_reg.get('total_open')} != register {val_open_count}"
        )
    if len(val_all) != val_open_count:
        errors.append(f"NEXT_DIGITAL_VALIDATION_WORK all_items={len(val_all)} != {val_open_count}")

    pending_declared = pending_reg.get("total_pending_rows", 0)
    if pending_declared != len(pending_all):
        errors.append(f"NON_DIGITAL_PENDING total_pending_rows={pending_declared} != all_items {len(pending_all)}")
    if len(pending_all) != len(pending_rows):
        errors.append(
            f"NON_DIGITAL_PENDING all_items={len(pending_all)} != register pending rows {len(pending_rows)}"
        )

    impl_ids = {i["requirement_id"] for i in impl_all}
    reg_impl_ids = {r["requirement_id"] for r in rows if r.get("work_state") == "DIGITAL_IMPLEMENTATION_OPEN"}
    if impl_ids != reg_impl_ids:
        errors.append("NEXT_DIGITAL_IMPLEMENTATION_WORK all_items ID set mismatch vs register")

    val_ids = {i["requirement_id"] for i in val_all}
    reg_val_ids = {r["requirement_id"] for r in rows if r.get("work_state") == "DIGITAL_VALIDATION_OPEN"}
    if val_ids != reg_val_ids:
        errors.append("NEXT_DIGITAL_VALIDATION_WORK all_items ID set mismatch vs register")

    pending_ids = {i["requirement_id"] for i in pending_all}
    reg_pending_ids = {r["requirement_id"] for r in pending_rows}
    if pending_ids != reg_pending_ids:
        errors.append("NON_DIGITAL_PENDING all_items ID set mismatch vs register")

    if "top_items" in impl_reg or "top_items" in val_reg:
        errors.append("legacy top_items field present — use all_items + top_priority_items")
    if "sample_rows" in pending_reg:
        errors.append("legacy sample_rows field present — use all_items")

    # --- state accounting ---
    if len(rows) != atomic:
        errors.append(f"requirements length {len(rows)} != ATOMIC_TOTAL {atomic}")
    ws_counts = Counter(r.get("work_state") for r in rows)
    unknown = set(ws_counts) - ALL_ACCOUNTED_STATES
    if unknown:
        errors.append(f"unknown work_state values: {sorted(unknown)}")
    immediate_total = sum(ws_counts.values())
    if immediate_total != atomic:
        errors.append(f"IMMEDIATE_STATE_ACCOUNTING_TOTAL={immediate_total} != ATOMIC_TOTAL={atomic}")

    integrity_pass = len(errors) == 0
    report = {
        "BASELINE_V2_B4_REGISTER_INTEGRITY_PASS": integrity_pass,
        "errors": errors,
        "metrics": {
            "VALIDATION_OPEN_ROWS_WITHOUT_IMPL_EVIDENCE": sum(
                1 for r in rows
                if r.get("work_state") == "DIGITAL_VALIDATION_OPEN" and not validation_open_impl_admissible(r)
            ),
            "IMPLEMENTATION_OPEN_ROWS_WITHOUT_SPECIFIC_MISSING_CAPABILITY": sum(
                1 for r in rows
                if r.get("work_state") == "DIGITAL_IMPLEMENTATION_OPEN" and not r.get("specific_missing_implementation")
            ),
            "IMMEDIATE_STATE_ACCOUNTING_TOTAL": immediate_total,
        },
    }
    (OUT / "B4_REGISTER_INTEGRITY_REPORT.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        print("BASELINE_V2_B4_REGISTER_INTEGRITY_FAIL", file=sys.stderr)
        return 1

    print("BASELINE_V2_B4_MAPPING_VALIDATION_PASS")
    print("BASELINE_V2_B4_REGISTER_INTEGRITY_PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
