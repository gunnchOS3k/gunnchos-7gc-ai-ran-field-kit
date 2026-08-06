"""Claim taxonomy, transitions, and prohibited patterns."""

from __future__ import annotations

from typing import Any

BASE_STATES = ["TARGET", "IMPLEMENTED", "VALIDATED", "CERTIFIED"]

EXTENDED_STATES = [
    "NOT_STARTED",
    "PLANNED",
    "DOCUMENTED_DESIGN",
    "TARGET",
    "IMPLEMENTED",
    "UNIT_TESTED",
    "INTEGRATION_TESTED",
    "SIMULATION_VALIDATED",
    "HARDWARE_MEASURED",
    "FIELD_VALIDATED",
    "INDEPENDENTLY_REPRODUCED",
    "REGULATORY_TESTED",
    "CARRIER_ACCEPTED",
    "CERTIFIED",
    "BLOCKED_PHYSICAL",
    "BLOCKED_HUMAN",
    "BLOCKED_EXTERNAL",
    "BLOCKED_CREDENTIAL_CONFIGURATION",
    "NOT_CLAIMABLE",
    "STANDARD_NOT_AVAILABLE",
]

# Allowed forward transitions (from -> to). Same-state always allowed.
ALLOWED_TRANSITIONS: dict[str, set[str]] = {
    "NOT_STARTED": {
        "PLANNED",
        "DOCUMENTED_DESIGN",
        "TARGET",
        "BLOCKED_PHYSICAL",
        "BLOCKED_HUMAN",
        "BLOCKED_EXTERNAL",
        "BLOCKED_CREDENTIAL_CONFIGURATION",
        "NOT_CLAIMABLE",
        "STANDARD_NOT_AVAILABLE",
    },
    "PLANNED": {
        "DOCUMENTED_DESIGN",
        "TARGET",
        "NOT_STARTED",
        "BLOCKED_PHYSICAL",
        "BLOCKED_HUMAN",
        "BLOCKED_EXTERNAL",
        "NOT_CLAIMABLE",
    },
    "DOCUMENTED_DESIGN": {
        "TARGET",
        "IMPLEMENTED",
        "BLOCKED_PHYSICAL",
        "BLOCKED_HUMAN",
        "BLOCKED_EXTERNAL",
        "NOT_CLAIMABLE",
        "STANDARD_NOT_AVAILABLE",
    },
    "TARGET": {
        "DOCUMENTED_DESIGN",
        "PLANNED",
        "IMPLEMENTED",
        "BLOCKED_PHYSICAL",
        "BLOCKED_HUMAN",
        "BLOCKED_EXTERNAL",
        "BLOCKED_CREDENTIAL_CONFIGURATION",
        "NOT_CLAIMABLE",
        "STANDARD_NOT_AVAILABLE",
    },
    "IMPLEMENTED": {"UNIT_TESTED", "INTEGRATION_TESTED", "BLOCKED_PHYSICAL", "BLOCKED_EXTERNAL"},
    "UNIT_TESTED": {"INTEGRATION_TESTED", "SIMULATION_VALIDATED", "BLOCKED_PHYSICAL"},
    "INTEGRATION_TESTED": {"SIMULATION_VALIDATED", "HARDWARE_MEASURED", "BLOCKED_PHYSICAL"},
    "SIMULATION_VALIDATED": {"HARDWARE_MEASURED", "BLOCKED_PHYSICAL", "FIELD_VALIDATED"},
    "HARDWARE_MEASURED": {"FIELD_VALIDATED", "REGULATORY_TESTED", "BLOCKED_EXTERNAL"},
    "FIELD_VALIDATED": {
        "INDEPENDENTLY_REPRODUCED",
        "REGULATORY_TESTED",
        "CARRIER_ACCEPTED",
        "CERTIFIED",
    },
    "INDEPENDENTLY_REPRODUCED": {"REGULATORY_TESTED", "CERTIFIED"},
    "REGULATORY_TESTED": {"CARRIER_ACCEPTED", "CERTIFIED"},
    "CARRIER_ACCEPTED": {"CERTIFIED"},
    "CERTIFIED": set(),
    "BLOCKED_PHYSICAL": {"DOCUMENTED_DESIGN", "TARGET", "IMPLEMENTED", "NOT_STARTED"},
    "BLOCKED_HUMAN": {"DOCUMENTED_DESIGN", "TARGET", "FIELD_VALIDATED", "NOT_STARTED"},
    "BLOCKED_EXTERNAL": {"DOCUMENTED_DESIGN", "TARGET", "NOT_STARTED", "NOT_CLAIMABLE"},
    "BLOCKED_CREDENTIAL_CONFIGURATION": {"DOCUMENTED_DESIGN", "TARGET", "NOT_STARTED"},
    "NOT_CLAIMABLE": {"STANDARD_NOT_AVAILABLE", "TARGET", "DOCUMENTED_DESIGN"},
    "STANDARD_NOT_AVAILABLE": {"NOT_CLAIMABLE", "TARGET", "DOCUMENTED_DESIGN"},
}

