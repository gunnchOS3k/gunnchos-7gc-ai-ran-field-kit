#!/usr/bin/env python3
"""Validate Wave009 field-kit aggregate: OS-PLATFORM-020 sandbox evidence mirror."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AGG = ROOT / "artifacts/engineering_wave009/WAVE009_AGGREGATE.json"
MIRROR = ROOT / "artifacts/engineering_wave009/device_os_mirror"


def main() -> int:
    agg = json.loads(AGG.read_text(encoding="utf-8"))
    wave = json.loads((MIRROR / "WAVE009_RESULT.json").read_text(encoding="utf-8"))
    suite = json.loads((MIRROR / "SANDBOX_ENFORCEMENT_RESULT.json").read_text(encoding="utf-8"))
    beh = json.loads((MIRROR / "BEHAVIORAL_NEGATIVE_CONTROL_RESULT.json").read_text(encoding="utf-8"))

    errors: list[str] = []
    if agg.get("status") != "PASS":
        errors.append("aggregate_status_not_pass")
    if agg.get("TARGET_REQUIREMENTS") != 1:
        errors.append("target_requirements_not_1")
    if agg.get("requirement_ids") != ["OS-PLATFORM-020"]:
        errors.append("unexpected_requirement_ids")
    if agg.get("OS_PLATFORM_020") != "IMPLEMENTED_AND_VALIDATED":
        errors.append("os020_not_validated")
    if agg.get("BASELINE_COUNTS_UPDATED") is not False:
        errors.append("baseline_counts_updated")
    if agg.get("DIGITAL_VALIDATION_QUEUE_UPDATED") is not False:
        errors.append("validation_queue_updated")
    if agg.get("OS_PLATFORM_020_BASELINE_STATE_UNCHANGED") != "DIGITAL_VALIDATION_OPEN":
        errors.append("baseline_state_changed")
    if wave.get("ENGINEERING_WAVE_009") != "PASS":
        errors.append("mirror_wave_not_pass")
    if suite.get("SANDBOX_BACKEND") != "bubblewrap":
        errors.append("backend_not_bubblewrap")
    if suite.get("KERNEL_SANDBOX") is not True:
        errors.append("kernel_sandbox_false")
    if suite.get("PLAIN_SUBPROCESS_COUNTS_AS_SANDBOX") is not False:
        errors.append("plain_subprocess_claim")
    if suite.get("SANDBOX_EXECUTED_AS_ROOT") is not False:
        errors.append("executed_as_root")
    if suite.get("BWRAP_INVOKED_WITH_SUDO") is not False:
        errors.append("bwrap_with_sudo")
    if beh.get("BEHAVIORAL_NEGATIVE_CONTROL_COUNT", 0) < 12:
        errors.append("insufficient_sabotage_controls")
    if beh.get("BEHAVIORAL_NEGATIVE_CONTROLS_PASS") is not True:
        errors.append("sabotage_controls_failed")

    # Ensure no Baseline v2 files are part of this aggregate commit expectation.
    baseline_touch = list((ROOT / "program/digital_ecosystem_baseline_v2").glob("*"))
    _ = baseline_touch  # present on main; aggregate must not modify them (checked by git in CI)

    if errors:
        print({"ok": False, "errors": errors})
        return 1
    print({"ok": True, "OS_PLATFORM_020": "IMPLEMENTED_AND_VALIDATED", "BASELINE_COUNTS_UPDATED": False})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
