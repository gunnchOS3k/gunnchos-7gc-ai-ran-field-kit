"""Claim firewall for NVIDIA × Oulu external reproduction (C-PKT-002)."""
from __future__ import annotations

from typing import Any

# Hard false unless independently earned outside this packet.
ALWAYS_FALSE = (
    "IMPROVED_STATE_OF_ART",
    "PHYSICAL",
    "OTA",
    "6G_CERTIFIED",
    "CARRIER_ACCEPTED",
    "STANDARDIZED_6G",
    "EXTERNAL_REPRODUCTION_COMPLETE",
    "PEER_REVIEWED_PASS",
    "NVIDIA_AERIAL_VALIDATED",
    "AODT_VALIDATED",
    "PYAERIAL_VALIDATED",
)

# Intermediate tokens require matching evidence fields.
INTERMEDIATE_ALLOWED = (
    "SOURCE_VERIFIED",
    "REFERENCE_SPEC_INCOMPLETE",
    "MODEL_IMPLEMENTED",
    "DIGITAL_MODEL_EXECUTED",
    "BASELINE_MATCH_PENDING",
    "BASELINE_MATCHED_NUMERIC",
    "DIGITAL_REPRODUCTION_PASS",
    "PREPARATION_ONLY",
    "UNAVAILABLE_FAIL_CLOSED",
    "NEGATIVE_RESULT_DOCUMENTED",
)

FORBIDDEN_TRUE = (
    "IMPROVED_STATE_OF_ART",
    "STATE_OF_ART_SURPASSED",
    "BREAKTHROUGH_PROVEN",
    "PHYSICAL_VALIDATED",
    "6G_CERTIFIED",
    "CARRIER_ACCEPTED",
)


def enforce_firewall(payload: dict[str, Any]) -> dict[str, Any]:
    """Mutate a copy: force SoA/physical/cert/carrier false; reject forbidden trues."""
    out = dict(payload)
    for key in ALWAYS_FALSE:
        out[key] = False
    claims = dict(out.get("claims") or {})
    for key in ALWAYS_FALSE:
        claims[key] = False
    out["claims"] = claims
    for key in FORBIDDEN_TRUE:
        if out.get(key) is True or claims.get(key) is True:
            raise AssertionError(f"forbidden claim set true: {key}")
    token = out.get("classification") or out.get("ladder_token")
    if isinstance(token, str):
        if token not in INTERMEDIATE_ALLOWED and token not in (
            "SOURCE_DOCUMENTED",
            "REGISTERED",
        ):
            # Unknown tokens must not look like SoA
            if any(x in token.upper() for x in ("SOA", "STATE_OF_ART", "CERTIFIED", "CARRIER", "OTA")):
                raise AssertionError(f"forbidden ladder token: {token}")
    out["IMPROVED_STATE_OF_ART"] = False
    return out


def assert_no_soa(payload: dict[str, Any]) -> None:
    enforce_firewall(payload)
