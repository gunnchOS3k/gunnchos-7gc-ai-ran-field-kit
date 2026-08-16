#!/usr/bin/env python3
"""Validate Charter Engineering Requirement Register V2 granularity + pending classification.

Fails when coarse pending hides digitally executable work, parents hide open children,
branch tips are presented as accepted main, or required fields are missing.

Emits token: CHARTER_REQUIREMENT_GRANULARITY_AND_PENDING_CLASSIFICATION_PASS
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REGISTER = (
    ROOT
    / "artifacts"
    / "charter_exhaustion"
    / "CHARTER_ENGINEERING_REQUIREMENT_REGISTER_V2.json"
)

REQUIRED_FIELDS = [
    "requirement_id",
    "parent_requirement",
    "layer",
    "product",
    "owner_repo",
    "accepted_main_sha",
    "description",
    "digital_acceptance_criteria",
    "real_implementation_files",
    "real_test_files",
    "real_runtime_evidence",
    "evidence_level",
    "depth_level",
    "verification_level",
    "S0",
    "S1",
    "S2",
    "digital_work_still_possible",
    "digital_work_description",
    "engineering_state",
    "final_non_digital_dependency",
    "next_packet",
]

OPEN = "ATOMIC_DIGITAL_IMPLEMENTATION_OPEN"
COMPLETE = "DIGITAL_IMPLEMENTATION_COMPLETE"
PENDING_STATES = {
    "DIGITAL_PREPARATION_COMPLETE_EXTERNAL_PENDING",
    "DIGITAL_PREPARATION_COMPLETE_HUMAN_PENDING",
    "DIGITAL_PREPARATION_COMPLETE_PHYSICAL_PENDING",
    "STANDARD_PENDING",
    "OWNER_DECISION_PENDING",
}
PHYSICALISH = {
    "DIGITAL_PREPARATION_COMPLETE_PHYSICAL_PENDING",
    "DIGITAL_PREPARATION_COMPLETE_EXTERNAL_PENDING",
    "DIGITAL_PREPARATION_COMPLETE_HUMAN_PENDING",
}


def fail(errors: list[str], msg: str) -> None:
    errors.append(msg)


def main() -> int:
    errors: list[str] = []
    if not REGISTER.exists() or REGISTER.stat().st_size == 0:
        print("FAIL: register missing or empty")
        print("CHARTER_REQUIREMENT_GRANULARITY_AND_PENDING_CLASSIFICATION_PASS=false")
        return 1

    try:
        doc = json.loads(REGISTER.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"FAIL: register JSON invalid: {exc}")
        print("CHARTER_REQUIREMENT_GRANULARITY_AND_PENDING_CLASSIFICATION_PASS=false")
        return 1

    reqs: list[dict[str, Any]] = doc.get("requirements") or []
    if not reqs:
        fail(errors, "requirements array empty")

    forbidden = set(doc.get("forbidden_branch_shas_as_accepted_main") or [])
    by_id: dict[str, dict[str, Any]] = {}
    children: dict[str | None, list[str]] = {}

    for r in reqs:
        rid = r.get("requirement_id")
        if not rid:
            fail(errors, "row missing requirement_id")
            continue
        if rid in by_id:
            fail(errors, f"{rid}: duplicate requirement_id")
        by_id[rid] = r
        parent = r.get("parent_requirement")
        children.setdefault(parent, []).append(rid)

        for field in REQUIRED_FIELDS:
            if field not in r:
                fail(errors, f"{rid}: missing required field {field}")

        if not r.get("owner_repo"):
            fail(errors, f"{rid}: child/row missing owner_repo")

        sha = str(r.get("accepted_main_sha") or "")
        if not sha:
            fail(errors, f"{rid}: empty accepted_main_sha")
        if sha in forbidden or any(sha.startswith(f[:7]) for f in forbidden):
            fail(errors, f"{rid}: branch tip SHA presented as accepted_main_sha ({sha[:12]})")

        depth = r.get("depth_level")
        impl = r.get("real_implementation_files") or []
        digital_possible = bool(r.get("digital_work_still_possible"))
        irreducible = bool(r.get("irreducible_non_digital"))
        state = r.get("engineering_state")

        if depth == "D_INCOMPLETE" and impl == [] and digital_possible is False:
            if not irreducible:
                fail(
                    errors,
                    f"{rid}: D_INCOMPLETE + empty impl + digital_work_still_possible=false "
                    "without irreducible_non_digital",
                )
            if not irreducible and state == OPEN:
                fail(errors, f"{rid}: OPEN with digital_work_still_possible=false")

        # PHYSICAL/EXTERNAL/HUMAN pending while digital prep missing:
        # if this row is pending and digital_possible false, it must be irreducible
        # AND should not itself be the mixed coarse row (reopened splits handle that).
        if state in PHYSICALISH and digital_possible is False and not irreducible:
            fail(
                errors,
                f"{rid}: {state} with digital_work_still_possible=false requires "
                "irreducible_non_digital=true (split digital prep first)",
            )

        if state in {
            "DIGITAL_PREPARATION_COMPLETE_PHYSICAL_PENDING",
            "DIGITAL_PREPARATION_COMPLETE_EXTERNAL_PENDING",
            "DIGITAL_PREPARATION_COMPLETE_HUMAN_PENDING",
        }:
            # Prefer parent digital prep open sibling naming convention when parent is a prep row.
            pass

        if state == COMPLETE and r.get("children_required_for_parent_complete"):
            # checked after map built
            pass

        if digital_possible and state in PENDING_STATES and not r.get("reopened"):
            # digital still possible should usually be OPEN, not pending-complete
            fail(
                errors,
                f"{rid}: digital_work_still_possible=true but engineering_state={state}",
            )

    # Parent complete while required child open
    for rid, r in by_id.items():
        if r.get("engineering_state") != COMPLETE:
            continue
        kids = children.get(rid, [])
        if not kids and not r.get("children_required_for_parent_complete"):
            continue
        for kid in kids:
            ks = by_id[kid].get("engineering_state")
            if ks == OPEN or (
                by_id[kid].get("digital_work_still_possible")
                and ks != COMPLETE
            ):
                fail(
                    errors,
                    f"{rid}: parent COMPLETE while child {kid} is {ks}",
                )
        if r.get("children_required_for_parent_complete") and any(
            by_id[k].get("engineering_state") == OPEN for k in kids
        ):
            fail(errors, f"{rid}: children_required_for_parent_complete but children OPEN")

    # Count consistency
    open_count = sum(1 for r in reqs if r.get("engineering_state") == OPEN)
    claimed = doc.get("ATOMIC_DIGITAL_IMPLEMENTATION_OPEN")
    if claimed != open_count:
        fail(
            errors,
            f"ATOMIC_DIGITAL_IMPLEMENTATION_OPEN claim {claimed} != computed {open_count}",
        )

    if doc.get("policy", {}).get("WP001_READY_FOR_OWNER_DECISION") is True and open_count:
        fail(errors, "WP001_READY_FOR_OWNER_DECISION true while atomic open > 0")

    if doc.get("claim_firewall", {}).get("WP001_READY_FOR_OWNER_DECISION") is True and open_count:
        fail(errors, "claim_firewall WP001_READY_FOR_OWNER_DECISION true while open > 0")

    if doc.get("policy", {}).get("FIELD_KIT_71_MERGE_RECOMMEND") is True:
        fail(errors, "FIELD_KIT_71_MERGE_RECOMMEND must remain false for this packet")

    # Empty files check for referenced local register companion artifacts when listed
    for path in [
        REGISTER,
        ROOT / "artifacts" / "experience_review" / "EXPERIENCE_DEFECT_BACKLOG.json",
        ROOT
        / "artifacts"
        / "experience_review"
        / "EXPERIENCE_REVIEW_COUNCIL_STATUS.json",
    ]:
        if path.exists() and path.stat().st_size == 0:
            fail(errors, f"empty file: {path.relative_to(ROOT)}")

    token = "CHARTER_REQUIREMENT_GRANULARITY_AND_PENDING_CLASSIFICATION_PASS"
    if errors:
        print(f"FAIL ({len(errors)}):")
        for e in errors:
            print(f"  - {e}")
        print(f"{token}=false")
        print(f"ATOMIC_DIGITAL_IMPLEMENTATION_OPEN={open_count}")
        return 1

    print(f"PASS: register rows={len(reqs)} open={open_count}")
    print(f"{token}=true")
    print(f"ATOMIC_DIGITAL_IMPLEMENTATION_OPEN={open_count}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
