#!/usr/bin/env python3
"""Validate Wave005 field-kit aggregate mirror (no baseline updates)."""
from __future__ import annotations
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    agg_path = ROOT / "artifacts/engineering_wave005/WAVE005_AGGREGATE.json"
    mirror = ROOT / "artifacts/engineering_wave005/device_os_mirror"
    agg = json.loads(agg_path.read_text())
    assert agg.get("DO_NOT_MERGE_UNTIL_WAVE005_DEPENDENCY_PRS_ACCEPTED") is True
    assert agg.get("BASELINE_COUNTS_UPDATED") is False
    assert agg.get("DO_NOT_UPDATE_BASELINE_COUNTS") is True
    assert agg.get("OS_PLATFORM_020_UNTOUCHED") is True
    assert agg.get("UNCONDITIONAL_TRUE_CLASSIFIERS") == 0
    assert agg.get("device_os_pr") == 127
    wave = json.loads((mirror / "WAVE005_RESULT.json").read_text())
    assert wave.get("wave005_ok") is True
    assert wave.get("summary", {}).get("total") == 12
    claims = json.loads((mirror / "CLAIM_BOUNDARIES.json").read_text())
    for k in ("STANDARDIZED_6G", "CARRIER_ACCEPTED", "REAL_NTN_MODEM_VALIDATED", "PHYSICAL_VALIDATION"):
        assert claims.get(k) is False, k
    baseline = ROOT / "program/digital_ecosystem_baseline_v2/BASELINE_V2_RESULT.json"
    assert baseline.exists()
    print("WAVE005_AGGREGATE_VALIDATION_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
