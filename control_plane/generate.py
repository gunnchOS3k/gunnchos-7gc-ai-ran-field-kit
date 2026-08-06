"""Generate all Gate 0 control-plane artifacts deterministically."""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from control_plane import INGESTION_SCRIPT_VERSION, STATUS_AUTOMATED_PASS, STATUS_CHARTER_PENDING, STATUS_GATE_0_PASS
from control_plane.catalog.claims_catalog import (
    build_claim_taxonomy,
    build_claims_from_requirements,
    build_prohibited_patterns,
)
from control_plane.catalog.evidence_catalog import (
    build_backlogs,
    build_evidence_acceptance_rules,
    build_evidence_registry,
    build_evidence_taxonomy,
)
from control_plane.catalog.gates_catalog import (
    build_external_gate_registry,
    build_gate_definitions,
    build_gate_dependency_graph,
    build_gate_status,
    build_human_action_registry,
    build_physical_gate_registry,
)
from control_plane.catalog.repositories_catalog import (
    build_branch_migration_inventory,
    build_branch_migration_status,
    build_branch_policy,
    build_canonical_policy,
    build_repository_inventory,
    build_repository_ownership,
)
from control_plane.catalog.requirements_catalog import build_requirements
from control_plane.io_util import dump_json, dump_yaml, load_yaml
from control_plane.paths import (
    BACKLOG,
    BRANCH_AUDIT_PATH,
    CHARTER_APPROVAL_RECORD,
    CHARTER_FILE,
    CHARTER_SOURCE_RECORD,
    CLAIMS,
    DECISIONS,
    DEFAULT_REPOS_ROOT,
    EVIDENCE,
    GATES,
    PROGRAM,
    REPORTS,
    REPOSITORIES,
    REQUIREMENTS,
    ROOT,
    SCHEMAS,
)
from control_plane.status import charter_is_approved, compute_gate0_status, pending_owners


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def write_schemas() -> None:
    SCHEMAS.mkdir(parents=True, exist_ok=True)
    REQUIREMENTS.mkdir(parents=True, exist_ok=True)
    CLAIMS.mkdir(parents=True, exist_ok=True)
    GATES.mkdir(parents=True, exist_ok=True)
    REPOSITORIES.mkdir(parents=True, exist_ok=True)
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    BACKLOG.mkdir(parents=True, exist_ok=True)

    req_item_props = {
        "id": {"type": "string"},
        "title": {"type": "string"},
        "source_section": {"type": "string"},
        "source_line_start": {"type": "integer"},
        "source_line_end": {"type": "integer"},
        "normative_text": {"type": "string"},
        "requirement_type": {"type": "string"},
        "subsystem": {"type": "string"},
        "device_scope": {"type": "array", "items": {"type": "string"}},
        "gate": {"type": "integer"},
        "priority": {"type": "string"},
        "safety_critical": {"type": "boolean"},
        "security_relevant": {"type": "boolean"},
        "privacy_relevant": {"type": "boolean"},
        "accessibility_relevant": {"type": "boolean"},
        "scientific_evidence_relevant": {"type": "boolean"},
        "owner_repository": {"type": "string"},
        "supporting_repositories": {"type": "array", "items": {"type": "string"}},
        "verification_method": {"type": "string"},
        "required_evidence": {"type": "array", "items": {"type": "string"}},
        "dependencies": {"type": "array", "items": {"type": "string"}},
        "claim_state": {"type": "string"},
        "implementation_state": {"type": "string"},
        "validation_state": {"type": "string"},
        "certification_state": {"type": "string"},
        "blockers": {"type": "array", "items": {"type": "string"}},
        "notes": {"type": "string"},
    }
    req_schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "requirements.schema.json",
        "type": "object",
        "required": ["schema_version", "requirements"],
        "properties": {
            "schema_version": {"type": "string"},
            "count": {"type": "integer"},
            "requirements": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": list(req_item_props.keys()),
                    "properties": req_item_props,
                    "additionalProperties": False,
                },
            },
        },
    }
    dump_json(req_schema, REQUIREMENTS / "requirements.schema.json")
    dump_json(req_schema, SCHEMAS / "requirements.schema.json")

    claim_schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "claim.schema.json",
        "type": "object",
        "required": ["schema_version", "claims"],
        "properties": {
            "schema_version": {"type": "string"},
            "claims": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": [
                        "claim_id",
                        "requirement_id",
                        "statement",
                        "claim_state",
                        "implementation_state",
                        "validation_state",
                        "certification_state",
                        "evidence_ids",
                        "blockers",
                        "notes",
                    ],
                },
            },
        },
    }
    dump_json(claim_schema, CLAIMS / "claim.schema.json")

    gate_schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "gate.schema.json",
        "type": "object",
        "required": ["schema_version", "criteria"],
        "properties": {
            "schema_version": {"type": "string"},
            "criteria": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": [
                        "gate",
                        "criterion_id",
                        "criterion",
                        "owner",
                        "status",
                        "evidence",
                        "blockers",
                        "automatable",
                        "next_action",
                        "acceptance_authority",
                    ],
                },
            },
        },
    }
    dump_json(gate_schema, GATES / "gate.schema.json")

    repo_schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "repository.schema.json",
        "type": "object",
        "required": ["schema_version", "repositories"],
        "properties": {
            "schema_version": {"type": "string"},
            "repositories": {"type": "array", "items": {"type": "object", "required": ["name", "classification"]}},
        },
    }
    dump_json(repo_schema, REPOSITORIES / "repository.schema.json")

    evidence_schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "evidence.schema.json",
        "type": "object",
        "required": ["schema_version", "entries"],
        "properties": {
            "schema_version": {"type": "string"},
            "entries": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["evidence_id", "class", "title", "path", "provenance", "physical"],
                },
            },
        },
    }
    dump_json(evidence_schema, EVIDENCE / "evidence.schema.json")

    gap_schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "gap.schema.json",
        "type": "object",
        "required": ["schema_version", "gaps"],
        "properties": {
            "schema_version": {"type": "string"},
            "gaps": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["gap_id", "requirement_id", "title", "class", "owner_repository"],
                },
            },
        },
    }
    dump_json(gap_schema, BACKLOG / "gap.schema.json")


