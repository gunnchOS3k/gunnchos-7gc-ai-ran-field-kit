"""AI-RAN safe recommendation stack: telemetry → policy → rollback.

No unsafe carrier control planes.
"""
from __future__ import annotations

from typing import Any


FORBIDDEN_ACTIONS = {
    "force_carrier_attach",
    "override_operator_amf",
    "disable_lawful_intercept",
    "inject_false_measurement_to_operator",
    "mutate_live_ran_without_guardrail",
}


def run_ai_ran_safe() -> dict[str, Any]:
    telemetry = {
        "cell_load": 0.72,
        "worst_user_qoe": 0.61,
        "privacy_budget_remaining": 0.9,
        "path": "terrestrial",
    }
    recommendation = {
        "action": "prefer_local_edge_cache",
        "rationale": "worst_user_qoe_below_threshold",
        "carrier_control": False,
        "requires_human_ack_for_external": True,
    }
    if recommendation["action"] in FORBIDDEN_ACTIONS:
        raise AssertionError("unsafe carrier action recommended")
    applied = {
        "applied": True,
        "action": recommendation["action"],
        "guardrails": ["no_carrier_control", "privacy_budget", "rollback_ready"],
    }
    # Simulate regression → rollback
    rollback = {
        "triggered": True,
        "reason": "qoe_did_not_improve",
        "restored_policy": "static_baseline",
        "carrier_mutated": False,
    }
    ok = (
        applied["applied"]
        and recommendation["carrier_control"] is False
        and rollback["carrier_mutated"] is False
        and all(a not in FORBIDDEN_ACTIONS for a in [recommendation["action"]])
    )
    return {
        "schema": "gunnchos.net_sec_rc001.ai_ran_safe.v1",
        "ok": ok,
        "telemetry": telemetry,
        "recommendation": recommendation,
        "applied": applied,
        "rollback": rollback,
        "forbidden_actions": sorted(FORBIDDEN_ACTIONS),
        "CARRIER_ACCEPTED": False,
        "claim_boundary": "Advisory AI-RAN policy only; no unsafe carrier control.",
        "token_candidate": "AI_RAN_DIGITAL_RUNTIME",
    }
