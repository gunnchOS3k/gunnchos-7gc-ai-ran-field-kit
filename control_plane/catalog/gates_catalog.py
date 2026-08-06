"""Gate 0–8 definitions, status criteria, and registries."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

WORK_CLASSES = [
    "AUTOMATABLE_NOW",
    "AUTOMATABLE_AFTER_DEPENDENCY",
    "REQUIRES_EDMUND",
    "REQUIRES_LOCAL_HARDWARE",
    "REQUIRES_PHYSICAL_PROTOTYPE",
    "REQUIRES_HUMAN_PARTICIPANTS",
    "REQUIRES_ETHICS_OR_GOVERNANCE_APPROVAL",
    "REQUIRES_EXTERNAL_PARTNER",
    "REQUIRES_CARRIER",
    "REQUIRES_CERTIFICATION_LAB",
    "REQUIRES_MANUFACTURER",
    "REQUIRES_STANDARD_FINALIZATION",
    "NOT_CURRENTLY_CLAIMABLE",
]


def _crit(
    gate: int,
    cid: str,
    criterion: str,
    owner: str,
    status: str,
    evidence: list[str],
    blockers: list[str],
    automatable: str,
    next_action: str,
    acceptance_authority: str,
) -> dict[str, Any]:
    return {
        "gate": gate,
        "criterion_id": cid,
        "criterion": criterion,
        "owner": owner,
        "status": status,
        "evidence": evidence,
        "blockers": blockers,
        "automatable": automatable,
        "next_action": next_action,
        "acceptance_authority": acceptance_authority,
    }


def build_gate_definitions() -> dict[str, Any]:
    return {
        "schema_version": "1.0.0",
        "gates": [
            {
                "gate": 0,
                "name": "Vision and Traceability",
                "summary": "Charter, device roles, requirement IDs, claims, ownership",
            },
            {
                "gate": 1,
                "name": "Integrated Development Platform",
                "summary": "OS boot, ring auth input, dock, local AI, game core loops",
            },
            {
                "gate": 2,
                "name": "Device Vertical Slices",
                "summary": "Enclosure, battery/thermal, secure boot, signed update, UX",
            },
            {
                "gate": 3,
                "name": "Ecosystem Alpha",
                "summary": "Continuity, connectivity manager, fleet, threat models, 7GC plans",
            },
            {
                "gate": 4,
                "name": "Field Pilot",
                "summary": "Real users, connectivity, NTN, accessibility, governance",
            },
            {
                "gate": 5,
                "name": "Preproduction",
                "summary": "DFM, supply chain, regulatory, carrier, provisioning",
            },
            {
                "gate": 6,
                "name": "Release Candidate",
                "summary": "No critical defects, factory image, rollback, support lifecycle",
            },
            {
                "gate": 7,
                "name": "Carrier and Market Deployment",
                "summary": "Certifications, manufacturing, support staffing, fleet ops",
            },
            {
                "gate": 8,
                "name": "Standardized 6G Migration",
                "summary": "Map standards, upgrade/replace, conformance, honest 6G language",
            },
        ],
    }


def build_gate_dependency_graph() -> dict[str, Any]:
    return {
        "schema_version": "1.0.0",
        "dependencies": {
            "0": [],
            "1": [0],
            "2": [1],
            "3": [2],
            "4": [3],
            "5": [4],
            "6": [5],
            "7": [6],
            "8": [7],
        },
        "notes": [
            "Gate N requires Gate N-1 baseline criteria to be established (not necessarily passed).",
            "Physical/human/external criteria remain blocked until evidence exists.",
        ],
    }


def build_gate_status(
    *,
    charter_approved: bool = False,
    gate0_overall: str | None = None,
    gate1_software_ready: bool = False,
) -> dict[str, Any]:
    g0_c1_status = "APPROVED" if charter_approved else "PRODUCT_CHARTER_APPROVAL_PENDING_EDMUND"
    g0_c1_blockers = [] if charter_approved else ["REQUIRES_EDMUND"]
    g0_c1_next = (
        "Maintain approval record; proceed to Gate 1 physical evidence"
        if charter_approved
        else "Edmund reviews and records charter approval"
    )
    criteria = [
        _crit(
            0,
            "G0-C1",
            "Product charter approved",
            "Edmund Gunn Jr.",
            g0_c1_status,
            ["program/charters/CHARTER_APPROVAL_RECORD.yaml"],
            g0_c1_blockers,
            "REQUIRES_EDMUND" if not charter_approved else "AUTOMATABLE_NOW",
            g0_c1_next,
            "Edmund Gunn Jr.",
        ),
        _crit(
            0,
            "G0-C2",
            "Device roles frozen",
            "gunnchos-7gc-ai-ran-field-kit",
            "DOCUMENTED_DESIGN",
            ["program/requirements/device_role_baseline.yaml", "program/decisions/DR-0002-DEVICE-ROLE-BASELINE.md"],
            [],
            "AUTOMATABLE_NOW",
            "Maintain device_role_baseline.yaml",
            "Edmund Gunn Jr.",
        ),
        _crit(
            0,
            "G0-C3",
            "Requirement identifiers assigned",
            "gunnchos-7gc-ai-ran-field-kit",
            "DOCUMENTED_DESIGN",
            ["program/requirements/requirements.yaml"],
            [],
            "AUTOMATABLE_NOW",
            "Regenerate via control_plane generate",
            "control_plane validators",
        ),
        _crit(
            0,
            "G0-C4",
            "Claims classified",
            "gunnchos-7gc-ai-ran-field-kit",
            "DOCUMENTED_DESIGN",
            ["program/claims/claims.yaml", "program/claims/claim_taxonomy.yaml"],
            [],
            "AUTOMATABLE_NOW",
            "Keep claims synchronized with requirements",
            "control_plane validators",
        ),
        _crit(
            0,
            "G0-C5",
            "Repository ownership established",
            "gunnchos-7gc-ai-ran-field-kit",
            "DOCUMENTED_DESIGN",
            [
                "program/repositories/repository_ownership.yaml",
                "program/decisions/DR-0005-CANONICAL-REPOSITORY-SET.md",
            ],
            [],
            "AUTOMATABLE_NOW",
            "Maintain reconciled owners; no CONTROL_PLANE_PENDING_DECISION remains",
            "Edmund Gunn Jr.",
        ),
    ]

    # Gate 1: software evidence ready / physical pending after Gate 0 approval reconciliation
    gate1 = [
        ("G1-C1", "gunnchOS boots on representative hardware", "gunnchos-device-os", "REQUIRES_LOCAL_HARDWARE"),
        ("G1-C2", "Ring prototype sends authenticated input", "EdgeGesture-Fall-2025-Edge-AI-Qualcomm-Hackathon", "REQUIRES_PHYSICAL_PROTOTYPE"),
        ("G1-C3", "At least one device docks successfully", "gunnchos-device-os", "REQUIRES_PHYSICAL_PROTOTYPE"),
        ("G1-C4", "gunnchAI3k local runtime functions", "gunnchAI3k", "REQUIRES_LOCAL_HARDWARE"),
        ("G1-C5", "Each game completes one core loop", "gunnchos-7gc-ai-ran-field-kit", "AUTOMATABLE_AFTER_DEPENDENCY"),
    ]
    for cid, text, owner, cls in gate1:
        if gate1_software_ready:
            status = "SOFTWARE_EVIDENCE_READY"
            evidence = [
                "gate1/reports/GATE_1_AUTOMATED_COMPLETION_REPORT.md",
                "gate1/reports/GATE_1_IMPLEMENTATION_MATRIX.md",
                "gate1/evidence/pending",
            ]
            blockers = [cls, "PHYSICAL_EVIDENCE_PENDING"]
            next_action = f"Collect accepted physical evidence for: {text}"
            # Dual token: software ready + physical pending
            # status field carries SOFTWARE_EVIDENCE_READY; PHYSICAL_EVIDENCE_PENDING remains as blocker
        else:
            status = "BLOCKED"
            evidence = []
            blockers = [cls]
            next_action = f"Collect evidence for: {text}"
        criteria.append(
            _crit(1, cid, text, owner, status, evidence, blockers, cls, next_action, "Edmund Gunn Jr.")
        )

    gate2 = [
        ("G2-C1", "Representative enclosure", "REQUIRES_PHYSICAL_PROTOTYPE"),
        ("G2-C2", "Working display and controls", "REQUIRES_PHYSICAL_PROTOTYPE"),
        ("G2-C3", "Real battery and thermal measurements", "REQUIRES_LOCAL_HARDWARE"),
        ("G2-C4", "Secure boot", "REQUIRES_PHYSICAL_PROTOTYPE"),
        ("G2-C5", "Signed update", "REQUIRES_PHYSICAL_PROTOTYPE"),
        ("G2-C6", "Device-specific game UX", "AUTOMATABLE_AFTER_DEPENDENCY"),
        ("G2-C7", "Ring calibration and fallback", "REQUIRES_PHYSICAL_PROTOTYPE"),
    ]
    for cid, text, cls in gate2:
        criteria.append(
            _crit(2, cid, text, "gunnchos-hardware-industrial-design", "BLOCKED", [], [cls], cls, f"Blocked: {text}", "Edmund Gunn Jr.")
        )

    for gate, items in [
        (
            3,
            [
                ("G3-C1", "Cross-device identity and continuity", "AUTOMATABLE_AFTER_DEPENDENCY"),
                ("G3-C2", "Multi-device saves", "AUTOMATABLE_AFTER_DEPENDENCY"),
                ("G3-C3", "Connectivity manager", "AUTOMATABLE_AFTER_DEPENDENCY"),
                ("G3-C4", "Fleet observability", "AUTOMATABLE_AFTER_DEPENDENCY"),
                ("G3-C5", "Security threat models", "AUTOMATABLE_NOW"),
                ("G3-C6", "7GC test plans", "AUTOMATABLE_NOW"),
                ("G3-C7", "Repair procedure", "AUTOMATABLE_NOW"),
            ],
        ),
        (
            4,
            [
                ("G4-C1", "Real users", "REQUIRES_HUMAN_PARTICIPANTS"),
                ("G4-C2", "Real connectivity conditions", "REQUIRES_LOCAL_HARDWARE"),
                ("G4-C3", "Long-duration operation", "REQUIRES_LOCAL_HARDWARE"),
                ("G4-C4", "Terrestrial and NTN experiments", "REQUIRES_EXTERNAL_PARTNER"),
                ("G4-C5", "Accessibility evaluation", "REQUIRES_HUMAN_PARTICIPANTS"),
                ("G4-C6", "Local-language evaluation", "REQUIRES_HUMAN_PARTICIPANTS"),
                ("G4-C7", "Community governance review", "REQUIRES_ETHICS_OR_GOVERNANCE_APPROVAL"),
                ("G4-C8", "Incident and support exercises", "REQUIRES_HUMAN_PARTICIPANTS"),
            ],
        ),
        (
            5,
            [
                ("G5-C1", "Design for manufacture", "REQUIRES_MANUFACTURER"),
                ("G5-C2", "Supply-chain audit", "REQUIRES_EXTERNAL_PARTNER"),
                ("G5-C3", "Regulatory test candidates", "REQUIRES_CERTIFICATION_LAB"),
                ("G5-C4", "Carrier engagement", "REQUIRES_CARRIER"),
                ("G5-C5", "Privacy and security review", "REQUIRES_ETHICS_OR_GOVERNANCE_APPROVAL"),
                ("G5-C6", "Production provisioning", "REQUIRES_MANUFACTURER"),
                ("G5-C7", "Packaging and support system", "REQUIRES_EXTERNAL_PARTNER"),
            ],
        ),
        (
            6,
            [
                ("G6-C1", "No unresolved critical safety or security defects", "REQUIRES_EDMUND"),
                ("G6-C2", "Signed factory image", "REQUIRES_PHYSICAL_PROTOTYPE"),
                ("G6-C3", "Verified update and rollback", "REQUIRES_PHYSICAL_PROTOTYPE"),
                ("G6-C4", "Clean install and recovery", "REQUIRES_PHYSICAL_PROTOTYPE"),
                ("G6-C5", "Complete applications and game paths", "AUTOMATABLE_AFTER_DEPENDENCY"),
                ("G6-C6", "Published support lifecycle", "REQUIRES_EXTERNAL_PARTNER"),
                ("G6-C7", "Pilot evidence accepted", "REQUIRES_EDMUND"),
            ],
        ),
        (
            7,
            [
                ("G7-C1", "Required regional certifications", "REQUIRES_CERTIFICATION_LAB"),
                ("G7-C2", "Carrier or network acceptance", "REQUIRES_CARRIER"),
                ("G7-C3", "Production manufacturing", "REQUIRES_MANUFACTURER"),
                ("G7-C4", "Support staffing", "REQUIRES_EXTERNAL_PARTNER"),
                ("G7-C5", "Fleet operations", "AUTOMATABLE_AFTER_DEPENDENCY"),
                ("G7-C6", "Vulnerability-response process", "AUTOMATABLE_NOW"),
                ("G7-C7", "Repair and replacement inventory", "REQUIRES_EXTERNAL_PARTNER"),
            ],
        ),
        (
            8,
            [
                ("G8-C1", "Map finalized 3GPP/ITU requirements", "REQUIRES_STANDARD_FINALIZATION"),
                ("G8-C2", "Upgrade compatible components", "REQUIRES_STANDARD_FINALIZATION"),
                ("G8-C3", "Replace non-compliant components", "REQUIRES_STANDARD_FINALIZATION"),
                ("G8-C4", "Complete formal conformance testing", "REQUIRES_CERTIFICATION_LAB"),
                ("G8-C5", "6G certification language only after path exists", "REQUIRES_STANDARD_FINALIZATION"),
            ],
        ),
    ]:
        for cid, text, cls in items:
            status = "NOT_CURRENTLY_CLAIMABLE" if cls in (
                "REQUIRES_STANDARD_FINALIZATION",
                "REQUIRES_CERTIFICATION_LAB",
                "REQUIRES_CARRIER",
                "REQUIRES_MANUFACTURER",
            ) else "BLOCKED"
            criteria.append(
                _crit(
                    gate,
                    cid,
                    text,
                    "gunnchos-7gc-ai-ran-field-kit",
                    status,
                    [],
                    [cls],
                    cls,
                    f"Baseline only — blocked until evidence: {text}",
                    "Edmund Gunn Jr.",
                )
            )

    overall = gate0_overall or ("GATE_0_PASS" if charter_approved else "GATE_0_AUTOMATED_PASS")
    secondary = (
        "CHARTER_APPROVED"
        if charter_approved and overall == "GATE_0_PASS"
        else ("CHARTER_APPROVED" if charter_approved else "PRODUCT_CHARTER_APPROVAL_PENDING_EDMUND")
    )
    return {
        "schema_version": "1.0.0",
        "work_classes": WORK_CLASSES,
        "overall_status_token": overall,
        "secondary_status_token": secondary,
        # GATE_0_PASS is allowed only when compute_gate0_status says so; otherwise treat as prohibited.
        "prohibited_status_token": None if overall == "GATE_0_PASS" else "GATE_0_PASS",
        "gate1_status_tokens": [
            "SOFTWARE_EVIDENCE_READY",
            "PHYSICAL_EVIDENCE_PENDING",
            "GATE_1_AUTOMATED_PASS",
        ],
        "criteria": criteria,
    }


def build_external_gate_registry(root: Path) -> dict[str, Any]:
    src = root / "EXTERNAL_GATE_REGISTRY.json"
    entries = []
    if src.exists():
        data = json.loads(src.read_text(encoding="utf-8"))
        for e in data.get("entries", []):
            entries.append(
                {
                    "id": e["id"],
                    "status": e["status"],
                    "evidence_label": e["evidence_label"],
                    "owner": e["owner"],
                    "source_artifact": "EXTERNAL_GATE_REGISTRY.json",
                    "automatable": "REQUIRES_EXTERNAL_PARTNER"
                    if e.get("evidence_label") == "BLOCKED_EXTERNAL"
                    else "NOT_CURRENTLY_CLAIMABLE",
                }
            )
    return {
        "schema_version": "1.0.0",
        "migrated_from": "EXTERNAL_GATE_REGISTRY.json",
        "original_preserved": True,
        "entries": entries,
    }


def build_physical_gate_registry(root: Path) -> dict[str, Any]:
    src = root / "PHYSICAL_EVIDENCE_REGISTRY.json"
    entries = []
    if src.exists():
        data = json.loads(src.read_text(encoding="utf-8"))
        for e in data.get("entries", []):
            entries.append(
                {
                    "id": e["id"],
                    "status": e["status"],
                    "evidence_label": e["evidence_label"],
                    "source_artifact": "PHYSICAL_EVIDENCE_REGISTRY.json",
                    "automatable": "REQUIRES_LOCAL_HARDWARE"
                    if e.get("evidence_label") == "BLOCKED_HARDWARE"
                    else "REQUIRES_EXTERNAL_PARTNER",
                }
            )
    return {
        "schema_version": "1.0.0",
        "migrated_from": "PHYSICAL_EVIDENCE_REGISTRY.json",
        "original_preserved": True,
        "entries": entries,
    }


def build_human_action_registry() -> dict[str, Any]:
    return {
        "schema_version": "1.0.0",
        "entries": [
            {
                "id": "HA-001",
                "action": "Approve product charter",
                "owner": "Edmund Gunn Jr.",
                "status": "PENDING",
                "gate": 0,
                "automatable": "REQUIRES_EDMUND",
            },
            {
                "id": "HA-002",
                "action": "Approve deletion of legacy master branches",
                "owner": "Edmund Gunn Jr.",
                "status": "PENDING",
                "gate": 0,
                "automatable": "REQUIRES_EDMUND",
            },
            {
                "id": "HA-003",
                "action": "Merge field-kit PR #12 after credential configuration",
                "owner": "Edmund Gunn Jr.",
                "status": "PENDING",
                "gate": 0,
                "automatable": "REQUIRES_EDMUND",
            },
            {
                "id": "HA-004",
                "action": "Conduct accessibility evaluation with participants",
                "owner": "research team",
                "status": "PENDING",
                "gate": 4,
                "automatable": "REQUIRES_HUMAN_PARTICIPANTS",
            },
            {
                "id": "HA-005",
                "action": "Independent non-author reproduction",
                "owner": "non_author",
                "status": "PENDING",
                "gate": 5,
                "automatable": "REQUIRES_EXTERNAL_PARTNER",
            },
        ],
    }
