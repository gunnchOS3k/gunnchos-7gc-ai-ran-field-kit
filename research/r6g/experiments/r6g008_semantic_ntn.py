"""R6G-008 — NTN semantic service continuity for WAIKE / gunnchAI.

Wraps the digital semantic continuity matrix; never claims real learning outcomes.
"""
from __future__ import annotations

from typing import Any

from research.r6g.claim_firewall import assert_no_soa
from research.r6g.experiments.semantic_continuity_ntn_education import run_semantic_continuity


def run_r6g008() -> dict[str, Any]:
    base = run_semantic_continuity()
    # Rank modes by long_outage recovery (digital only).
    long = {m: base["matrix"][m]["long_outage"] for m in base["modes"]}
    ranked = sorted(
        long.items(),
        key=lambda kv: (kv[1]["recovery_after_reconnect_s"], kv[1]["bytes_transferred_norm"]),
    )
    best = ranked[0][0]
    worst = ranked[-1][0]
    report = {
        "schema": "gunnchos.r6g.r6g008.v1",
        "packet": "R6G-008",
        "ok": True,
        "status": "DIGITALLY_EXECUTED",
        "claim_state": "MODELED",
        "waike_transfer": {
            "case_study": "research/r6g/waike/case_studies/R6G-008.md",
            "counts_as_scientific_validation": False,
            "gunnchai_affordance": "explain continuity modes; flag overclaim",
        },
        "semantic_continuity": base,
        "digital_rank_long_outage_best_to_worst": [m for m, _ in ranked],
        "best_mode_under_long_outage": best,
        "worst_mode_under_long_outage": worst,
        "real_education_outcome_claimed": False,
        "guaranteed_learning_outcomes": False,
        "human_study": "EXTERNAL_PENDING",
        "PHYSICAL_REPRODUCTION_PENDING": True,
        "IMPROVED_STATE_OF_ART": False,
        "note": "NTN semantic continuity digital research only — no guaranteed learning outcomes.",
    }
    assert_no_soa(report)
    assert report["real_education_outcome_claimed"] is False
    assert report["guaranteed_learning_outcomes"] is False
    return report