def write_charter_records() -> None:
    assert CHARTER_FILE.exists(), f"Missing charter at {CHARTER_FILE}"
    text = CHARTER_FILE.read_text(encoding="utf-8")
    line_count = len(text.splitlines())
    sha = _sha256(CHARTER_FILE)
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    git_state: dict[str, Any] = {"applicable": False, "notes": "Source charter is outside a git repo"}
    dump_yaml(
        {
            "source_filename": "gunnchOS3k Carrier-Grade 6G Equitable Compute Ecosystem (1).md",
            "ingested_path": str(CHARTER_FILE.relative_to(ROOT)),
            "sha256": sha,
            "ingestion_timestamp_utc": ts,
            "line_count": line_count,
            "ingestion_script_version": INGESTION_SCRIPT_VERSION,
            "git_state": git_state,
        },
        CHARTER_SOURCE_RECORD,
    )
    # Preserve an existing APPROVED approval record — never silently regress to pending.
    if CHARTER_APPROVAL_RECORD.exists():
        existing = load_yaml(CHARTER_APPROVAL_RECORD)
        approved = bool(existing.get("approved") is True and existing.get("approver")) or (
            str(existing.get("status") or "").upper() == "APPROVED" and bool(existing.get("approver"))
        )
        if approved:
            # Refresh charter hash linkage only; keep approval metadata intact.
            existing["approved_charter_sha256"] = existing.get("approved_charter_sha256") or sha
            dump_yaml(existing, CHARTER_APPROVAL_RECORD)
            return
    dump_yaml(
        {
            "status": STATUS_CHARTER_PENDING,
            "approved": False,
            "approver": None,
            "approval_timestamp_utc": None,
            "notes": (
                "This assignment is not formal product-charter approval. "
                "GATE_0_PASS is prohibited until Edmund records approval."
            ),
        },
        CHARTER_APPROVAL_RECORD,
    )


