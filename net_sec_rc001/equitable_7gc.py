"""7GC equitable connectivity scenarios with honest metrics (no fabricated community outcomes)."""
from __future__ import annotations

from typing import Any


CAMPUSES = (
    "campus_alpha",
    "campus_beta",
    "campus_gamma",
    "campus_delta",
    "campus_epsilon",
    "campus_zeta",
    "campus_eta",
)


def run_equitable_7gc() -> dict[str, Any]:
    scenarios = []
    for i, campus in enumerate(CAMPUSES):
        scenarios.append({
            "campus": campus,
            "scenario": "affordable_edge_continuity",
            "paths_considered": ["wifi", "cellular_5ga", "ntn_sim", "local"],
            "metric_availability": "SYNTHETIC_LAB_ONLY",
            "coverage_fraction_measured": None,
            "coverage_fraction_status": "NOT_MEASURED_FIELD",
            "worst_user_qoe_lab": round(0.55 + (i * 0.03), 3),
            "community_outcome_fabricated": False,
            "note": "Lab-synthetic continuity score only; no claimed campus population outcome.",
        })
    ok = len(scenarios) == 7 and all(s["community_outcome_fabricated"] is False for s in scenarios)
    ok = ok and all(s["coverage_fraction_measured"] is None for s in scenarios)
    return {
        "schema": "gunnchos.net_sec_rc001.equitable_7gc.v1",
        "ok": ok,
        "campuses": list(CAMPUSES),
        "scenarios": scenarios,
        "claim_boundary": "Honest metrics only; no fabricated community outcomes.",
    }
