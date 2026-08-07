#!/usr/bin/env python3
"""Validate G2-C6 shared product quality contract."""
from __future__ import annotations

import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("pyyaml required")
    raise SystemExit(2)

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "gate2/nonphysical/G2_C6_device_game_ux/product_quality_contract.yaml"
REQUIRED_DIMS = {
    "core_loop_completeness",
    "input_latency",
    "frame_pacing",
    "load_time",
    "crash_free_smoke",
    "input_classes",
    "same_input_menu_accessibility",
    "save_resume",
    "offline_behavior",
    "second_screen_docked",
    "audio_haptics",
    "accessibility",
    "telemetry",
    "performance_profiling",
    "device_role_adaptation",
    "failure_reconnect",
}


def main() -> int:
    data = yaml.safe_load(CONTRACT.read_text(encoding="utf-8"))
    errors = []
    if data.get("physical_execution_freeze") != "ACTIVE":
        errors.append("physical_execution_freeze must be ACTIVE")
    games = set(data.get("game_ids") or [])
    for g in (
        "beatlink-party",
        "archive-of-life-artifact-world",
        "pedestrian-pursuit",
        "anime-aggressors",
    ):
        if g not in games:
            errors.append(f"missing game_id {g}")
    dims = {d.get("id") for d in (data.get("dimensions") or [])}
    missing = REQUIRED_DIMS - dims
    if missing:
        errors.append(f"missing dimensions: {sorted(missing)}")
    if data.get("protected_asset_policy") != "no_copyrighted_music_or_anime_ip":
        errors.append("protected_asset_policy mismatch")
    if data.get("telemetry_namespace") != "gunnchos.game":
        errors.append("telemetry_namespace must be gunnchos.game")
    if data.get("grafana_backend") != "TEST_ONLY_STANDALONE":
        errors.append("grafana_backend must be TEST_ONLY_STANDALONE")
    if errors:
        print("PRODUCT_QUALITY_CONTRACT_FAIL")
        for e in errors:
            print("-", e)
        return 1
    print("PRODUCT_QUALITY_CONTRACT_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
