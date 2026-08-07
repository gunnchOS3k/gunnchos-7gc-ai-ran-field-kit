#!/usr/bin/env python3
"""Validate G2-C6 product quality contract presence and engine-neutral dimensions."""
from __future__ import annotations

import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "gate2/nonphysical/G2_C6_device_game_ux/contract/product_quality_contract.yaml"
REQUIRED = {
    "core_loop_completeness",
    "input_latency",
    "frame_pacing",
    "load_time",
    "crash_free_smoke",
    "controller_touch_keyboard_ring_input",
    "same_input_menu_accessibility",
    "save_resume",
    "offline_behavior",
    "second_screen_docked_behavior",
    "audio_haptics",
    "accessibility",
    "telemetry",
    "performance_profiling",
    "device_role_adaptation",
    "failure_reconnect",
}


def main() -> int:
    data = yaml.safe_load(CONTRACT.read_text())
    dims = set(data.get("dimensions", []))
    missing = sorted(REQUIRED - dims)
    if missing:
        print("PRODUCT_QUALITY_CONTRACT_FAIL", missing)
        return 1
    if not data.get("yaml_profiles_alone_insufficient"):
        print("PRODUCT_QUALITY_CONTRACT_FAIL: must mark yaml profiles insufficient")
        return 1
    if not data.get("instrumentation_required"):
        print("PRODUCT_QUALITY_CONTRACT_FAIL: instrumentation_required must be true")
        return 1
    print("PRODUCT_QUALITY_CONTRACT_PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
