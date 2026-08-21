from __future__ import annotations

from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]

def test_aggregate_flags():
    agg = json.loads((ROOT / "artifacts/engineering_wave006/WAVE006_AGGREGATE.json").read_text())
    assert agg["BASELINE_COUNTS_UPDATED"] is False
    assert agg.get("DO_NOT_MERGE_UNTIL_WAVE006_INTEGRITY_REPAIR_ACCEPTED") is True
    assert agg["target_requirements"] == 10
    assert agg["OS_PLATFORM_020_UNTOUCHED"] is True

def test_integrity_repair_aggregate():
    repair = json.loads((ROOT / "artifacts/engineering_wave006/WAVE006_INTEGRITY_REPAIR_AGGREGATE.json").read_text())
    assert repair["historical_device_os_pr"] == 129
    assert repair["historical_field_kit_pr"] == 104
    assert repair["authoritative_repair_device_os_pr"] == 130
    assert repair["BASELINE_COUNTS_UPDATED"] is False
    assert repair["DO_NOT_MERGE_UNTIL_WAVE006_INTEGRITY_REPAIR_ACCEPTED"] is True

def test_mirror_wave006_ok():
    wave = json.loads((ROOT / "artifacts/engineering_wave006/device_os_mirror/WAVE006_RESULT.json").read_text())
    assert wave["wave006_ok"] is True
    assert wave["summary"]["validated"] == 10
    assert wave.get("status") == "PASS"
