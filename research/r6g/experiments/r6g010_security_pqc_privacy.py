"""R6G-010 — Zero-trust / PQC / ISAC privacy scoring hooks (digital only).

Scoring hooks for research comparison — not a certification, not COMPLIANT_6G.
"""
from __future__ import annotations

from typing import Any

from research.r6g.claim_firewall import assert_no_soa

# Pre-registered weights (locked before scoring campaigns).
PREREGISTERED_SECURITY_WEIGHTS = {
    "scheme_id": "SEC_PRIV_V1",
    "locked_at": "2026-08-15",
    "weights": {
        "zero_trust_posture": 0.25,
        "pqc_readiness": 0.25,
        "sensing_privacy": 0.25,
        "key_lifecycle": 0.15,
        "auditability": 0.10,
    },
    "amendments": [],
    "classification": "GUNNCHOS_PROPOSED_RESEARCH_METRIC",
    "NOT_CERTIFICATION": True,
}


def _clamp01(x: float) -> float:
    return max(0.0, min(1.0, x))


def score_profile(components: dict[str, float]) -> dict[str, Any]:
    w = PREREGISTERED_SECURITY_WEIGHTS["weights"]
    total = 0.0
    detail = {}
    for k, wt in w.items():
        v = _clamp01(float(components.get(k, 0.0)))
        detail[k] = {"value": v, "weight": wt, "weighted": round(v * wt, 4)}
        total += v * wt
    privacy = detail["sensing_privacy"]["value"]
    privacy_floor_fail = privacy < 0.25
    return {
        "components": detail,
        "score": round(total, 4),
        "privacy_floor_fail": privacy_floor_fail,
        "scheme_id": PREREGISTERED_SECURITY_WEIGHTS["scheme_id"],
        "classification": "GUNNCHOS_PROPOSED_RESEARCH_METRIC",
        "NOT_CERTIFICATION": True,
    }


def run_r6g010() -> dict[str, Any]:
    profiles = {
        "baseline_rel16_terrestrial": score_profile({
            "zero_trust_posture": 0.45,
            "pqc_readiness": 0.20,
            "sensing_privacy": 0.40,
            "key_lifecycle": 0.50,
            "auditability": 0.55,
        }),
        "research_candidate_digital": score_profile({
            "zero_trust_posture": 0.70,
            "pqc_readiness": 0.55,
            "sensing_privacy": 0.65,
            "key_lifecycle": 0.60,
            "auditability": 0.70,
        }),
        "overclaim_trap": score_profile({
            "zero_trust_posture": 0.95,
            "pqc_readiness": 0.95,
            "sensing_privacy": 0.10,  # sensing privacy collapse
            "key_lifecycle": 0.90,
            "auditability": 0.90,
        }),
    }
    trap = profiles["overclaim_trap"]
    cand = profiles["research_candidate_digital"]
    # Falsification: high aggregate with collapsed privacy must fail the privacy floor gate
    trap_fails_floor = trap["privacy_floor_fail"] is True and cand["privacy_floor_fail"] is False
    report = {
        "schema": "gunnchos.r6g.r6g010.v1",
        "packet": "R6G-010",
        "ok": True,
        "status": "MODELED_SCORING_HOOKS",
        "claim_state": "MODELED_SCORING_HOOKS",
        "ladder_earned": ["R0", "R1"],
        "weight_scheme": PREREGISTERED_SECURITY_WEIGHTS,
        "profiles": profiles,
        "privacy_floor": 0.25,
        "falsification": {
            "overclaim_trap_scores_worse_when_privacy_collapses": trap_fails_floor,
            "note": "Illustrative privacy-floor gate; not a falsifiable security campaign",
            "ILLUSTRATIVE": True,
        },
        "hooks": {
            "score_profile": "research.r6g.experiments.r6g010_security_pqc_privacy.score_profile",
            "consumers": ["adoption packages", "WAIKE case study", "portfolio matrix"],
        },
        "SECURITY_PQC_PRIVACY_HOOKS_DIGITAL": False,
        "STANDARDIZED_6G": False,
        "COMPLIANT": False,
        "CERTIFIED": False,
        "PHYSICAL_REPRODUCTION_PENDING": True,
        "IMPROVED_STATE_OF_ART": False,
        "note": "Scoring hooks only — not DIGITALLY_EXECUTED evidence; not a certification.",
    }
    assert_no_soa(report)
    assert report["STANDARDIZED_6G"] is False
    assert report["COMPLIANT"] is False
    return report
