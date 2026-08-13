#!/usr/bin/env python3
"""Compute USER_READY_DIGITAL_RELEASE_CANDIDATE as AND of child tokens.

Never accept a manual PASS. Child tokens may become true only from independent
accepted-main evidence recorded in the gate JSON. PHYSICAL / HUMAN_E6 /
SHIPPING stay outside the digital AND.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
GATE = ROOT / "USER_READY_RELEASE_CANDIDATE_GATE.json"

DIGITAL_AND_KEYS = [
    "STUDENT_DIGITAL_PICKUP_AND_USE_READY",
    "OFFICE_DIGITAL_PICKUP_AND_USE_READY",
    "TEACHER_DIGITAL_PICKUP_AND_USE_READY",
    "BUILDER_DIGITAL_PICKUP_AND_USE_READY",
    "CREATIVE_DIGITAL_PICKUP_AND_USE_READY",
    "FOUR_GAME_FULL_PLAYTHROUGH_RC",
    "FOUR_GAME_ACHIEVEMENT_SYSTEM_RC",
    "FOUR_GAME_AI_HEURISTIC_POLISH_RC",
    "WAIKE_FULL_CURRICULUM_DIGITAL_RC",
    "WAIKE_ASSESSMENT_SYSTEM_DIGITAL_RC",
    "WAIKE_TEACHER_WORKFLOW_DIGITAL_RC",
    "GUNNCHAI_MARKET_TASK_COVERAGE_RC",
    "GUNNCHAI_STUDENT_COMPANION_RC",
    "GUNNCHAI_OFFICE_COMPANION_RC",
    "GUNNCHAI_TEACHER_ASSISTANT_RC",
    "GUNNCHAI_BUILDER_ASSISTANT_RC",
    "GUNNCHAI_CREATIVE_ASSISTANT_RC",
    "GUNNCHDEVICE_LAB_ALL_DEVICE_PROFILES_RC",
    "GUNNCHDEVICE_LAB_FULL_ECOSYSTEM_RC",
    "HARDWARE_DIGITAL_DESIGN_RC",
    "FIRMWARE_DIGITAL_RC",
    "NETWORKING_SECURITY_5GA_NTN_6G_MIGRATION_DIGITAL_RC",
]


def compute(doc: dict) -> tuple[bool, list[str]]:
    tokens = doc["digital_tokens"]
    missing = [k for k in DIGITAL_AND_KEYS if k not in tokens]
    if missing:
        raise SystemExit(f"gate missing digital tokens: {missing}")
    false_keys = [k for k in DIGITAL_AND_KEYS if tokens[k] is not True]
    return (len(false_keys) == 0, false_keys)


def main() -> int:
    doc = json.loads(GATE.read_text(encoding="utf-8"))
    if doc.get("manual_override_forbidden") is not True:
        print("FAIL: manual_override_forbidden must be true")
        return 1
    computed, false_keys = compute(doc)
    recorded = doc.get("USER_READY_DIGITAL_RELEASE_CANDIDATE")
    if recorded is True and not computed:
        print("FAIL: USER_READY_DIGITAL_RELEASE_CANDIDATE was manually set PASS")
        print("false_children:", false_keys)
        return 1
    doc["USER_READY_DIGITAL_RELEASE_CANDIDATE"] = computed
    doc["computed_and"] = {
        "operator": "AND",
        "inputs": DIGITAL_AND_KEYS,
        "false_children": false_keys,
        "true_children": [k for k in DIGITAL_AND_KEYS if k not in false_keys],
    }
    # Separate non-digital tokens: never inferred from the digital AND.
    separate = doc.setdefault("separate_non_digital_tokens", {})
    for key in ("PHYSICAL_PICKUP_AND_USE_READY", "HUMAN_E6", "SHIPPING_PRODUCT"):
        if separate.get(key) is not True:
            separate[key] = False
        elif not separate.get(f"{key}_accepted_main_evidence"):
            print(f"FAIL: {key}=true without accepted_main_evidence")
            return 1
    GATE.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("USER_READY_DIGITAL_RELEASE_CANDIDATE=" + ("true" if computed else "false"))
    print("false_children_count=" + str(len(false_keys)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
