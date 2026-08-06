"""Compute Gate 0 overall status from approval + validators + ownership."""

from __future__ import annotations

from typing import Any

from control_plane import (
    STATUS_AUTOMATED_PASS,
    STATUS_AUTOMATED_PARTIAL,
    STATUS_CHARTER_PENDING,
    STATUS_GATE_0_PASS,
)
from control_plane.io_util import load_yaml
from control_plane.paths import CHARTER_APPROVAL_RECORD, GATES, REPOSITORIES, REQUIREMENTS
from control_plane.validators import validate_control_plane


def charter_is_approved(approval: dict[str, Any] | None = None) -> bool:
    doc = approval if approval is not None else load_yaml(CHARTER_APPROVAL_RECORD)
    if doc.get("approved") is True and doc.get("approver"):
        return True
    return str(doc.get("status") or "").upper() == "APPROVED" and bool(doc.get("approver"))


def pending_owners(reqs: list[dict[str, Any]] | None = None, ownership: dict[str, Any] | None = None) -> list[str]:
    pending: set[str] = set()
    if ownership is None and (REPOSITORIES / "repository_ownership.yaml").exists():
        ownership = load_yaml(REPOSITORIES / "repository_ownership.yaml")
    if ownership:
        for o in ownership.get("pending_decision_owners") or []:
            pending.add(str(o))
        for o in (ownership.get("owner_to_requirements") or {}):
            if o == "CONTROL_PLANE_PENDING_DECISION":
                pending.add(o)
        for o in (ownership.get("ring_workstream_ownership") or {}).values():
            if o == "CONTROL_PLANE_PENDING_DECISION":
                pending.add(o)
    if reqs is None and (REQUIREMENTS / "requirements.yaml").exists():
        reqs = load_yaml(REQUIREMENTS / "requirements.yaml").get("requirements") or []
    for r in reqs or []:
        if r.get("owner_repository") == "CONTROL_PLANE_PENDING_DECISION":
            pending.add("CONTROL_PLANE_PENDING_DECISION")
    return sorted(pending)


def compute_gate0_status(
    *,
    approval: dict[str, Any] | None = None,
    reqs: list[dict[str, Any]] | None = None,
    ownership: dict[str, Any] | None = None,
    run_validators: bool = True,
) -> dict[str, Any]:
    approval = approval if approval is not None else load_yaml(CHARTER_APPROVAL_RECORD)
    approved = charter_is_approved(approval)
    pending = pending_owners(reqs, ownership)
    issues = validate_control_plane() if run_validators else []
    errors = [i for i in issues if i.severity == "error"]
    validators_ok = not errors

    if approved and validators_ok and not pending:
        overall = STATUS_GATE_0_PASS
        secondary = "CHARTER_APPROVED"
    elif validators_ok:
        overall = STATUS_AUTOMATED_PASS
        secondary = STATUS_CHARTER_PENDING if not approved else (
            "PENDING_OWNERS" if pending else STATUS_CHARTER_PENDING
        )
    else:
        overall = STATUS_AUTOMATED_PARTIAL
        secondary = STATUS_CHARTER_PENDING if not approved else "VALIDATOR_ERRORS"

    return {
        "overall_status_token": overall,
        "secondary_status_token": secondary,
        "charter_approved": approved,
        "validators_ok": validators_ok,
        "pending_owners": pending,
        "validator_error_count": len(errors),
        "gate_0_pass_allowed": overall == STATUS_GATE_0_PASS,
    }
