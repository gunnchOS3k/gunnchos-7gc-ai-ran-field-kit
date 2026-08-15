"""Earnable and forbidden tokens for NET-SEC-6G-RC-001."""
from __future__ import annotations

from typing import Any

# Architecture / migration intent — does NOT claim RM520N-GL hardware is 5GA or NTN.
PRODUCT_WORDING = (
    "Software-defined architecture engineered for 5G-Advanced and NTN-capable "
    "paths (NTN via simulation), IMT-2030-aligned, and engineered for migration "
    "to standardized 6G; Quectel RM520N-GL digital baseline is Rel-16 NSA+SA "
    "Sub-6 terrestrial only — not 5G-Advanced hardware and not NTN."
)

# Packet-level earnable tokens (5GA stays false until a real Rel-18+/5GA surface exists
# that is not the Rel-16 RM520N modem path).
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

# Honest supporting token for the Rel-16 RM520N digital surface (not 5GA).
SUPPORTING_TOKENS = (
    "5G_REL16_TERRESTRIAL_DIGITAL_RUNTIME",
    # R6G digital-only research tokens (never imply physical SoA improvement)
    "R6G_REGISTRY_COMPLETE",
    "MULTIMODAL_ISAC_DIGITAL_IMPROVEMENT",
    "AI_PHY_UNCERTAINTY_AWARE_DIGITAL",
    "PREDICTIVE_RADIO_DT_DIGITAL",
    "HYBRID_SPECTRUM_FABRIC_DIGITAL",
    "SEMANTIC_CONTINUITY_NTN_EDU_DIGITAL",
    "R6G_DIGITAL_REPLICATION_PASS",
    "R6G_MULTI_SEED_REPRODUCED",
    "R6G_FALSIFICATION_DOCUMENTED",
    "R6G_ABLATIONS_DOCUMENTED",
    "R6G_INDEPENDENT_VERIFIER_PASS",
)

FORBIDDEN_TOKENS = (
    "STANDARDIZED_6G",
    "6G_CERTIFIED",
    "CARRIER_ACCEPTED",
    "REAL_NTN_MODEM_VALIDATED",
    "GATE_8_PASS",
    "IMPROVED_STATE_OF_ART",
)

CLAIM_BOUNDARY = (
    "Digital / simulation / standards-mapping only. Quectel RM520N-GL is terrestrial "
    "Rel-16 NSA+SA Sub-6 — not 5G-Advanced hardware, not NTN, not 6G. "
    "CARRIER EXTERNAL_PENDING. SM-DP+ EXTERNAL_PENDING. "
    "No unsafe carrier control. No global IMT2030_PASS. "
    "5GA_TERRESTRIAL_DIGITAL_RUNTIME requires a Rel-18+/5GA digital surface distinct "
    "from the Rel-16 modem path."
)


def empty_token_table() -> dict[str, bool]:
    table = {k: False for k in EARNABLE_TOKENS}
    table.update({k: False for k in SUPPORTING_TOKENS})
    table.update({k: False for k in FORBIDDEN_TOKENS})
    return table


TOKEN_TABLE = empty_token_table()


def assert_forbidden_remain_false(tokens: dict[str, Any]) -> None:
    for key in FORBIDDEN_TOKENS:
        if tokens.get(key) is True:
            raise AssertionError(f"forbidden token flipped true: {key}")