IMPLIED_FALSEHOODS = [
    "DOCUMENTED_DESIGN does not imply IMPLEMENTED.",
    "UNIT_TESTED does not imply INTEGRATION_TESTED.",
    "SIMULATION_VALIDATED does not imply HARDWARE_MEASURED.",
    "HARDWARE_MEASURED does not imply FIELD_VALIDATED.",
    "FIELD_VALIDATED does not imply CERTIFIED.",
    "A draft paper does not imply peer review.",
    "A dev board does not imply production hardware.",
    "An APK launch does not imply a complete game.",
    "A modem does not by itself imply carrier grade.",
    "IMT-2030 alignment does not imply standardized 6G certification.",
]

PROHIBITED_PATTERNS = [
    {
        "id": "PCP-001",
        "pattern": "commercial 6G certified",
        "reason": "Requires finalized standard and certification path",
    },
    {
        "id": "PCP-002",
        "pattern": "fully carrier certified",
        "reason": "Requires carrier acceptance evidence",
    },
    {
        "id": "PCP-003",
        "pattern": "deployed across seven global campuses",
        "reason": "Requires field deployment evidence",
    },
    {
        "id": "PCP-004",
        "pattern": "manufacturing ready",
        "reason": "Requires DFM and manufacturing evidence",
    },
    {
        "id": "PCP-005",
        "pattern": "production ready",
        "reason": "Requires release-candidate evidence",
    },
    {
        "id": "PCP-006",
        "pattern": "field validated",
        "reason": "Requires FIELD_VALIDATED evidence records",
    },
    {
        "id": "PCP-007",
        "pattern": "independently reproduced",
        "reason": "Requires non-author reproduction evidence",
    },
    {
        "id": "PCP-008",
        "pattern": "peer reviewed",
        "reason": "Requires venue peer-review evidence",
    },
    {
        "id": "PCP-009",
        "pattern": "accessible to everyone",
        "reason": "Absolute accessibility claims prohibited without studies",
    },
    {
        "id": "PCP-010",
        "pattern": "scientifically complete",
        "reason": "Absolute completeness claims prohibited",
    },
    {
        "id": "PCP-011",
        "pattern": "all species ever discovered",
        "reason": "Charter explicitly forbids completeness claim",
    },
    {
        "id": "PCP-012",
        "pattern": "universal connectivity",
        "reason": "Implies coverage creation; not defensible",
    },
]


def is_transition_allowed(from_state: str, to_state: str) -> bool:
    if from_state == to_state:
        return True
    if from_state not in EXTENDED_STATES or to_state not in EXTENDED_STATES:
        return False
    return to_state in ALLOWED_TRANSITIONS.get(from_state, set())


def build_claim_taxonomy() -> dict[str, Any]:
    return {
        "schema_version": "1.0.0",
        "base_states": BASE_STATES,
        "extended_states": EXTENDED_STATES,
        "allowed_transitions": {k: sorted(v) for k, v in ALLOWED_TRANSITIONS.items()},
        "implied_falsehoods": IMPLIED_FALSEHOODS,
    }


def build_prohibited_patterns() -> dict[str, Any]:
    return {
        "schema_version": "1.0.0",
        "patterns": PROHIBITED_PATTERNS,
        "allow_when": [
            "accompanied by accepted evidence record",
            "clearly marked negation or non-claim language",
        ],
    }


def build_claims_from_requirements(requirements: list[dict[str, Any]]) -> list[dict[str, Any]]:
    claims = []
    for req in requirements:
        claims.append(
            {
                "claim_id": f"CLM-{req['id']}",
                "requirement_id": req["id"],
                "statement": req["title"],
                "claim_state": req["claim_state"],
                "implementation_state": req["implementation_state"],
                "validation_state": req["validation_state"],
                "certification_state": req["certification_state"],
                "evidence_ids": [],
                "blockers": list(req.get("blockers") or []),
                "notes": req.get("notes") or "",
            }
        )
    return claims
