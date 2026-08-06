"""Evidence and backlog catalogs."""

from __future__ import annotations

from typing import Any


def build_evidence_taxonomy() -> dict[str, Any]:
    return {
        "schema_version": "1.0.0",
        "classes": [
            "DOCUMENT",
            "SCHEMA",
            "UNIT_TEST",
            "INTEGRATION_TEST",
            "SIMULATION",
            "HARDWARE_MEASUREMENT",
            "FIELD_MEASUREMENT",
            "HUMAN_STUDY",
            "EXTERNAL_ACCEPTANCE",
            "CERTIFICATION",
            "PROVENANCE",
        ],
        "rejection_rules": [
            "Physical evidence without PHYSICAL_EVIDENCE_REGISTRY entry is rejected.",
            "CERTIFIED claims without certification evidence IDs are rejected.",
            "FIELD_VALIDATED without human/field evidence is rejected.",
        ],
    }


def build_evidence_acceptance_rules() -> dict[str, Any]:
    return {
        "schema_version": "1.0.0",
        "rules": [
            {
                "id": "EAR-001",
                "rule": "Every evidence record requires provenance (path, hash, or commit).",
            },
            {
                "id": "EAR-002",
                "rule": "Hardware measurement evidence requires physical registry linkage.",
            },
            {
                "id": "EAR-003",
                "rule": "Independent reproduction evidence must identify non-author actor.",
            },
            {
                "id": "EAR-004",
                "rule": "Charter approval evidence must be recorded in CHARTER_APPROVAL_RECORD.yaml.",
            },
            {
                "id": "EAR-005",
                "rule": "GATE_0_PASS is prohibited without Edmund approval evidence.",
            },
        ],
    }


def build_evidence_registry() -> dict[str, Any]:
    return {
        "schema_version": "1.0.0",
        "entries": [
            {
                "evidence_id": "EV-CHARTER-001",
                "class": "DOCUMENT",
                "title": "Ingested product charter",
                "path": "program/charters/GUNNCHOS3K_CARRIER_GRADE_6G_ECOSYSTEM.md",
                "provenance": "CHARTER_SOURCE_RECORD.yaml",
                "supports_claims": ["CLM-SYS-MISSION-001"],
                "physical": False,
            },
            {
                "evidence_id": "EV-REQ-001",
                "class": "SCHEMA",
                "title": "Requirements catalog",
                "path": "program/requirements/requirements.yaml",
                "provenance": "generated_by_control_plane",
                "supports_claims": ["CLM-GATE-0-003"],
                "physical": False,
            },
            {
                "evidence_id": "EV-CLAIM-001",
                "class": "SCHEMA",
                "title": "Claims registry",
                "path": "program/claims/claims.yaml",
                "provenance": "generated_by_control_plane",
                "supports_claims": ["CLM-GATE-0-004"],
                "physical": False,
            },
            {
                "evidence_id": "EV-REPO-001",
                "class": "DOCUMENT",
                "title": "Repository inventory",
                "path": "program/repositories/repository_inventory.yaml",
                "provenance": "generated_by_control_plane",
                "supports_claims": ["CLM-GATE-0-005"],
                "physical": False,
            },
            {
                "evidence_id": "EV-EXT-REG-001",
                "class": "DOCUMENT",
                "title": "Preserved external gate registry",
                "path": "EXTERNAL_GATE_REGISTRY.json",
                "provenance": "preexisting_control_plane_artifact",
                "supports_claims": [],
                "physical": False,
            },
            {
                "evidence_id": "EV-PHYS-REG-001",
                "class": "DOCUMENT",
                "title": "Preserved physical evidence registry (all blocked)",
                "path": "PHYSICAL_EVIDENCE_REGISTRY.json",
                "provenance": "preexisting_control_plane_artifact",
                "supports_claims": [],
                "physical": False,
                "notes": "Registry documents blocked physical items; does not constitute measurements.",
            },
        ],
    }


def build_backlogs(requirements: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    master = []
    automatable = []
    human = []
    physical = []
    external = []
    for req in requirements:
        blockers = req.get("blockers") or []
        if not blockers and req.get("claim_state") in ("DOCUMENTED_DESIGN", "TARGET"):
            if req["gate"] == 0 and req["claim_state"] == "DOCUMENTED_DESIGN":
                continue
            item = {
                "gap_id": f"GAP-{req['id']}",
                "requirement_id": req["id"],
                "title": req["title"],
                "class": "AUTOMATABLE_AFTER_DEPENDENCY"
                if req["gate"] > 0
                else "AUTOMATABLE_NOW",
                "blockers": blockers,
                "owner_repository": req["owner_repository"],
            }
            master.append(item)
            if item["class"] == "AUTOMATABLE_NOW":
                automatable.append(item)
            continue
        for b in blockers:
            item = {
                "gap_id": f"GAP-{req['id']}-{b}",
                "requirement_id": req["id"],
                "title": req["title"],
                "class": b,
                "blockers": blockers,
                "owner_repository": req["owner_repository"],
            }
            master.append(item)
            if b in ("REQUIRES_EDMUND", "REQUIRES_HUMAN_PARTICIPANTS", "REQUIRES_ETHICS_OR_GOVERNANCE_APPROVAL", "PRODUCT_CHARTER_APPROVAL_PENDING_EDMUND"):
                human.append(item)
            elif b in ("REQUIRES_LOCAL_HARDWARE", "REQUIRES_PHYSICAL_PROTOTYPE"):
                physical.append(item)
            elif b in (
                "REQUIRES_EXTERNAL_PARTNER",
                "REQUIRES_CARRIER",
                "REQUIRES_CERTIFICATION_LAB",
                "REQUIRES_MANUFACTURER",
                "REQUIRES_STANDARD_FINALIZATION",
                "BLOCKED_CREDENTIAL_CONFIGURATION",
                "CONTROL_PLANE_PENDING_DECISION",
            ):
                external.append(item)
            elif b == "AUTOMATABLE_NOW" or "AUTOMATABLE" in b:
                automatable.append(item)
    # Deduplicate master by gap_id
    seen = set()
    uniq = []
    for m in master:
        if m["gap_id"] in seen:
            continue
        seen.add(m["gap_id"])
        uniq.append(m)
    return {
        "master": uniq,
        "automatable": automatable,
        "human": human,
        "physical": physical,
        "external": external,
    }
