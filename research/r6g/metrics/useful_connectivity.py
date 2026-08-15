"""Useful Connectivity Score — GUNNCHOS_PROPOSED_METRIC only."""
from __future__ import annotations

def useful_connectivity_score(*, R: float, D: float, A: float, Q: float, P: float, C: float) -> dict:
    if P <= 0 or C <= 0:
        raise ValueError("P and C must be > 0")
    score = (R * D * A * Q) / (P * C)
    return {
        "metric": "UsefulConnectivityScore",
        "classification": "GUNNCHOS_PROPOSED_METRIC",
        "NOT_ITU_METRIC": True,
        "NOT_3GPP_METRIC": True,
        "NOT_STANDARDIZED_METRIC": True,
        "components": {"R": R, "D": D, "A": A, "Q": Q, "P": P, "C": C},
        "score": round(score, 6),
        "note": "Exploratory; use alongside standard metrics, never instead.",
    }
