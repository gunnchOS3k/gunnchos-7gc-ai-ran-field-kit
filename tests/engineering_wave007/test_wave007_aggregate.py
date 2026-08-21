from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_aggregate_flags():
    agg = json.loads((ROOT / "artifacts/engineering_wave007/WAVE007_AGGREGATE.json").read_text())
    assert agg["BASELINE_COUNTS_UPDATED"] is False
    assert agg["DO_NOT_MERGE_UNTIL_WAVE007_BEATLINK_ACCEPTED"] is True
    assert agg["TARGET_REQUIREMENTS"] == 10
    assert agg["OS_PLATFORM_020_UNTOUCHED"] is True
    assert agg["READY_FOR_OWNER_MERGE"] is False
    assert agg["beatlink_pr"] == 25
    assert agg["prerequisite_field_kit_pr_106"] == "MERGED"


def test_mirror_wave007_ok():
    wave = json.loads(
        (ROOT / "artifacts/engineering_wave007/beatlink_mirror/WAVE007_RESULT.json").read_text()
    )
    assert wave["wave007_ok"] is True
    assert wave["summary"]["validated"] == 10
    assert wave["PARTIAL"] is False


def test_claim_boundaries_false():
    claims = json.loads(
        (ROOT / "artifacts/engineering_wave007/beatlink_mirror/CLAIM_BOUNDARIES.json").read_text()
    )
    assert claims["COMMERCIAL_MEDIA_RIPPED"] is False
    assert claims["LINK_EQUALS_RIP_PERMISSION"] is False


def test_frozen_post_wave006_counts():
    agg = json.loads((ROOT / "artifacts/engineering_wave007/WAVE007_AGGREGATE.json").read_text())
    frozen = agg["post_wave006_baseline_frozen"]
    assert frozen["ATOMIC_TOTAL"] == 419
    assert frozen["DIGITAL_IMPLEMENTATION_COMPLETE"] == 85
    assert frozen["DIGITAL_IMPLEMENTATION_OPEN"] == 76
    assert frozen["DIGITAL_VALIDATION_OPEN"] == 1
    assert frozen["NEXT_VALIDATION_ONLY"] == ["OS-PLATFORM-020"]
