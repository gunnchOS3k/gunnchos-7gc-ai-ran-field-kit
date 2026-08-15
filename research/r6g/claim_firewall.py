"""Absolute claim firewall for R6G."""
IMPROVED_STATE_OF_ART = False
PERMITTED = (
    "DIGITAL_REPRODUCTION_MATCHED",
    "SIMULATION_IMPROVEMENT_OBSERVED",
    "HYPOTHESIS_SUPPORTED_DIGITALLY",
    "PHYSICAL_REPRODUCTION_PENDING",
    "COMPARABLE_EVIDENCE_PENDING",
)

def assert_no_soa(payload: dict) -> None:
    if payload.get("IMPROVED_STATE_OF_ART") is True:
        raise AssertionError("IMPROVED_STATE_OF_ART forbidden")
    if payload.get("6G_BREAKTHROUGH_PASS") is True:
        raise AssertionError("single 6G breakthrough PASS forbidden")
