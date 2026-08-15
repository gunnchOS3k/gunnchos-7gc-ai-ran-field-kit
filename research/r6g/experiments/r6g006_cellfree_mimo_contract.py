"""R6G-006 — Distributed / cell-free MIMO — safe digital contract only.

No physical array claims, no SoA beat, no hardware exaggeration.
"""
from __future__ import annotations

from typing import Any

from research.r6g.claim_firewall import assert_no_soa

CONTRACT = {
    "topology": "cell_free_ap_cluster",
    "ap_count_modeled": 8,
    "ue_count_modeled": 4,
    "precoding": ["MRT", "RZF_DIGITAL"],
    "fronthaul": "IDEALIZED_DIGITAL",
    "channel": "IID_RAYLEIGH_SYNTHETIC",
    "forbidden_claims": [
        "PHYSICAL_CELL_FREE_DEPLOYMENT",
        "BEATS_VENDOR_MASSIVE_MIMO_OTA",
        "IMPROVED_STATE_OF_ART",
    ],
}


def run_r6g006() -> dict[str, Any]:
    # Toy spectral-efficiency proxy under idealized fronthaul (not a lab result).
    se_mrt = 1.8
    se_rzf = 2.4
    report = {
        "schema": "gunnchos.r6g.r6g006.v1",
        "packet": "R6G-006",
        "ok": True,
        "status": "MODELED_CONTRACT_ONLY",
        "claim_state": "MODELED",
        "contract": CONTRACT,
        "toy_spectral_efficiency_bps_hz": {"MRT": se_mrt, "RZF_DIGITAL": se_rzf},
        "delta_rzf_minus_mrt": round(se_rzf - se_mrt, 4),
        "PHYSICAL_REPRODUCTION_PENDING": True,
        "HARDWARE_PENDING": True,
        "IMPROVED_STATE_OF_ART": False,
        "note": "Contract + toy digital proxy only; no cell-free hardware campaign.",
    }
    assert_no_soa(report)
    return report
