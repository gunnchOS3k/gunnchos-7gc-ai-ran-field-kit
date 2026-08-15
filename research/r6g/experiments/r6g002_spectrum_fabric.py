"""R6G-002 — Hybrid spectrum fabric digital baseline."""
from __future__ import annotations
from typing import Any
from research.r6g.claim_firewall import assert_no_soa
from research.r6g.metrics.useful_connectivity import useful_connectivity_score

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


def decide(task: str, blockage: bool, weather_bad: bool, battery_low: bool) -> dict[str, Any]:
    if task == "offline_lesson" or battery_low:
        return {"decision": "local_only", "mode": "defer_or_semantic_sync"}
    if blockage and weather_bad:
        return {"decision": "multi_connectivity", "bearers": ["sub6_terrestrial", "LEO_NTN"], "fallback": "semantic_sync"}
    if weather_bad:
        return {"decision": "single_bearer", "bearers": ["FR3"], "avoid": ["FSO_OWC"]}
    if task == "bulk_backhaul":
        return {"decision": "single_bearer", "bearers": ["FSO_OWC"], "fallback": "sub_THz"}
    return {"decision": "multi_connectivity", "bearers": ["sub6_terrestrial", "FR3"], "fallback": "LEO_NTN"}


def run_r6g002() -> dict[str, Any]:
    decisions = {
        "nominal": decide("interactive", False, False, False),
        "blockage_weather": decide("interactive", True, True, False),
        "battery_low": decide("offline_lesson", False, False, True),
        "backhaul": decide("bulk_backhaul", False, False, False),
    }
    # Mark all non-sub6/local as HARDWARE_PENDING for physical
    hw = {k: {**v, "HARDWARE_PENDING": k not in {"sub6_terrestrial", "local_only", "LEO_NTN"}} for k, v in BEARERS.items()}
    ucs_peak = useful_connectivity_score(R=0.95, D=0.3, A=0.4, Q=0.5, P=2.0, C=2.5)
    ucs_useful = useful_connectivity_score(R=0.55, D=0.8, A=0.9, Q=0.85, P=1.0, C=1.0)
    report = {
        "schema": "gunnchos.r6g.r6g002.v1",
        "packet": "R6G-002",
        "ok": True,
        "status": "DIGITALLY_EXECUTED",
        "bearers": hw,
        "decisions": decisions,
        "useful_connectivity_comparison": {
            "peaky_link": ucs_peak,
            "useful_link": ucs_useful,
            "observation": "useful_link score higher despite lower peak R — exploratory only",
        },
        "IMPROVED_STATE_OF_ART": False,
        "PHYSICAL_REPRODUCTION_PENDING": True,
        "RM520N_GL_NTN": False,
        "RM520N_GL_5GA": False,
    }
    assert_no_soa(report)
    return report
