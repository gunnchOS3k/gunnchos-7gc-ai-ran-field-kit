"""R6G-007 — Adaptive RIS / intelligent environment — safe digital contract only.

No RIS purchase, no physical panel claims, no SoA exaggeration.
"""
from __future__ import annotations

from typing import Any

from research.r6g.claim_firewall import assert_no_soa

CONTRACT = {
    "elements_modeled": 64,
    "control": "PHASE_ONLY_DIGITAL",
    "channel": "SINGLE_BOUNCE_SYNTHETIC",
    "purchase_authorized": False,
    "forbidden_claims": [
        "PHYSICAL_RIS_VALIDATED",
        "PURCHASED_HARDWARE",
        "IMPROVED_STATE_OF_ART",
    ],
}


def run_r6g007() -> dict[str, Any]:
    passive_snr_db = 8.0
    adaptive_snr_db = 11.5
    report = {
        "schema": "gunnchos.r6g.r6g007.v1",
        "packet": "R6G-007",
        "ok": True,
        "status": "MODELED_CONTRACT_ONLY",
        "claim_state": "MODELED",
        "contract": CONTRACT,
        "toy_snr_db": {"passive_reflect": passive_snr_db, "adaptive_phase": adaptive_snr_db},
        "delta_db": round(adaptive_snr_db - passive_snr_db, 4),
        "PHYSICAL_REPRODUCTION_PENDING": True,
        "RIS_PURCHASE": False,
        "IMPROVED_STATE_OF_ART": False,
        "note": "Digital RIS contract only; no physical purchase this cycle.",
    }
    assert_no_soa(report)
    return report
