"""Earnable and forbidden tokens for NET-SEC-6G-RC-001."""
from __future__ import annotations

from typing import Any

PRODUCT_WORDING = (
    "5G-Advanced and NTN-capable, IMT-2030-aligned, software-defined, "
    "and engineered for migration to standardized 6G."
)

# Keys that may become true only when corresponding digital runtime evidence exists.
EARNABLE_TOKENS = (
    "5GA_TERRESTRIAL_DIGITAL_RUNTIME",
    "NTN_SIMULATION_RUNTIME",
    "AI_RAN_DIGITAL_RUNTIME",
    "SERVICE_CONTINUITY_POLICY",
    "APP_QOS_QOE_DIGITAL",
    "HOSTILE_NETWORK_DIGITAL",
    "IMT2030_MAPPING_COMPLETE_CURRENT_PUBLIC_DRAFT",
    "IMT2030_EVAL_HARNESS_CURRENT_DRAFT",
    "REL20_REL21_MIGRATION_TRACKER",
)

FORBIDDEN_TOKENS = (
    "STANDARDIZED_6G",
    "6G_CERTIFIED",
    "CARRIER_ACCEPTED",
    "REAL_NTN_MODEM_VALIDATED",
    "GATE_8_PASS",
)

CLAIM_BOUNDARY = (
    "Digital / simulation / standards-mapping only. Quectel RM520N-GL is terrestrial "
    "Rel-16 NSA+SA Sub-6 — not NTN, not 6G. CARRIER EXTERNAL_PENDING. SM-DP+ EXTERNAL_PENDING. "
    "No unsafe carrier control. No global IMT2030_PASS."
)


def empty_token_table() -> dict[str, bool]:
    table = {k: False for k in EARNABLE_TOKENS}
    table.update({k: False for k in FORBIDDEN_TOKENS})
    return table


TOKEN_TABLE = empty_token_table()


def assert_forbidden_remain_false(tokens: dict[str, Any]) -> None:
    for key in FORBIDDEN_TOKENS:
        if tokens.get(key) is True:
            raise AssertionError(f"forbidden token flipped true: {key}")
