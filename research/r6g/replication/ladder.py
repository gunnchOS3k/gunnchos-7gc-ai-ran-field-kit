"""Replication ladder R0–R9. Levels are earned per-candidate; never auto-inherited."""
from __future__ import annotations

LADDER = [
    {"level": "R0", "name": "SOURCE_DOCUMENTED", "auto_inherit": False},
    {"level": "R1", "name": "MODEL_IMPLEMENTED", "auto_inherit": False},
    {"level": "R2", "name": "SINGLE_SEED_DIGITAL_RUN", "auto_inherit": False},
    {"level": "R3", "name": "MULTI_SEED_DIGITAL_REPRODUCED", "auto_inherit": False},
    {"level": "R4", "name": "FALSIFICATION_AND_NEGATIVES_DOCUMENTED", "auto_inherit": False},
    {"level": "R5", "name": "ABLATIONS_COMPLETE", "auto_inherit": False},
    {"level": "R6", "name": "INDEPENDENT_VERIFIER_PASS", "auto_inherit": False},
    {"level": "R7", "name": "CLEAN_CHECKOUT_REPRODUCIBLE", "auto_inherit": False},
    {"level": "R8", "name": "EXTERNAL_REPRODUCTION", "auto_inherit": False},
    {"level": "R9", "name": "PHYSICAL_OR_PEER_REVIEWED", "auto_inherit": False},
]

# Parallel evidence taxonomy E0–E9 (surpass only at comparable level)
EVIDENCE_TAXONOMY = [
    "E0_DOCUMENTED",
    "E1_MODEL",
    "E2_DIGITAL_SIMULATION",
    "E3_EMULATION",
    "E4_SDR_LAB",
    "E5_HARDWARE_LAB",
    "E6_OTA_CONTROLLED",
    "E7_FIELD",
    "E8_EXTERNAL_INDEPENDENT",
    "E9_PEER_REVIEWED_OR_STANDARD_ACCEPTED",
]

CLAIM_STATES_ALLOWED = (
    "REGISTERED",
    "MODELED",
    "MODELED_ILLUSTRATIVE",
    "MODELED_SYNTHETIC_STUB",
    "MODELED_LOOKUP_TABLE",
    "MODELED_SCORING_HOOKS",
    "MODELED_CONTRACT_ONLY",
    "HARNESS_MAP_ONLY",
    "PROMISING_DIGITAL",
    "DIGITAL_IMPROVEMENT_CANDIDATE",
    "REPLICATION_INCOMPLETE",
    "NEGATIVE_RESULT_DOCUMENTED",
    "ADOPTION_A0_INTERNAL",
    "EXTERNAL_REPRODUCTION_PENDING",
    "PHYSICAL_REPRODUCTION_PENDING",
)

CLAIM_STATES_FORBIDDEN = (
    "BREAKTHROUGH_PROVEN",
    "STATE_OF_ART_SURPASSED",
    "IMPROVED_STATE_OF_ART",
    "PHYSICAL_VALIDATED",
    "PEER_REVIEWED_PASS",
    "STANDARDIZED_6G",
)


def max_earned_level(earned: list[str]) -> str:
    order = [x["level"] for x in LADDER]
    best = None
    for lvl in order:
        if lvl in earned:
            best = lvl
        else:
            break  # contiguous from R0 only if each earned; gaps stop climb
    return best or "NONE"


def contiguous_earned(flags: dict[str, bool]) -> list[str]:
    """Return contiguous prefix of levels that are True. Gap stops climb (no inherit)."""
    out = []
    for step in LADDER:
        lvl = step["level"]
        if flags.get(lvl):
            out.append(lvl)
        else:
            break
    return out
