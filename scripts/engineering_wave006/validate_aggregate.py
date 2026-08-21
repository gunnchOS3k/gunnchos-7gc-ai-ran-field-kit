#!/usr/bin/env python3
"""Validate Wave006 field-kit integrity-repair aggregate mirror (no baseline mutations)."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ABS_RE = re.compile(r"(/Users/|/home/|/mnt/|/tmp/|[A-Za-z]:\\\\)")

def main() -> int:
    agg_path = ROOT / "artifacts/engineering_wave006/WAVE006_AGGREGATE.json"
    repair_path = ROOT / "artifacts/engineering_wave006/WAVE006_INTEGRITY_REPAIR_AGGREGATE.json"
    mirror = ROOT / "artifacts/engineering_wave006/device_os_mirror"
    agg = json.loads(agg_path.read_text())
    repair = json.loads(repair_path.read_text()) if repair_path.exists() else agg
    assert agg["BASELINE_COUNTS_UPDATED"] is False
    assert agg["DO_NOT_UPDATE_BASELINE_COUNTS"] is True
    assert agg.get("DO_NOT_MERGE_UNTIL_WAVE006_INTEGRITY_REPAIR_ACCEPTED") is True or agg.get("DO_NOT_MERGE_UNTIL_WAVE006_DEPENDENCY_PRS_ACCEPTED") is True
    assert repair.get("DO_NOT_MERGE_UNTIL_WAVE006_INTEGRITY_REPAIR_ACCEPTED") is True
    assert agg["OS_PLATFORM_020_UNTOUCHED"] is True
    assert agg["UNCONDITIONAL_TRUE_CLASSIFIERS"] == 0
    assert agg["UNCONDITIONAL_TRUE_CLASSIFIERS_COMPUTED"] is True
    assert agg["COMPLETE_GATE_REQUIRES_10_OF_10"] is True
    assert agg["target_requirements"] == 10
    assert len(agg["requirement_ids"]) == 10
    assert repair.get("historical_device_os_pr") == 129
    assert repair.get("historical_field_kit_pr") == 104
    assert repair.get("authoritative_repair_device_os_pr") == 130
    assert repair.get("BASELINE_COUNTS_UPDATED") is False
    wave = json.loads((mirror / "WAVE006_RESULT.json").read_text())
    assert wave["wave006_ok"] is True
    assert wave["summary"]["validated"] == 10
    assert wave.get("status") == "PASS"
    assert wave.get("PARTIAL") is False
    claims = json.loads((mirror / "CLAIM_BOUNDARIES.json").read_text())
    assert all(v is False for v in claims.values())
    behavioral = json.loads((mirror / "BEHAVIORAL_NEGATIVE_CONTROL_RESULT.json").read_text())
    assert behavioral.get("BEHAVIORAL_NEGATIVE_CONTROLS_PASS") is True
    for path in list(mirror.glob("*.json")) + [agg_path, repair_path]:
        if not path.exists():
            continue
        blob = path.read_text(encoding="utf-8")
        if ABS_RE.search(blob):
            raise SystemExit(f"absolute path in {path.name}")
    print("wave006 integrity-repair aggregate validation PASS")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