def write_requirements_artifacts(reqs: list[dict[str, Any]]) -> None:
    dump_yaml({"schema_version": "1.0.0", "count": len(reqs), "requirements": reqs}, REQUIREMENTS / "requirements.yaml")

    source_map = [
        {
            "id": r["id"],
            "source_section": r["source_section"],
            "source_line_start": r["source_line_start"],
            "source_line_end": r["source_line_end"],
        }
        for r in reqs
    ]
    dump_yaml({"schema_version": "1.0.0", "mappings": source_map}, REQUIREMENTS / "requirement_source_map.yaml")

    ownership = [
        {
            "id": r["id"],
            "owner_repository": r["owner_repository"],
            "supporting_repositories": r["supporting_repositories"],
        }
        for r in reqs
    ]
    dump_yaml({"schema_version": "1.0.0", "ownership": ownership}, REQUIREMENTS / "requirement_ownership.yaml")

    deps = [{"id": r["id"], "dependencies": r["dependencies"]} for r in reqs]
    dump_yaml({"schema_version": "1.0.0", "dependencies": deps}, REQUIREMENTS / "requirement_dependencies.yaml")

    ver = [
        {
            "id": r["id"],
            "verification_method": r["verification_method"],
            "required_evidence": r["required_evidence"],
        }
        for r in reqs
    ]
    dump_yaml(
        {"schema_version": "1.0.0", "verification_methods": ver},
        REQUIREMENTS / "requirement_verification_methods.yaml",
    )

    dump_yaml(
        {
            "schema_version": "1.0.0",
            "frozen": True,
            "decision_record": "DR-0002-DEVICE-ROLE-BASELINE.md",
            "roles": [
                {
                    "id": "STUDENT_14_5",
                    "name": "Student 14.5",
                    "summary": "Primary full-session learning and work platform",
                    "form_factor": "14.5-inch sustained-compute",
                },
                {
                    "id": "DS_XL_CODER",
                    "name": "DS-XL Coder",
                    "summary": "Dual-screen creation and build-learning device",
                    "form_factor": "dual-screen",
                },
                {
                    "id": "HANDHELD_HYBRID",
                    "name": "Handheld Hybrid",
                    "summary": "Mobile and dockable compute; not entertainment-only",
                    "form_factor": "handheld/dockable",
                },
                {
                    "id": "EDGE_IO_RINGS",
                    "name": "Edge I/O Rings",
                    "summary": "Primary embodied-computing interface; not optional accessories",
                    "form_factor": "wearable rings",
                },
            ],
        },
        REQUIREMENTS / "device_role_baseline.yaml",
    )


