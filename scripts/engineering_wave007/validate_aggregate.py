#!/usr/bin/env python3
"""Validate Wave007 field-kit BeatLink aggregate mirror (no baseline mutations)."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ABS_RE = re.compile(r"(/Users/|/home/|/mnt/c/Users|[A-Za-z]:\\\\)")
REQUIRED = [
    "GAME-BEATLINK-001",
    "GAME-BEATLINK-002",
    "GAME-BEATLINK-003",
    "GAME-BEATLINK-004",
    "GAME-BEATLINK-005",
    "GAME-BEATLINK-006",
    "GAME-BEATLINK-007",
    "GAME-BEATLINK-008",
    "GAME-BEATLINK-009",
    "GAME-BEATLINK-010",
]
MIRROR_FILES = [
    "WAVE007_RESULT.json",
    "REQUIREMENT_RESULTS.json",
    "REQUIREMENT_EVALUATOR_MATRIX.json",
    "EVALUATOR_INTEGRITY_RESULT.json",
    "CLAIM_BOUNDARIES.json",
    "BEHAVIORAL_NEGATIVE_CONTROL_RESULT.json",
    "COMPLETION_GATE_NEGATIVE_CONTROL_RESULT.json",
    "E2E_MULTI_CLIENT_BROWSER_RESULT.json",
    "SCORING_LEDGER_REPLAY_RESULT.json",
    "SESSION_RESUME_A_B_C_RESULT.json",
    "SONG_SOURCE_RIGHTS_RESULT.json",
    "DEVICE_TIMING_PROFILE_RESULT.json",
    "AUDIENCE_INFLUENCE_SPAM_CAP_RESULT.json",
]


def main() -> int:
    agg_path = ROOT / "artifacts/engineering_wave007/WAVE007_AGGREGATE.json"
    mirror = ROOT / "artifacts/engineering_wave007/beatlink_mirror"
    marker = ROOT / "artifacts/engineering_wave007/DO_NOT_MERGE_UNTIL_WAVE007_BEATLINK_ACCEPTED.md"
    assert agg_path.is_file(), "missing WAVE007_AGGREGATE.json"
    assert marker.is_file(), "missing DO_NOT_MERGE marker"
    agg = json.loads(agg_path.read_text(encoding="utf-8"))

    assert agg["BASELINE_COUNTS_UPDATED"] is False
    assert agg["DO_NOT_UPDATE_BASELINE_COUNTS"] is True
    assert agg["DO_NOT_MERGE_UNTIL_WAVE007_BEATLINK_ACCEPTED"] is True
    assert agg["OS_PLATFORM_020_UNTOUCHED"] is True
    assert agg["UNCONDITIONAL_TRUE_CLASSIFIERS"] == 0
    assert agg["UNCONDITIONAL_TRUE_CLASSIFIERS_COMPUTED"] is True
    assert agg["COMPLETE_GATE_REQUIRES_10_OF_10"] is True
    assert agg["TARGET_REQUIREMENTS"] == 10
    assert agg["requirement_ids"] == REQUIRED
    assert agg["prerequisite_field_kit_pr_106"] == "MERGED"
    assert agg["beatlink_pr"] == 25
    assert agg["summary_mirror"]["validated"] == 10
    assert agg["PARTIAL"] is False
    assert agg["wave007_ok"] is True
    assert agg["CURSOR_MERGED_NOTHING"] is True
    assert agg["READY_FOR_OWNER_MERGE"] is False

    frozen = agg["post_wave006_baseline_frozen"]
    assert frozen["ATOMIC_TOTAL"] == 419
    assert frozen["DIGITAL_IMPLEMENTATION_COMPLETE"] == 85
    assert frozen["DIGITAL_IMPLEMENTATION_OPEN"] == 76
    assert frozen["DIGITAL_VALIDATION_OPEN"] == 1
    assert frozen["EVIDENCE_MAPPING_OPEN"] == 0
    assert frozen["NEXT_VALIDATION_ONLY"] == ["OS-PLATFORM-020"]

    for name in MIRROR_FILES:
        assert (mirror / name).is_file(), f"missing mirror {name}"

    wave = json.loads((mirror / "WAVE007_RESULT.json").read_text(encoding="utf-8"))
    assert wave["wave007_ok"] is True
    assert wave["summary"]["validated"] == 10
    assert wave["IMPLEMENTED_AND_VALIDATED"] == 10
    assert wave["PARTIAL"] is False
    assert wave["UNCONDITIONAL_TRUE_CLASSIFIERS"] == 0
    assert wave["OS_PLATFORM_020_UNTOUCHED"] is True
    assert wave["BASELINE_COUNTS_UPDATED"] is False

    claims = json.loads((mirror / "CLAIM_BOUNDARIES.json").read_text(encoding="utf-8"))
    assert claims.get("COMMERCIAL_MEDIA_RIPPED") is False
    assert claims.get("LINK_EQUALS_RIP_PERMISSION") is False
    assert claims.get("PROVIDER_RIGHTS_FABRICATED") is False
    assert all(v is False for v in claims.values())

    behavioral = json.loads(
        (mirror / "BEHAVIORAL_NEGATIVE_CONTROL_RESULT.json").read_text(encoding="utf-8")
    )
    assert behavioral.get("BEHAVIORAL_NEGATIVE_CONTROLS_PASS") is True

    song = json.loads((mirror / "SONG_SOURCE_RIGHTS_RESULT.json").read_text(encoding="utf-8"))
    assert song.get("LINK_IS_NOT_RIP_PERMISSION") is True

    # No Baseline v2 files may be part of this aggregate PR validation surface.
    baseline_touch_forbidden = [
        ROOT / "program/digital_ecosystem_baseline_v2/BASELINE_V2_RESULT.json",
    ]
    # File may exist on main; aggregate must not rewrite it — validator only checks aggregate artifacts.
    for path in list(mirror.glob("*.json")) + [agg_path]:
        blob = path.read_text(encoding="utf-8")
        if ABS_RE.search(blob):
            raise SystemExit(f"absolute path in {path.name}")
        if "sk-" in blob or "Bearer " in blob:
            raise SystemExit(f"secret-like token in {path.name}")

    print("wave007 beatlink aggregate validation PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
