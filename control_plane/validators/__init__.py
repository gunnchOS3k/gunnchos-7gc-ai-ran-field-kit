"""Control-plane validators."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from control_plane.catalog.claims_catalog import EXTENDED_STATES, is_transition_allowed
from control_plane.io_util import load_json, load_yaml
from control_plane.paths import (
    BACKLOG,
    CHARTER_APPROVAL_RECORD,
    CHARTER_FILE,
    CHARTER_SOURCE_RECORD,
    CLAIMS,
    EVIDENCE,
    GATES,
    REPOSITORIES,
    REQUIREMENTS,
    ROOT,
)


class ValidationIssue:
    def __init__(self, code: str, message: str, severity: str = "error") -> None:
        self.code = code
        self.message = message
        self.severity = severity

    def __str__(self) -> str:
        return f"[{self.severity.upper()}] {self.code}: {self.message}"


def _validate_schema(doc: Any, schema_path: Path, label: str, issues: list[ValidationIssue]) -> None:
    if not schema_path.exists():
        issues.append(ValidationIssue("SCHEMA_MISSING", f"Missing schema {schema_path}"))
        return
    schema = load_json(schema_path)
    validator = Draft202012Validator(schema)
    for err in sorted(validator.iter_errors(doc), key=lambda e: list(e.path)):
        issues.append(ValidationIssue("SCHEMA_INVALID", f"{label}: {err.message}"))


def validate_control_plane(
    *,
    allow_pending_charter: bool = True,
    check_claim_transition: tuple[str, str] | None = None,
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []

    if not CHARTER_FILE.exists():
        issues.append(ValidationIssue("CHARTER_MISSING", "Charter file missing"))
        return issues

    if not CHARTER_SOURCE_RECORD.exists():
        issues.append(ValidationIssue("CHARTER_SOURCE_RECORD_MISSING", "CHARTER_SOURCE_RECORD.yaml missing"))
    if not CHARTER_APPROVAL_RECORD.exists():
        issues.append(ValidationIssue("CHARTER_APPROVAL_MISSING", "CHARTER_APPROVAL_RECORD.yaml missing"))
    else:
        approval = load_yaml(CHARTER_APPROVAL_RECORD)
        if approval.get("status") == "GATE_0_PASS" or approval.get("approved") is True:
            # Only valid with explicit approver — still not auto GATE_0_PASS for ecosystem
            if not approval.get("approver"):
                issues.append(
                    ValidationIssue(
                        "ILLEGAL_APPROVAL",
                        "Charter marked approved without approver",
                    )
                )
        if not allow_pending_charter and approval.get("status") == "PRODUCT_CHARTER_APPROVAL_PENDING_EDMUND":
            issues.append(ValidationIssue("CHARTER_PENDING", "Charter approval still pending"))

    req_path = REQUIREMENTS / "requirements.yaml"
    if not req_path.exists():
        issues.append(ValidationIssue("REQUIREMENTS_MISSING", "requirements.yaml missing"))
        return issues

    req_doc = load_yaml(req_path)
    _validate_schema(req_doc, REQUIREMENTS / "requirements.schema.json", "requirements", issues)
    reqs = req_doc.get("requirements") or []
    ids = [r.get("id") for r in reqs]
    if len(ids) != len(set(ids)):
        dupes = sorted({i for i in ids if ids.count(i) > 1})
        issues.append(ValidationIssue("DUPLICATE_REQUIREMENT_ID", f"Duplicate IDs: {dupes}"))

    known_repos = set()
    inv_path = REPOSITORIES / "repository_inventory.yaml"
    if inv_path.exists():
        inv = load_yaml(inv_path)
        known_repos = {r["name"] for r in inv.get("repositories") or []}
    known_repos.add("CONTROL_PLANE_PENDING_DECISION")
    known_repos.add("ALL_FIRST_PARTY")  # not a repo but device scope only

    owner_graph: dict[str, list[str]] = defaultdict(list)
    dep_graph: dict[str, list[str]] = {}
    id_set = set(ids)

    for r in reqs:
        rid = r["id"]
        if not r.get("source_section") or r.get("source_line_start") is None:
            issues.append(ValidationIssue("MISSING_SOURCE_REF", f"{rid} missing source reference"))
        owner = r.get("owner_repository")
        if not owner:
            issues.append(ValidationIssue("MISSING_OWNER", f"{rid} has no owner"))
        elif owner not in known_repos and owner != "CONTROL_PLANE_PENDING_DECISION":
            # Allow owners that are canonical names even if missing locally
            if owner not in known_repos:
                issues.append(
                    ValidationIssue(
                        "UNKNOWN_OWNER_REPO",
                        f"{rid} owner_repository unknown: {owner}",
                        severity="warning",
                    )
                )
        for s in r.get("supporting_repositories") or []:
            if s not in known_repos:
                issues.append(
                    ValidationIssue(
                        "UNKNOWN_SUPPORTING_REPO",
                        f"{rid} supporting repo unknown: {s}",
                        severity="warning",
                    )
                )
        for st_field in ("claim_state", "implementation_state", "validation_state", "certification_state"):
            val = r.get(st_field)
            if val not in EXTENDED_STATES and val not in (
                "NOT_STARTED",
                "DOCUMENTED_DESIGN",
                "TARGET",
                "NOT_CLAIMABLE",
                "STANDARD_NOT_AVAILABLE",
            ):
                issues.append(ValidationIssue("UNSUPPORTED_CLAIM_STATE", f"{rid} {st_field}={val}"))
        if r.get("certification_state") == "CERTIFIED" and not (r.get("required_evidence")):
            issues.append(ValidationIssue("ILLEGAL_CERTIFICATION", f"{rid} CERTIFIED without evidence"))
        if r.get("claim_state") == "CERTIFIED" and r.get("certification_state") not in ("CERTIFIED",):
            issues.append(
                ValidationIssue(
                    "ILLEGAL_CERTIFICATION",
                    f"{rid} claim_state CERTIFIED without certification_state CERTIFIED",
                )
            )
        if r.get("claim_state") in ("HARDWARE_MEASURED", "FIELD_VALIDATED") and "REQUIRES_LOCAL_HARDWARE" not in (
            r.get("blockers") or []
        ):
            # Must have physical evidence linkage for measured claims — reject if marked measured without blockers/evidence
            if r.get("claim_state") == "HARDWARE_MEASURED":
                issues.append(
                    ValidationIssue(
                        "PHYSICAL_EVIDENCE_REJECTION",
                        f"{rid} claims HARDWARE_MEASURED without physical evidence pathway",
                    )
                )
        deps = r.get("dependencies") or []
        dep_graph[rid] = deps
        for d in deps:
            if d not in id_set and d:
                issues.append(ValidationIssue("UNKNOWN_DEPENDENCY", f"{rid} depends on unknown {d}"))
            owner_graph[rid].append(d)

    # Circular dependency detection (DFS)
    visiting: set[str] = set()
    visited: set[str] = set()

    def dfs(node: str, stack: list[str]) -> None:
        if node in visiting:
            cycle = " -> ".join(stack[stack.index(node) :] + [node])
            issues.append(ValidationIssue("CIRCULAR_DEPENDENCY", f"Cycle detected: {cycle}"))
            return
        if node in visited or node not in dep_graph:
            return
        visiting.add(node)
        for nxt in dep_graph.get(node, []):
            dfs(nxt, stack + [node])
        visiting.remove(node)
        visited.add(node)

    for node in dep_graph:
        dfs(node, [])

    claims_path = CLAIMS / "claims.yaml"
    if claims_path.exists():
        claims_doc = load_yaml(claims_path)
        _validate_schema(claims_doc, CLAIMS / "claim.schema.json", "claims", issues)
        for c in claims_doc.get("claims") or []:
            if c.get("claim_state") not in EXTENDED_STATES:
                issues.append(
                    ValidationIssue("UNSUPPORTED_CLAIM_STATE", f"{c.get('claim_id')} state {c.get('claim_state')}")
                )
            if c.get("certification_state") == "CERTIFIED" and not c.get("evidence_ids"):
                issues.append(
                    ValidationIssue(
                        "ILLEGAL_CERTIFICATION",
                        f"{c.get('claim_id')} CERTIFIED without evidence_ids",
                    )
                )

    if check_claim_transition:
        frm, to = check_claim_transition
        if not is_transition_allowed(frm, to):
            issues.append(
                ValidationIssue(
                    "ILLEGAL_CLAIM_TRANSITION",
                    f"Transition {frm} -> {to} is not allowed",
                )
            )

    gate_path = GATES / "gate_status.yaml"
    if gate_path.exists():
        gate_doc = load_yaml(gate_path)
        _validate_schema(gate_doc, GATES / "gate.schema.json", "gate_status", issues)
        if gate_doc.get("overall_status_token") == "GATE_0_PASS":
            approval = load_yaml(CHARTER_APPROVAL_RECORD) if CHARTER_APPROVAL_RECORD.exists() else {}
            approved = bool(approval.get("approved") is True and approval.get("approver")) or (
                str(approval.get("status") or "").upper() == "APPROVED" and bool(approval.get("approver"))
            )
            # pending owners block GATE_0_PASS
            pending_owners = False
            own_path = REPOSITORIES / "repository_ownership.yaml"
            if own_path.exists():
                own = load_yaml(own_path)
                if own.get("pending_decision_owners"):
                    pending_owners = True
                if "CONTROL_PLANE_PENDING_DECISION" in (own.get("owner_to_requirements") or {}):
                    pending_owners = True
            req_pending = False
            if req_path.exists():
                for r in (load_yaml(req_path).get("requirements") or []):
                    if r.get("owner_repository") == "CONTROL_PLANE_PENDING_DECISION":
                        req_pending = True
                        break
            if not approved or pending_owners or req_pending:
                issues.append(
                    ValidationIssue(
                        "ILLEGAL_GATE_0_PASS",
                        "GATE_0_PASS claimed without Edmund approval evidence and cleared pending owners",
                    )
                )
        for c in gate_doc.get("criteria") or []:
            if not c.get("evidence") and not c.get("blockers"):
                issues.append(
                    ValidationIssue(
                        "GATE_CRITERION_INCOMPLETE",
                        f"{c.get('criterion_id')} lacks evidence and blockers",
                    )
                )

    dep_path = GATES / "gate_dependency_graph.yaml"
    if dep_path.exists():
        gdeps = load_yaml(dep_path).get("dependencies") or {}
        # ensure acyclic numeric gates
        for g, deps in gdeps.items():
            for d in deps:
                if int(d) >= int(g):
                    issues.append(
                        ValidationIssue(
                            "GATE_DEP_INVALID",
                            f"Gate {g} cannot depend on {d}",
                        )
                    )

    evid_path = EVIDENCE / "evidence_registry.yaml"
    if evid_path.exists():
        evid = load_yaml(evid_path)
        _validate_schema(evid, EVIDENCE / "evidence.schema.json", "evidence", issues)
        for e in evid.get("entries") or []:
            if not e.get("provenance"):
                issues.append(ValidationIssue("EVIDENCE_NO_PROVENANCE", f"{e.get('evidence_id')} missing provenance"))
            if e.get("physical") is True:
                # Must be linked to physical registry
                phys = load_yaml(GATES / "physical_gate_registry.yaml") if (GATES / "physical_gate_registry.yaml").exists() else {}
                phys_ids = {x["id"] for x in phys.get("entries") or []}
                if e.get("physical_registry_id") not in phys_ids:
                    issues.append(
                        ValidationIssue(
                            "PHYSICAL_EVIDENCE_REJECTION",
                            f"{e.get('evidence_id')} marked physical without registry linkage",
                        )
                    )

    # Preserve original external/physical registries
    for name in ("EXTERNAL_GATE_REGISTRY.json", "PHYSICAL_EVIDENCE_REGISTRY.json", "CROSS_REPO_VERSION_LOCK.json"):
        if not (ROOT / name).exists():
            issues.append(ValidationIssue("PRESERVED_ARTIFACT_MISSING", f"Required preserved artifact missing: {name}"))

    backlog = BACKLOG / "master_gap_backlog.yaml"
    if backlog.exists():
        _validate_schema(load_yaml(backlog), BACKLOG / "gap.schema.json", "backlog", issues)

    return issues


def issues_block_exit(issues: list[ValidationIssue]) -> bool:
    return any(i.severity == "error" for i in issues)
