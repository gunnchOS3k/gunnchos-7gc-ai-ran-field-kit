"""Useful Connectivity Score — GUNNCHOS_PROPOSED_RESEARCH_METRIC only.

Exact definition (pre-registered):

    UCS = (R * D * A * Q) / (P * C)

where all components are normalized dimensionless scores in (0, +∞), typically [0,1]
for R,D,A,Q and ≥ε for P,C (energy/cost penalties).

Pre-registered comparison weights / component meanings (locked before outcome reading):
  R — useful application throughput (normalized)
  D — effective distance / reach utility (normalized; not raw meters claim)
  A — availability
  Q — task / QoE success
  P — energy penalty (>0)
  C — cost penalty (>0)

This is NOT an ITU / 3GPP / standardized metric.
Do not use UCS alone to claim 146>145 Gbps or any physical SoA beat.
"""
from __future__ import annotations

from typing import Any

# Locked before comparing systems. Amendments require explicit log entry.
PREREGISTERED_WEIGHT_SCHEME = {
    "scheme_id": "UCS_V1_PRODUCT",
    "formula": "UCS = (R * D * A * Q) / (P * C)",
    "locked_at": "2026-08-15",
    "amendments": [],
    "component_definitions": {
        "R": "useful_application_throughput_norm",
        "D": "distance_or_reach_utility_norm",
        "A": "availability_norm",
        "Q": "task_qoe_success_norm",
        "P": "energy_penalty",
        "C": "cost_penalty",
    },
    "comparison_policy": "weights_not_tuned_after_seeing_which_system_wins",
    "classification": "GUNNCHOS_PROPOSED_METRIC",
    "research_metric_class": "GUNNCHOS_PROPOSED_RESEARCH_METRIC",
    "NOT_ITU_METRIC": True,
    "NOT_3GPP_METRIC": True,
    "NOT_STANDARDIZED_METRIC": True,
}


def useful_connectivity_score(*, R: float, D: float, A: float, Q: float, P: float, C: float) -> dict:
    if P <= 0 or C <= 0:
        raise ValueError("P and C must be > 0")
    score = (R * D * A * Q) / (P * C)
    return {
        "metric": "UsefulConnectivityScore",
        "classification": "GUNNCHOS_PROPOSED_METRIC",
        "research_metric_class": "GUNNCHOS_PROPOSED_RESEARCH_METRIC",
        "NOT_ITU_METRIC": True,
        "NOT_3GPP_METRIC": True,
        "NOT_STANDARDIZED_METRIC": True,
        "formula": PREREGISTERED_WEIGHT_SCHEME["formula"],
        "scheme_id": PREREGISTERED_WEIGHT_SCHEME["scheme_id"],
        "components": {"R": R, "D": D, "A": A, "Q": Q, "P": P, "C": C},
        "score": round(score, 6),
        "note": "Exploratory; use alongside standard metrics, never instead.",
    }


def sensitivity_analysis(base: dict[str, float], *, rel_delta: float = 0.1) -> dict[str, Any]:
    """One-at-a-time ±rel_delta sensitivity; predeclared, not outcome-tuned."""
    keys = ("R", "D", "A", "Q", "P", "C")
    base_score = useful_connectivity_score(**base)["score"]
    rows = []
    for k in keys:
        for sign, label in ((+1, "plus"), (-1, "minus")):
            comps = dict(base)
            factor = 1.0 + sign * rel_delta
            comps[k] = max(1e-6, comps[k] * factor)
            if k in ("P", "C"):
                comps[k] = max(1e-6, comps[k])
            s = useful_connectivity_score(**comps)["score"]
            rows.append({
                "component": k,
                "perturbation": label,
                "rel_delta": rel_delta,
                "score": s,
                "delta_vs_base": round(s - base_score, 6),
            })
    return {
        "scheme_id": PREREGISTERED_WEIGHT_SCHEME["scheme_id"],
        "base": base,
        "base_score": base_score,
        "rows": rows,
        "note": "Descriptive sensitivity only; not a statistical significance claim.",
    }
