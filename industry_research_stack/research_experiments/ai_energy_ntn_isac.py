"""Research-ready experiments aligned to Brooklyn 6G signals — no hardware claims."""
from __future__ import annotations
from typing import Any, Dict

def ai_assisted_network_policy(metrics: Dict[str, float]) -> Dict[str, Any]:
    # Toy policy: prefer lower RTT + lower energy cost.
    score = -(metrics.get("rtt_ms", 100) / 100.0) - 0.5 * metrics.get("energy_cost", 1.0)
    return {"policy": "ai_assisted_stub", "score": score, "evidence_class": "SIMULATED"}

def energy_aware_selection(candidates: list[dict]) -> dict:
    return min(candidates, key=lambda c: c.get("energy_cost", 1.0))

def digital_twin_compare(sim_a: dict, sim_b: dict) -> Dict[str, Any]:
    return {
        "delta_snr_db": abs(sim_a.get("snr_db", 0) - sim_b.get("snr_db", 0)),
        "evidence_class": "SIMULATED",
        "claim": "TWIN_COMPARE_FIXTURE_ONLY",
    }

def ntn_terrestrial_handoff_sim(terrestrial_up: bool, ntn_abstracted_up: bool) -> Dict[str, Any]:
    selected = "terrestrial" if terrestrial_up else ("ntn_abstracted" if ntn_abstracted_up else "none")
    return {
        "selected": selected,
        "ntn_claim": "ABSTRACTED_ONLY",
        "real_ntn_hardware": False,
    }

def isac_readiness_contract() -> Dict[str, Any]:
    return {
        "lane": "RESEARCH",
        "product_requirement": False,
        "interfaces": ["sensing_metadata_v0", "comm_link_v0"],
        "hardware_claim": False,
    }