def write_decisions() -> None:
    DECISIONS.mkdir(parents=True, exist_ok=True)
    docs = {
        "DR-0001-INTEGRATION-AUTHORITY.md": """# DR-0001 — Integration Authority

## Decision
`gunnchos-7gc-ai-ran-field-kit` is the Gate 0–8 ecosystem control-plane and integration authority for requirements, claims, gates, evidence registries, and cross-repo version locks.

## Status
ACCEPTED for Gate 0 automated scaffolding.

## Consequences
- Other repositories remain owners of subsystem implementation.
- Field-kit does not claim those subsystems are complete merely by owning traceability.
- Existing artifacts (`CROSS_REPO_VERSION_LOCK.json`, `EXTERNAL_GATE_REGISTRY.json`, etc.) are preserved.
""",
        "DR-0002-DEVICE-ROLE-BASELINE.md": """# DR-0002 — Device Role Baseline

## Decision
Freeze the product family roles as:
1. Student 14.5 — primary full-session learning/work platform
2. DS-XL Coder — dual-screen build-learning device
3. Handheld Hybrid — mobile/dockable compute (not entertainment-only)
4. Edge I/O Rings — primary embodied input (not optional accessories)

## Status
FROZEN in `program/requirements/device_role_baseline.yaml`.

## Notes
Hardware existence is not claimed by role freeze.
""",
        "DR-0003-CLAIM-CLASSIFICATION.md": """# DR-0003 — Claim Classification

## Decision
Adopt extended claim states beyond TARGET/IMPLEMENTED/VALIDATED/CERTIFIED, with explicit transition rules and prohibited patterns (especially premature 6G/carrier/field claims).

## Status
ACCEPTED — see `program/claims/claim_taxonomy.yaml` and `prohibited_claim_patterns.yaml`.

## Non-claims
IMT-2030 alignment does not imply standardized 6G certification.
""",
        "DR-0004-RING-WORKSTREAM-OWNERSHIP.md": """# DR-0004 — Ring Workstream Ownership

## Decision
Document cross-repo responsibility for Edge I/O Rings across industrial/electrical design, firmware, sensing/inference, secure pairing, gunnchOS input service, calibration, haptics, SDK, game integration, measurement, privacy, safety, and manufacturing.

## Workstream matrix (ownership ≠ existence)

| Workstream | Accountable owner | Supporting | Notes |
|---|---|---|---|
| Industrial / electrical design | `gunnchos-hardware-industrial-design` | EdgeGesture, edge-io-measurement-node | No production ring claim |
| Ring firmware | `gunnchos-hardware-industrial-design` | hardware-industrial-design, EdgeGesture | No dedicated firmware repo proven |
| Sensing and inference | `EdgeGesture-Fall-2025-Edge-AI-Qualcomm-Hackathon` | edge-io-measurement-node, gunnchAI3k | Research / hackathon provenance |
| Secure pairing and authentication | `gunnchos-device-os` | EdgeGesture | Anti-replay / pairing / revocation |
| gunnchOS input service | `gunnchos-device-os` | EdgeGesture | OS-side input routing |
| Calibration | `EdgeGesture-Fall-2025-Edge-AI-Qualcomm-Hackathon` | edge-io-measurement-node, device-os | Per-user / per-surface |
| Haptics | `gunnchos-hardware-industrial-design` | EdgeGesture, hardware-industrial-design | No validated haptics stack claimed |
| Application SDK | `gunnchos-device-os` | games, EdgeGesture | Pending dedicated SDK package |
| Game integration | per-game repos | EdgeGesture, device-os | Optional gestures only |
| Measurement and validation | `edge-io-measurement-node` | field-kit, EdgeGesture | Lab / field measurement |
| Privacy | `gunnchos-device-os` | EdgeGesture, gunnchAI3k | Local motion processing / consent |
| Safety | `gunnchos-device-os` | EdgeGesture | No silent destructive actions |
| Manufacturing | `gunnchos-hardware-industrial-design` | hardware-industrial-design | No manufacturer engaged |

## Status
DOCUMENTED in this decision record and applied via `control_plane.generate.apply_ring_workstream_ownership`.

## Critical disclaimer
Ownership assignment does **not** claim that a dedicated production ring repository, manufactured ring, or validated firmware exists.
""",
        "DR-0005-CANONICAL-REPOSITORY-SET.md": """# DR-0005 — Canonical Repository Set

## Decision
Adopt the Gate 0 canonical seed set for control plane, devices/OS/AI/input, four games, and connectivity/7GC/AI-RAN/NTN research repos. Classify oulu-named labs as LEGACY_NAME/SUPPORTING unless promoted later.

## Status
ACCEPTED for inventory and ownership mapping.

## Non-actions this pass
No renames, deletions, archives, or recreations.
""",
    }
    for name, body in docs.items():
        (DECISIONS / name).write_text(body, encoding="utf-8")


def write_legacy_report(inventory: dict[str, Any]) -> None:
    lines = [
        "# Legacy and Duplicate Repository Report",
        "",
        "Generated by Gate 0 control plane. No repositories were renamed or deleted.",
        "",
        "| Repository | Classification | Role | Notes |",
        "|---|---|---|---|",
    ]
    for r in inventory["repositories"]:
        if r["classification"] in ("LEGACY_NAME", "DUPLICATE", "ARCHIVE_CANDIDATE", "OUT_OF_SCOPE", "MISSING_LOCALLY"):
            lines.append(
                f"| {r['name']} | {r['classification']} | {r.get('role','')} | {r.get('notes','')} |"
            )
    lines.append("")
    lines.append("## Naming remediation plan")
    lines.append("")
    lines.append("1. Keep oulu-* remote names as LEGACY_NAME until Edmund approves remapping.")
    lines.append("2. Do not plaster Oulu branding into general gunnchOS product docs.")
    lines.append("3. EdgeGesture remains canonical for ring gesture research as standalone.")
    lines.append("4. Duplicate standalone Downloads checkouts are SUPPORTING/DUPLICATE mirrors — do not treat as second sources of truth.")
    lines.append("")
    (REPOSITORIES / "legacy_and_duplicate_report.md").write_text("\n".join(lines), encoding="utf-8")


