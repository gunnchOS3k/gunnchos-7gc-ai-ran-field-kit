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
            "ablation_seeds": [7, 11, 19],
            "robustness_seeds": [51, 52, 53],
        },
        "R6G-005": {
            "primary_seeds": [3, 5, 7, 11, 13, 17, 19, 23],
            "negative_stresses": ["in_distribution", "noisy_csi", "adversarial_csi"],
            "ablation_seeds": [3, 5, 7],
            "robustness_seeds": [41, 42, 43],
        },
        "R6G-009": {
            "primary_seeds": [2, 4, 6, 8, 10, 12, 14, 16],
            "negative_seeds": [90, 91],
            "ablation_seeds": [2, 4, 6],
            "robustness_seeds": [70, 71, 72],
        },
        "R6G-002": {
            "scenario_seeds": [1],
            "note": "Deterministic orchestrator; seed reserved for future stochastic channel",
        },
    },
    "amendments": [],
}
