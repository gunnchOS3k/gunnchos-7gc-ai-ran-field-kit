"""Operator checklist for Gate 1 physical workstreams."""

from __future__ import annotations

from typing import Any

CHECKS: dict[str, list[dict[str, Any]]] = {
    "boot": [
        {
            "check_id": "boot_identity",
            "description": "Capture device identity on representative boot hardware",
            "required_presence": "PRESENT_CONFIRMED",
            "capability_id": "representative_boot_hardware",
            "pass_rule": "device_id recorded from observed device; evidence_class=physical",
        },
        {
            "check_id": "boot_services",
            "description": "Record service health after boot",
            "required_presence": "PRESENT_CONFIRMED",
            "capability_id": "representative_boot_hardware",
            "pass_rule": "service health captured; no invented metrics",
        },
    ],
    "ring-auth": [
        {
            "check_id": "ring_present",
            "description": "Confirm ring prototype PRESENT_CONFIRMED",
            "required_presence": "PRESENT_CONFIRMED",
            "capability_id": "ring_prototype",
            "pass_rule": "operator observation of physical ring",
        },
        {
            "check_id": "ring_auth_frame",
            "description": "Capture authenticated anti-replay frame",
            "required_presence": "PRESENT_CONFIRMED",
            "capability_id": "ring_prototype",
            "pass_rule": "nonce + payload digest present",
        },
    ],
    "dock": [
        {
            "check_id": "dock_present",
            "description": "Confirm dock station PRESENT_CONFIRMED",
            "required_presence": "PRESENT_CONFIRMED",
            "capability_id": "dock_station",
            "pass_rule": "operator observation of dock",
        },
        {
            "check_id": "dock_continuity",
            "description": "Record power/display/session continuity",
            "required_presence": "PRESENT_CONFIRMED",
            "capability_id": "dock_station",
            "pass_rule": "continuity fields recorded from session",
        },
    ],
    "ai-runtime": [
        {
            "check_id": "ai_target_present",
            "description": "Confirm on-device AI target PRESENT_CONFIRMED",
            "required_presence": "PRESENT_CONFIRMED",
            "capability_id": "on_device_ai_runtime_target",
            "pass_rule": "target device observed",
        },
        {
            "check_id": "ai_local_only",
            "description": "Verify local_only mode and egress denied",
            "required_presence": "PRESENT_CONFIRMED",
            "capability_id": "on_device_ai_runtime_target",
            "pass_rule": "mode=local_only and network_egress=denied",
        },
    ],
    "games": [
        {
            "check_id": "game_target_present",
            "description": "Confirm game target device PRESENT_CONFIRMED",
            "required_presence": "PRESENT_CONFIRMED",
            "capability_id": "game_target_device",
            "pass_rule": "target device observed",
        },
        {
            "check_id": "game_core_loop",
            "description": "Complete one core loop per required game",
            "required_presence": "PRESENT_CONFIRMED",
            "capability_id": "game_target_device",
            "pass_rule": "steps_completed recorded for each game",
        },
    ],
}


def plan_from_inventory(inventory: dict[str, Any]) -> dict[str, Any]:
    caps = {c["label"]: c for c in inventory.get("gate1_capabilities") or []}
    workstreams = []
    for ws, checks in CHECKS.items():
        cap_id = checks[0]["capability_id"]
        cap = caps.get(cap_id) or {}
        presence = cap.get("presence", "MISSING_ASSUMED")
        runnable = presence == "PRESENT_CONFIRMED"
        workstreams.append(
            {
                "workstream": ws,
                "capability_id": cap_id,
                "presence": presence,
                "runnable": runnable,
                "blocker_class": None if runnable else cap.get("blocker_class", "REQUIRES_LOCAL_HARDWARE"),
                "checks": checks,
            }
        )
    return {
        "schema_version": "1.0.0",
        "collected_at_utc": inventory.get("collected_at_utc"),
        "workstreams": workstreams,
        "runnable_count": sum(1 for w in workstreams if w["runnable"]),
        "blocked_count": sum(1 for w in workstreams if not w["runnable"]),
        "note": "No workstream is runnable until capability presence is PRESENT_CONFIRMED.",
    }


def get_check(workstream: str, check_id: str) -> dict[str, Any] | None:
    for c in CHECKS.get(workstream) or []:
        if c["check_id"] == check_id:
            return c
    return None