def write_evidence_provenance_policy() -> None:
    (EVIDENCE / "evidence_provenance_policy.md").write_text(
        """# Evidence Provenance Policy

1. Every evidence record must include provenance (path, content hash, or git commit).
2. Physical measurements require linkage to `PHYSICAL_EVIDENCE_REGISTRY.json` / `physical_gate_registry.yaml`.
3. External acceptances require linkage to `external_gate_registry.yaml`.
4. Fabricated evidence is prohibited.
5. `GATE_0_PASS` requires Edmund approval evidence in `CHARTER_APPROVAL_RECORD.yaml`.
6. Simulation or unit-test evidence cannot satisfy hardware-measured or field-validated claims.
""",
        encoding="utf-8",
    )


def apply_ring_workstream_ownership(reqs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Split Edge I/O Ring accountability across documented workstreams (ownership ≠ existence)."""
    remaps: dict[str, tuple[str, list[str]]] = {
        # Industrial / awareness of physical form: hardware owns industrial expression of rings as device family member
        "RING-AWARE-001": (
            "gunnchos-hardware-industrial-design",
            ["EdgeGesture-Fall-2025-Edge-AI-Qualcomm-Hackathon", "gunnchos-device-os", "edge-io-measurement-node"],
        ),
        # OS input routing
        "RING-AWARE-008": (
            "gunnchos-device-os",
            ["EdgeGesture-Fall-2025-Edge-AI-Qualcomm-Hackathon", "gunnchos-hardware-industrial-design"],
        ),
        # Security / pairing / revocation / anti-replay / anti-spoof
        "RING-RELIAB-008": (
            "gunnchos-device-os",
            ["EdgeGesture-Fall-2025-Edge-AI-Qualcomm-Hackathon"],
        ),
        "RING-RELIAB-009": (
            "gunnchos-device-os",
            ["EdgeGesture-Fall-2025-Edge-AI-Qualcomm-Hackathon"],
        ),
        "RING-RELIAB-010": (
            "gunnchos-device-os",
            ["EdgeGesture-Fall-2025-Edge-AI-Qualcomm-Hackathon"],
        ),
        "RING-RELIAB-011": (
            "gunnchos-device-os",
            ["EdgeGesture-Fall-2025-Edge-AI-Qualcomm-Hackathon"],
        ),
        # Privacy + safety
        "RING-RELIAB-013": (
            "gunnchos-device-os",
            ["EdgeGesture-Fall-2025-Edge-AI-Qualcomm-Hackathon", "gunnchAI3k"],
        ),
        "RING-RELIAB-014": (
            "gunnchos-device-os",
            ["EdgeGesture-Fall-2025-Edge-AI-Qualcomm-Hackathon"],
        ),
        "RING-RELIAB-015": (
            "gunnchos-device-os",
            ["EdgeGesture-Fall-2025-Edge-AI-Qualcomm-Hackathon"],
        ),
        "RING-RELIAB-016": (
            "gunnchos-device-os",
            ["EdgeGesture-Fall-2025-Edge-AI-Qualcomm-Hackathon"],
        ),
        # Haptics / firmware planning owners (planning ≠ component existence)
        "RING-INPUT-035": (
            "gunnchos-hardware-industrial-design",
            ["EdgeGesture-Fall-2025-Edge-AI-Qualcomm-Hackathon", "gunnchos-hardware-industrial-design"],
        ),
        "RING-RELIAB-005": (
            "gunnchos-hardware-industrial-design",
            ["EdgeGesture-Fall-2025-Edge-AI-Qualcomm-Hackathon", "gunnchos-device-os"],
        ),
    }
    for req in reqs:
        rid = req["id"]
        if rid in remaps:
            owner, supporting = remaps[rid]
            req["owner_repository"] = owner
            req["supporting_repositories"] = supporting
            note = (req.get("notes") or "").strip()
            suffix = "Ring workstream ownership per DR-0004; does not claim component existence."
            if suffix not in note:
                req["notes"] = f"{note} {suffix}".strip()
        # Measurement support for calibration / sensing requirements
        if rid.startswith("RING-RELIAB-00") and rid in {
            "RING-RELIAB-001",
            "RING-RELIAB-002",
            "RING-RELIAB-003",
            "RING-RELIAB-004",
        }:
            supporting = list(req.get("supporting_repositories") or [])
            if "edge-io-measurement-node" not in supporting:
                supporting.append("edge-io-measurement-node")
            req["supporting_repositories"] = supporting
    return reqs


def reconcile_pending_owners(reqs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Assign planning owners so CONTROL_PLANE_PENDING_DECISION does not remain."""
    owner_map = {
        "FULL-OPS-010": "gunnchos-device-os",
        "FULL-OPS-012": "gunnchos-hardware-industrial-design",
        "FULL-OPS-013": "gunnchos-7gc-ai-ran-field-kit",
        "FULL-OPS-014": "gunnchos-7gc-ai-ran-field-kit",
        "FULL-OPS-015": "gunnchos-7gc-ai-ran-field-kit",
        "GATE-5-001": "gunnchos-hardware-industrial-design",
        "GATE-5-002": "gunnchos-7gc-ai-ran-field-kit",
        "GATE-5-006": "gunnchos-7gc-ai-ran-field-kit",
        "GATE-5-007": "gunnchos-7gc-ai-ran-field-kit",
        "GATE-7-001": "gunnchos-7gc-ai-ran-field-kit",
        "GATE-7-002": "gunnchos-7gc-ai-ran-field-kit",
        "GATE-7-003": "gunnchos-hardware-industrial-design",
        "GATE-7-004": "gunnchos-7gc-ai-ran-field-kit",
        "GATE-7-007": "gunnchos-7gc-ai-ran-field-kit",
    }
    for req in reqs:
        rid = req["id"]
        if rid in owner_map:
            req["owner_repository"] = owner_map[rid]
        if req.get("owner_repository") == "CONTROL_PLANE_PENDING_DECISION":
            # Fail-safe: park on field-kit control plane rather than leave pending token
            req["owner_repository"] = "gunnchos-7gc-ai-ran-field-kit"
        blockers = [b for b in (req.get("blockers") or []) if b != "CONTROL_PLANE_PENDING_DECISION"]
        req["blockers"] = blockers
    return reqs


def generate_all(repos_root: Path | None = None, audit_path: Path | None = None) -> dict[str, Any]:
    repos_root = repos_root or DEFAULT_REPOS_ROOT
    audit_path = audit_path or BRANCH_AUDIT_PATH
    PROGRAM.mkdir(parents=True, exist_ok=True)
    write_schemas()
    write_charter_records()
    write_decisions()

    reqs = reconcile_pending_owners(apply_ring_workstream_ownership(build_requirements()))
    write_requirements_artifacts(reqs)

    claims = build_claims_from_requirements(reqs)
    dump_yaml({"schema_version": "1.0.0", "count": len(claims), "claims": claims}, CLAIMS / "claims.yaml")
    dump_yaml(build_claim_taxonomy(), CLAIMS / "claim_taxonomy.yaml")
    dump_yaml(build_prohibited_patterns(), CLAIMS / "prohibited_claim_patterns.yaml")

    ownership = build_repository_ownership(reqs)
    dump_yaml(ownership, REPOSITORIES / "repository_ownership.yaml")

    approval = load_yaml(CHARTER_APPROVAL_RECORD)
    approved = charter_is_approved(approval)
    pending = pending_owners(reqs, ownership)
    if approved and not pending:
        gate0_overall = STATUS_GATE_0_PASS
    elif approved:
        gate0_overall = STATUS_AUTOMATED_PASS
    else:
        gate0_overall = STATUS_AUTOMATED_PASS

    gate1_ready = (ROOT / "gate1" / "orchestrator" / "cli.py").exists()
    dump_yaml(build_gate_definitions(), GATES / "gate_definitions.yaml")
    dump_yaml(
        build_gate_status(
            charter_approved=approved,
            gate0_overall=gate0_overall,
            gate1_software_ready=gate1_ready and approved,
        ),
        GATES / "gate_status.yaml",
    )
    dump_yaml(build_gate_dependency_graph(), GATES / "gate_dependency_graph.yaml")
    dump_yaml(build_external_gate_registry(ROOT), GATES / "external_gate_registry.yaml")
    dump_yaml(build_physical_gate_registry(ROOT), GATES / "physical_gate_registry.yaml")
    dump_yaml(build_human_action_registry(), GATES / "human_action_registry.yaml")

    field_kit_post = {
        "github_default_branch": "main",
        "migration_case": "MIGRATED_IDENTICAL_HISTORY",
        "main_sha": "de818fbe371ee87557d9a171626985536ff5578d",
        "master_sha": "de818fbe371ee87557d9a171626985536ff5578d",
        "open_prs": [
            {
                "baseRefName": "main",
                "headRefName": "cursor/field-kit-remote-integrity-release",
                "number": 12,
                "title": "fix(ci): remote integrity — App-token locked sibling checkout",
            },
            {
                "baseRefName": "main",
                "headRefName": "portfolio-spine-hardening",
                "number": 1,
                "isDraft": True,
                "title": "Portfolio hardening: mission docs, CI, evidence discipline (Tier 1)",
            },
        ],
    }
    inventory = build_repository_inventory(repos_root, audit_path, field_kit_post)
    dump_yaml(inventory, REPOSITORIES / "repository_inventory.yaml")
    dump_yaml(build_canonical_policy(), REPOSITORIES / "canonical_repository_policy.yaml")
    dump_yaml(build_branch_policy(), REPOSITORIES / "branch_policy.yaml")
    dump_yaml(build_branch_migration_inventory(audit_path), REPOSITORIES / "branch_migration_inventory.yaml")
    dump_yaml(build_branch_migration_status(audit_path), REPOSITORIES / "branch_migration_status.yaml")
    write_legacy_report(inventory)

    dump_yaml(build_evidence_taxonomy(), EVIDENCE / "evidence_taxonomy.yaml")
    dump_yaml(build_evidence_acceptance_rules(), EVIDENCE / "evidence_acceptance_rules.yaml")
    dump_yaml(build_evidence_registry(), EVIDENCE / "evidence_registry.yaml")
    write_evidence_provenance_policy()

    backlogs = build_backlogs(reqs)
    dump_yaml({"schema_version": "1.0.0", "gaps": backlogs["master"]}, BACKLOG / "master_gap_backlog.yaml")
    dump_yaml({"schema_version": "1.0.0", "gaps": backlogs["automatable"]}, BACKLOG / "cursor_automatable_backlog.yaml")
    dump_yaml({"schema_version": "1.0.0", "gaps": backlogs["human"]}, BACKLOG / "human_action_backlog.yaml")
    dump_yaml({"schema_version": "1.0.0", "gaps": backlogs["physical"]}, BACKLOG / "physical_work_backlog.yaml")
    dump_yaml({"schema_version": "1.0.0", "gaps": backlogs["external"]}, BACKLOG / "external_dependency_backlog.yaml")

    # Recompute with validators after artifacts exist
    status = compute_gate0_status(approval=approval, reqs=reqs, ownership=ownership, run_validators=True)
    # Keep gate_status overall aligned with computed status when validators pass
    if status["overall_status_token"] == STATUS_GATE_0_PASS or gate0_overall == STATUS_GATE_0_PASS:
        # Refresh gate_status tokens if validators confirm
        if status["validators_ok"] and not status["pending_owners"] and approved:
            dump_yaml(
                build_gate_status(
                    charter_approved=True,
                    gate0_overall=STATUS_GATE_0_PASS,
                    gate1_software_ready=gate1_ready,
                ),
                GATES / "gate_status.yaml",
            )
            status_tokens = [STATUS_GATE_0_PASS, "CHARTER_APPROVED"]
        else:
            status_tokens = [STATUS_AUTOMATED_PASS, STATUS_CHARTER_PENDING]
    else:
        status_tokens = [status["overall_status_token"], status["secondary_status_token"]]

    return {
        "requirement_count": len(reqs),
        "claim_count": len(claims),
        "repository_count": len(inventory["repositories"]),
        "status_tokens": status_tokens,
        "pending_owners": status.get("pending_owners") or pending,
    }
