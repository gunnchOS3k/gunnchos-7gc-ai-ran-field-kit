"""R6G-002 — Hybrid spectrum fabric digital baseline."""
from __future__ import annotations
from typing import Any
from research.r6g.claim_firewall import assert_no_soa
from research.r6g.metrics.useful_connectivity import (
    PREREGISTERED_WEIGHT_SCHEME,
    sensitivity_analysis,
    useful_connectivity_score,
)

BEARERS = {
    "sub6_terrestrial": {"status": "SIMULATED", "latency_ms": 20, "rate_mbps": 200},
    "FR3": {"status": "MODELED", "latency_ms": 18, "rate_mbps": 800},
    "mmWave": {"status": "MODELED", "latency_ms": 15, "rate_mbps": 2000},
    "sub_THz": {"status": "MODELED", "latency_ms": 12, "rate_mbps": 10000},
    "THz": {"status": "MODELED", "latency_ms": 10, "rate_mbps": 50000},
    "FSO_OWC": {"status": "MODELED", "latency_ms": 5, "rate_mbps": 20000},
    "LEO_NTN": {"status": "SIMULATED", "latency_ms": 45, "rate_mbps": 5},
    "local_only": {"status": "SIMULATED", "latency_ms": 1, "rate_mbps": 1000},
}


def decide(
    task: str,
    *,
    blockage: bool = False,
    weather_bad: bool = False,
    battery_low: bool = False,
    terrestrial_up: bool = True,
    thz_available: bool = False,
    optical_los: bool = False,
) -> dict[str, Any]:
    if task == "offline_lesson" or battery_low or not terrestrial_up and task == "local_first":
        return {"decision": "local_only", "mode": "defer_or_semantic_sync", "scenario": "offline_or_local_first"}
    if not terrestrial_up:
        return {"decision": "single_bearer", "bearers": ["LEO_NTN"], "fallback": "semantic_sync", "scenario": "terrestrial_unavailable_ntn"}
    if thz_available and task == "high_volume_sync":
        return {"decision": "single_bearer", "bearers": ["THz"], "fallback": "FR3", "scenario": "thz_available"}
    if blockage and (thz_available or weather_bad):
        return {"decision": "multi_connectivity", "bearers": ["FR3", "mmWave"], "fallback": "sub6_terrestrial", "scenario": "thz_blocked_fr3_mmwave"}
    if optical_los and task == "bulk_backhaul":
        return {"decision": "single_bearer", "bearers": ["FSO_OWC"], "fallback": "sub_THz", "scenario": "optical_los_fso"}
    if blockage and weather_bad:
        return {"decision": "multi_connectivity", "bearers": ["sub6_terrestrial", "LEO_NTN"], "fallback": "semantic_sync"}
    if weather_bad:
        return {"decision": "single_bearer", "bearers": ["FR3"], "avoid": ["FSO_OWC"]}
    if task == "bulk_backhaul":
        return {"decision": "single_bearer", "bearers": ["FSO_OWC"], "fallback": "sub_THz"}
    return {"decision": "multi_connectivity", "bearers": ["sub6_terrestrial", "FR3"], "fallback": "LEO_NTN"}


# Continuum order (low → high peak rate; not a standards ranking).
BEARER_CONTINUUM = (
    "local_only",
    "LEO_NTN",
    "sub6_terrestrial",
    "FR3",
    "mmWave",
    "sub_THz",
    "FSO_OWC",
    "THz",
)

POLICIES = (
    "peak_rate_first",
    "availability_first",
    "energy_first",
    "local_first",
    "ucs_predeclared",
)


def _policy_choice(policy: str, *, blockage: bool, weather_bad: bool, terrestrial_up: bool) -> dict[str, Any]:
    if policy == "local_first" or not terrestrial_up:
        return {"policy": policy, "bearers": ["local_only"], "fallback": "LEO_NTN"}
    if policy == "peak_rate_first":
        return {"policy": policy, "bearers": ["THz"] if not blockage else ["mmWave"], "fallback": "FR3"}
    if policy == "availability_first":
        return {
            "policy": policy,
            "bearers": ["sub6_terrestrial", "LEO_NTN"] if weather_bad or blockage else ["sub6_terrestrial", "FR3"],
            "fallback": "semantic_sync",
        }
    if policy == "energy_first":
        return {"policy": policy, "bearers": ["sub6_terrestrial"], "avoid": ["THz", "FSO_OWC"]}
    # ucs_predeclared — prefer useful connectivity components, not peak R
    return {"policy": policy, "bearers": ["FR3", "sub6_terrestrial"], "fallback": "LEO_NTN", "metric": "UCS"}


def run_r6g002() -> dict[str, Any]:
    decisions = {
        "nominal": decide("interactive"),
        "thz_available": decide("high_volume_sync", thz_available=True),
        "thz_blocked": decide("high_volume_sync", thz_available=True, blockage=True, weather_bad=True),
        "terrestrial_unavailable_ntn": decide("interactive", terrestrial_up=False),
        "optical_los_fso": decide("bulk_backhaul", optical_los=True),
        "offline_local_first": decide("local_first", terrestrial_up=False, battery_low=True),
        "blockage_weather": decide("interactive", blockage=True, weather_bad=True),
        "battery_low": decide("offline_lesson", battery_low=True),
        "backhaul": decide("bulk_backhaul"),
    }
    policy_comparisons = {
        p: _policy_choice(p, blockage=True, weather_bad=True, terrestrial_up=True)
        for p in POLICIES
    }
    # Mark all non-sub6/local as HARDWARE_PENDING for physical
    hw = {
        k: {
            **v,
            "HARDWARE_PENDING": k not in {"sub6_terrestrial", "local_only", "LEO_NTN"},
            "continuum_index": BEARER_CONTINUUM.index(k) if k in BEARER_CONTINUUM else -1,
        }
        for k, v in BEARERS.items()
    }
    peak_comps = {"R": 0.95, "D": 0.3, "A": 0.4, "Q": 0.5, "P": 2.0, "C": 2.5}
    useful_comps = {"R": 0.55, "D": 0.8, "A": 0.9, "Q": 0.85, "P": 1.0, "C": 1.0}
    ucs_peak = useful_connectivity_score(**peak_comps)
    ucs_useful = useful_connectivity_score(**useful_comps)
    report = {
        "schema": "gunnchos.r6g.r6g002.v1",
        "packet": "R6G-002",
        "ok": True,
        "status": "DIGITALLY_EXECUTED",
        "bearer_continuum": list(BEARER_CONTINUUM),
        "bearers": hw,
        "decisions": decisions,
        "policy_comparisons": policy_comparisons,
        "useful_connectivity_comparison": {
            "metric_scheme": PREREGISTERED_WEIGHT_SCHEME,
            "research_metric_class": "GUNNCHOS_PROPOSED_RESEARCH_METRIC",
            "peaky_link": ucs_peak,
            "useful_link": ucs_useful,
            "peak_vs_useful": "useful_link score higher despite lower peak R — exploratory only",
            "sensitivity_useful_link": sensitivity_analysis(useful_comps, rel_delta=0.1),
            "no_146_gt_145_claim": True,
        },
        "IMPROVED_STATE_OF_ART": False,
        "PHYSICAL_REPRODUCTION_PENDING": True,
        "RM520N_GL_NTN": False,
        "RM520N_GL_5GA": False,
    }
    assert_no_soa(report)
    return report
