"""Useful Connectivity Score — GUNNCHOS_PROPOSED_RESEARCH_METRIC only.

Exact definition (pre-registered BEFORE evaluation):

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
Do not rewrite weights after seeing which policy wins.
"""
from __future__ import annotations

import hashlib
import json
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
    # Default multiplicative emphasis (applied after base UCS components are formed).
    # These are NOT tuned post-hoc to crown a policy.
    "default_component_weights": {
        "R": 1.0,
        "D": 1.0,
        "A": 1.0,
        "Q": 1.0,
        "P": 1.0,
        "C": 1.0,
    },
    "equal_component_weights": {
        "R": 1.0,
        "D": 1.0,
        "A": 1.0,
        "Q": 1.0,
        "P": 1.0,
        "C": 1.0,
    },
    # Task-specific permitted weight sets — declared before eval; not outcome-edited.
    "task_specific_permitted_weights": {
        "student": {"R": 0.8, "D": 1.0, "A": 1.3, "Q": 1.4, "P": 1.0, "C": 1.2},
        "gaming": {"R": 1.2, "D": 0.7, "A": 1.1, "Q": 1.5, "P": 1.0, "C": 0.9},
        "creator": {"R": 1.4, "D": 0.8, "A": 1.0, "Q": 1.2, "P": 1.1, "C": 1.0},
        "Ring": {"R": 1.0, "D": 1.1, "A": 1.2, "Q": 1.3, "P": 1.2, "C": 1.0},
        "rural_NTN": {"R": 0.7, "D": 1.5, "A": 1.4, "Q": 1.1, "P": 1.0, "C": 1.3},
        "ISAC": {"R": 1.0, "D": 1.2, "A": 1.1, "Q": 1.3, "P": 1.1, "C": 1.0},
    },
    "comparison_policy": "weights_not_tuned_after_seeing_which_system_wins",
    "classification": "GUNNCHOS_PROPOSED_METRIC",
    "research_metric_class": "GUNNCHOS_PROPOSED_RESEARCH_METRIC",
    "NOT_ITU_METRIC": True,
    "NOT_3GPP_METRIC": True,
    "NOT_STANDARDIZED_METRIC": True,
}


def preregistration_hash(scheme: dict[str, Any] | None = None) -> str:
    """SHA-256 of the locked scheme (canonical JSON). Store before reading outcomes."""
    payload = dict(scheme if scheme is not None else PREREGISTERED_WEIGHT_SCHEME)
    payload.pop("preregistration_hash", None)
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


# Computed once at import — frozen fingerprint of the pre-registered scheme.
PREREGISTRATION_HASH = preregistration_hash()
PREREGISTERED_WEIGHT_SCHEME = {
    **PREREGISTERED_WEIGHT_SCHEME,
    "preregistration_hash": PREREGISTRATION_HASH,
}


def useful_connectivity_score(
    *,
    R: float,
    D: float,
    A: float,
    Q: float,
    P: float,
    C: float,
    weights: dict[str, float] | None = None,
) -> dict:
    if P <= 0 or C <= 0:
        raise ValueError("P and C must be > 0")
    w = weights or PREREGISTERED_WEIGHT_SCHEME["default_component_weights"]
    # Weighted components: raise R,D,A,Q to weight; scale P,C by weight (penalties).
    Rw = R ** float(w.get("R", 1.0))
    Dw = D ** float(w.get("D", 1.0))
    Aw = A ** float(w.get("A", 1.0))
    Qw = Q ** float(w.get("Q", 1.0))
    Pw = max(1e-9, P * float(w.get("P", 1.0)))
    Cw = max(1e-9, C * float(w.get("C", 1.0)))
    score = (Rw * Dw * Aw * Qw) / (Pw * Cw)
    return {
        "metric": "UsefulConnectivityScore",
        "classification": "GUNNCHOS_PROPOSED_METRIC",
        "research_metric_class": "GUNNCHOS_PROPOSED_RESEARCH_METRIC",
        "NOT_ITU_METRIC": True,
        "NOT_3GPP_METRIC": True,
        "NOT_STANDARDIZED_METRIC": True,
        "formula": PREREGISTERED_WEIGHT_SCHEME["formula"],
        "scheme_id": PREREGISTERED_WEIGHT_SCHEME["scheme_id"],
        "preregistration_hash": PREREGISTRATION_HASH,
        "weights_applied": dict(w),
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
        "preregistration_hash": PREREGISTRATION_HASH,
        "base": base,
        "base_score": base_score,
        "rows": rows,
        "note": "Descriptive sensitivity only; not a statistical significance claim.",
    }


def weight_scheme_bundle(base: dict[str, float], *, task: str | None = None) -> dict[str, Any]:
    """Evaluate default / equal / task-specific weights on the same components."""
    default = useful_connectivity_score(**base)
    equal = useful_connectivity_score(
        **base, weights=PREREGISTERED_WEIGHT_SCHEME["equal_component_weights"]
    )
    task_row = None
    if task and task in PREREGISTERED_WEIGHT_SCHEME["task_specific_permitted_weights"]:
        tw = PREREGISTERED_WEIGHT_SCHEME["task_specific_permitted_weights"][task]
        task_row = useful_connectivity_score(**base, weights=tw)
    return {
        "preregistration_hash": PREREGISTRATION_HASH,
        "locked_at": PREREGISTERED_WEIGHT_SCHEME["locked_at"],
        "weights_rewritten_after_eval": False,
        "default": default,
        "equal_weights": equal,
        "task_specific": task_row,
        "sensitivity": sensitivity_analysis(base, rel_delta=0.1),
    }
