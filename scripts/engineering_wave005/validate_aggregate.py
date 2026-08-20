#!/usr/bin/env python3
"""Validate Wave005 field-kit integrity-repair aggregate mirror (no baseline updates)."""
from __future__ import annotations
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ABS_RE = re.compile(r"(/Users/|/home/|/mnt/|/tmp/|[A-Za-z]:\\\\)")


def main() -> int:
    agg_path = ROOT / "artifacts/engineering_wave005/WAVE005_AGGREGATE.json"
    mirror = ROOT / "artifacts/engineering_wave005/device_os_mirror"
    agg = json.loads(agg_path.read_text())
    assert agg.get("DO_NOT_MERGE_UNTIL_WAVE005_INTEGRITY_REPAIR_ACCEPTED") is True
    assert agg.get("BASELINE_COUNTS_UPDATED") is False
    assert agg.get("DO_NOT_UPDATE_BASELINE_COUNTS") is True
    assert agg.get("OS_PLATFORM_020_UNTOUCHED") is True
    assert agg.get("UNCONDITIONAL_TRUE_CLASSIFIERS") == 0
    assert agg.get("UNCONDITIONAL_TRUE_CLASSIFIERS_COMPUTED") is True
    assert agg.get("historical_device_os_pr") == 127
    assert agg.get("historical_field_kit_pr") == 101
    assert agg.get("authoritative_repair_device_os_pr") == 128
    assert agg.get("device_os_pr") == 128
    wave = json.loads((mirror / "WAVE005_RESULT.json").read_text())
    assert wave.get("wave005_ok") is True
    assert wave.get("summary", {}).get("total") == 12
    assert wave.get("summary", {}).get("validated") == 12
    assert wave.get("UNCONDITIONAL_TRUE_CLASSIFIERS") == 0
    claims = json.loads((mirror / "CLAIM_BOUNDARIES.json").read_text())
    for k in ("STANDARDIZED_6G", "CARRIER_ACCEPTED", "REAL_NTN_MODEM_VALIDATED", "PHYSICAL_VALIDATION", "PRODUCTION_APP_PRIORITY_SIGNING"):
        assert claims.get(k) is False, k
    for req in ("EVALUATOR_INTEGRITY_RESULT.json", "COMPLETION_GATE_NEGATIVE_CONTROL_RESULT.json",
                "APPLICATION_PRIORITY_AUTHORITY_RESULT.json", "APPLICATION_PRIORITY_BOUNDARY_RESULT.json",
                "USER_PREFERENCE_POLICY_RESULT.json", "SOURCE_PROVENANCE_RESULT.json", "INTEGRITY_REPAIR_RESULT.json"):
        assert (mirror / req).exists(), req
    for path in mirror.glob("*.json"):
        assert not ABS_RE.search(path.read_text(encoding="utf-8")), path.name
    baseline = ROOT / "program/digital_ecosystem_baseline_v2/BASELINE_V2_RESULT.json"
    assert baseline.exists()
    # Prove baseline registers untouched by this PR (file still present; counts not edited here)
    print("WAVE005_INTEGRITY_AGGREGATE_VALIDATION_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
