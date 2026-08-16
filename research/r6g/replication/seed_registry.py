"""Pre-registered seeds for multi-seed digital replication (fixed before analysis)."""
from __future__ import annotations

# Seeds locked before reading outcomes. Do not cherry-pick post-hoc.
SEED_REGISTRY = {
    "schema": "gunnchos.r6g.seed_registry.v1",
    "preregistered": True,
    "note": "Seeds fixed for replication; adding seeds requires amendment log.",
    "candidates": {
        "R6G-003": {
            "primary_seeds": [7, 11, 19, 23, 29, 31, 37, 41],
            "negative_seeds": [101, 202, 303, 404],
            "ablation_seeds": [7, 11, 19, 23],
            "robustness_seeds": [51, 52, 53, 54, 55],
        },
        "R6G-005": {
            "primary_seeds": [3, 5, 7, 11, 13, 17, 19, 23],
            "negative_stresses": ["in_distribution", "noisy_csi", "adversarial_csi"],
            "ablation_seeds": [3, 5, 7, 11],
            "robustness_seeds": [41, 42, 43, 44, 45],
        },
        "R6G-009": {
            "primary_seeds": [2, 4, 6, 8, 10, 12, 14, 16],
            "negative_seeds": [90, 91],
            "ablation_seeds": [2, 4, 6, 8],
            "robustness_seeds": [70, 71, 72, 73, 74],
        },
        "R6G-006": {
            "primary_seeds": [7, 11, 13, 17, 19, 23, 29, 31],
            "negative_stresses": ["fronthaul_quantize", "ap_dropout", "pilot_contamination"],
            "ablation_seeds": [7, 11, 13],
            "robustness_seeds": [61, 62, 63],
        },
        "R6G-007": {
            "primary_seeds": [5, 9, 11, 15, 21, 25, 27, 33],
            "negative_stresses": ["phase_quant_2bit", "element_failure", "mobility_mismatch"],
            "ablation_seeds": [5, 9, 11],
            "robustness_seeds": [81, 82, 83],
        },
        "R6G-011": {
            "harness_seeds": [1, 2, 3],
            "note": "Harness is deterministic over TPR JSON; seeds reserved for future stochastic observables",
        },
        "R6G-002": {
            "scenario_seeds": [1],
            "note": "Deterministic orchestrator; seed reserved for future stochastic channel",
        },
    },
    "amendments": [
        {
            "id": "AMD-STREAM-C-PKT-001",
            "as_of": "2026-08-16",
            "change": (
                "Preregister R6G-006/007 multi-seed + ablation/robustness sets; "
                "extend 003/005/009 ablation+robustness seeds; reserve 011 harness seeds. "
                "No post-hoc cherry-pick of outcomes."
            ),
        }
    ],
}
