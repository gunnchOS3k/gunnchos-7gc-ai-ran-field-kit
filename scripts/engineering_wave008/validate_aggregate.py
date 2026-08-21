#!/usr/bin/env python3
"""Validate Wave008 field-kit Archive aggregate mirror (no baseline mutations)."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ABS_RE = re.compile(r"(/Users/|/home/|/mnt/c/Users|[A-Za-z]:\\\\)")
REQUIRED = [f"GAME-AOL-{i:03d}" for i in range(1, 16)]
MIRROR_FILES = [
    "WAVE008_RESULT.json",
    "REQUIREMENT_RESULTS.json",
    "REQUIREMENT_EVALUATOR_MATRIX.json",
    "EVALUATOR_INTEGRITY_RESULT.json",
    "CLAIM_BOUNDARIES.json",
    "BEHAVIORAL_NEGATIVE_CONTROL_RESULT.json",
    "COMPLETION_GATE_NEGATIVE_CONTROL_RESULT.json",
    "ARCHIVEDEX_BROWSER_E2E_RESULT.json",
    "COVERAGE_SCOPE_RESULT.json",
    "CANONICAL_IDENTIFIER_RESULT.json",
    "SOURCE_INTEGRATION_TRUTH_RESULT.json",
    "SNAPSHOT_REPRODUCTION_RESULT.json",
    "EXTERNAL_TEXT_SAFETY_RESULT.json",
]


def main() -> int:
    agg_path = ROOT / "artifacts/engineering_wave008/WAVE008_AGGREGATE.json"
    mirror = ROOT / "artifacts/engineering_wave008/archive_mirror"
    marker = ROOT / "artifacts/engineering_wave008/DO_NOT_MERGE_UNTIL_WAVE008_ARCHIVE_ACCEPTED.md"
    assert agg_path.is_file(), "missing WAVE008_AGGREGATE.json"
    assert marker.is_file(), "missing DO_NOT_MERGE marker"
    agg = json.loads(agg_path.read_text(encoding="utf-8"))

    assert agg["BASELINE_COUNTS_UPDATED"] is False
    assert agg["DO_NOT_UPDATE_BASELINE_COUNTS"] is True
    assert agg["DO_NOT_MERGE_UNTIL_WAVE008_ARCHIVE_ACCEPTED"] is True
    assert agg["OS_PLATFORM_020_UNTOUCHED"] is True
    assert agg["UNCONDITIONAL_TRUE_CLASSIFIERS"] == 0
    assert agg["UNCONDITIONAL_TRUE_CLASSIFIERS_COMPUTED"] is True
    assert agg["COMPLETE_GATE_REQUIRES_15_OF_15"] is True
    assert agg["TARGET_REQUIREMENTS"] == 15
    assert agg["requirement_ids"] == REQUIRED
    assert agg["prerequisite_field_kit_pr_108"] == "MERGED"
    assert agg["archive_pr"] == 35
    assert agg.get("mandatory_playwright") is True
    assert agg.get("playwright_skipped") is False
    assert agg["summary_mirror"]["validated"] == 15
    assert agg["PARTIAL"] is False
    assert agg["wave008_ok"] is True
    assert agg["IMPLEMENTED_AND_VALIDATED"] == 15
    assert agg["CURSOR_MERGED_NOTHING"] is True
    assert agg["READY_FOR_OWNER_MERGE"] is False

    frozen = agg["post_wave007_baseline_frozen"]
    assert frozen["ATOMIC_TOTAL"] == 419
    assert frozen["DIGITAL_IMPLEMENTATION_COMPLETE"] == 95
    assert frozen["DIGITAL_IMPLEMENTATION_OPEN"] == 66
    assert frozen["DIGITAL_VALIDATION_OPEN"] == 1
    assert frozen["EVIDENCE_MAPPING_OPEN"] == 0
    assert frozen["NEXT_VALIDATION_ONLY"] == ["OS-PLATFORM-020"]

    for name in MIRROR_FILES:
        assert (mirror / name).is_file(), f"missing mirror {name}"

    wave = json.loads((mirror / "WAVE008_RESULT.json").read_text(encoding="utf-8"))
    assert wave["wave008_ok"] is True
    assert wave["summary"]["validated"] == 15
    assert wave["IMPLEMENTED_AND_VALIDATED"] == 15
    assert wave["PARTIAL"] is False
    assert wave["UNCONDITIONAL_TRUE_CLASSIFIERS"] == 0
    assert wave.get("PLAYWRIGHT_MANDATORY") is True
    assert wave.get("PLAYWRIGHT_SKIPPED") is False
    assert wave["OS_PLATFORM_020_UNTOUCHED"] is True
    assert wave["BASELINE_COUNTS_UPDATED"] is False

    browser = json.loads((mirror / "ARCHIVEDEX_BROWSER_E2E_RESULT.json").read_text(encoding="utf-8"))
    assert browser.get("playwright_ran") is True
    assert browser.get("playwright_skipped") is False
    assert browser.get("ok") is True

    claims = json.loads((mirror / "CLAIM_BOUNDARIES.json").read_text(encoding="utf-8"))
    assert claims.get("ALL_KNOWN_LIFE_COMPLETE") is False
    assert claims.get("GBIF_LIVE_INTEGRATION") is False
    assert claims.get("OS_PLATFORM_020_TOUCHED") is False
    assert claims.get("BASELINE_COUNTS_UPDATED") is False

    behavioral = json.loads(
        (mirror / "BEHAVIORAL_NEGATIVE_CONTROL_RESULT.json").read_text(encoding="utf-8")
    )
    assert behavioral.get("BEHAVIORAL_NEGATIVE_CONTROLS_PASS") is True
    assert behavioral.get("BEHAVIORAL_NEGATIVE_CONTROL_COUNT", 0) >= 22
    assert agg.get("FIXTURE_ONLY_SOURCE_VERIFIED_COUNT", 1) == 0
    assert agg.get("AUTHENTIC_EXTERNAL_SOURCE_SNAPSHOTS_PRESENT") is False
    assert browser.get("runtime") == "vite_preview"
    assert (mirror / "WAVE008_INTEGRITY_REPAIR_RESULT.json").is_file()
    repair = json.loads((mirror / "WAVE008_INTEGRITY_REPAIR_RESULT.json").read_text(encoding="utf-8"))
    assert repair.get("WAVE008_PREMERGE_INTEGRITY_REPAIR") in ("PASS", "PARTIAL")
    assert repair.get("STATIC_HARNESS_CLOSURE") is False
    assert agg["archive_head_sha"]
    assert len(agg["archive_head_sha"]) == 40

    truth = json.loads((mirror / "SOURCE_INTEGRATION_TRUTH_RESULT.json").read_text(encoding="utf-8"))
    assert truth.get("MISSING_DEFAULTS_TO_NEEDS_VERIFICATION") is True
    assert truth.get("NO_FAKE_LIVE") is True

    # Absolute path / secret scan on aggregate artifacts
    for path in [agg_path, *mirror.glob("*.json")]:
        text = path.read_text(encoding="utf-8")
        assert not ABS_RE.search(text), f"absolute path in {path.name}"
        assert "ghp_" not in text and "sk-" not in text

    print("WAVE008_AGGREGATE_VALIDATION_PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"WAVE008_AGGREGATE_VALIDATION_FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
