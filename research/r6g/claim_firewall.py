"""Absolute claim firewall for R6G."""
IMPROVED_STATE_OF_ART = False
PERMITTED = (
    "DIGITAL_REPRODUCTION_MATCHED",
    "SIMULATION_IMPROVEMENT_OBSERVED",
    "HYPOTHESIS_SUPPORTED_DIGITALLY",
    "PHYSICAL_REPRODUCTION_PENDING",
    "COMPARABLE_EVIDENCE_PENDING",
    "PROMISING_DIGITAL",
    "DIGITAL_IMPROVEMENT_CANDIDATE",
    "FALSIFIABLE_NEGATIVE_CASES_DOCUMENTED",
)
FORBIDDEN_CLAIM_STATES = (
    "BREAKTHROUGH_PROVEN",
    "STATE_OF_ART_SURPASSED",
    "PHYSICAL_VALIDATED",
    "EXTERNAL_REPRODUCTION_COMPLETE",
    "PEER_REVIEWED_PASS",
    "STANDARDIZED_6G",
)

def assert_no_soa(payload: dict) -> None:
    if payload.get("IMPROVED_STATE_OF_ART") is True:
        raise AssertionError("IMPROVED_STATE_OF_ART forbidden")
    if payload.get("6G_BREAKTHROUGH_PASS") is True:
        raise AssertionError("single 6G breakthrough PASS forbidden")
    cs = payload.get("claim_state")
    if cs in FORBIDDEN_CLAIM_STATES:
        raise AssertionError(f"forbidden claim_state: {cs}")
