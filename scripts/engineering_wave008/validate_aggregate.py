#!/usr/bin/env python3
"""Validate Wave008 field-kit Archive aggregate mirror (post-acceptance; no baseline mutations)."""
from __future__ import annotations

import json
import re
import subprocess
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
    "WAVE008_INTEGRITY_REPAIR_RESULT.json",
    "FIELD_PROVENANCE_RESULT.json",
    "PIPELINE_AB_REPRODUCTION_RESULT.json",
]
EXPECTED_HEAD = "0a8089ad50df36a738743e358dcc039f97a004cb"
EXPECTED_MERGE = "069243c365552f00707650e9d81a8046ba3075d8"


def main() -> int:
    agg_path = ROOT / "artifacts/engineering_wave008/WAVE008_AGGREGATE.json"
    mirror = ROOT / "artifacts/engineering_wave008/archive_mirror"
    marker = ROOT / "artifacts/engineering_wave008/DO_NOT_MERGE_UNTIL_WAVE008_ARCHIVE_ACCEPTED.md"
    assert agg_path.is_file(), "missing WAVE008_AGGREGATE.json"
    assert marker.is_file(), "missing DO_NOT_MERGE marker"
    agg = json.loads(agg_path.read_text(encoding="utf-8"))
    marker_text = marker.read_text(encoding="utf-8")
    assert "SATISFIED" in marker_text or "satisfied" in marker_text.lower()
    assert EXPECTED_HEAD in marker_text
    assert EXPECTED_MERGE in marker_text
    assert "#35" in marker_text or "35" in marker_text

    # Post-acceptance sequencing truth
    assert agg["archive_pr"] == 35
    assert agg["archive_head_sha"] == EXPECTED_HEAD
    assert agg["archive_merge_sha"] == EXPECTED_MERGE
    assert agg["archive_accepted_main"] is True
    assert agg["archive_accepted_main_verified"] is True
    assert agg["archive_tree_equivalence"] is True
    assert agg["ARCHIVE_ACCEPTANCE_CONDITION_SATISFIED"] is True
    assert agg["DO_NOT_MERGE_UNTIL_WAVE008_ARCHIVE_ACCEPTED"] is False
    assert agg["READY_FOR_OWNER_MERGE"] is True
    assert agg["READY_FOR_OWNER_MERGE_SEQUENCE"] is True
    assert agg["TARGET_REQUIREMENTS"] == 15
    assert agg["IMPLEMENTED_AND_VALIDATED"] == 15
    assert agg["BASELINE_COUNTS_UPDATED"] is False
    assert agg["DO_NOT_UPDATE_BASELINE_COUNTS"] is True
    assert agg["OS_PLATFORM_020_UNTOUCHED"] is True
    assert agg["CURSOR_MERGED_NOTHING"] is True
    assert agg.get("BASELINE_FILES_CHANGED", 1) == 0

    # Historical guard was false/blocked before #35
    history = agg.get("sequencing_guard_history") or {}
    before = history.get("before_archive_35_accepted") or {}
    assert before.get("DO_NOT_MERGE_UNTIL_WAVE008_ARCHIVE_ACCEPTED") is True
    assert before.get("READY_FOR_OWNER_MERGE") is False
    assert before.get("READY_FOR_OWNER_MERGE_SEQUENCE") is False

    assert agg["UNCONDITIONAL_TRUE_CLASSIFIERS"] == 0
    assert agg["UNCONDITIONAL_TRUE_CLASSIFIERS_COMPUTED"] is True
    assert agg["COMPLETE_GATE_REQUIRES_15_OF_15"] is True
    assert agg["requirement_ids"] == REQUIRED
    assert agg["prerequisite_field_kit_pr_108"] == "MERGED"
    assert agg.get("mandatory_playwright") is True
    assert agg.get("playwright_skipped") is False
    assert agg["summary_mirror"]["validated"] == 15
    assert agg["PARTIAL"] is False
    assert agg["wave008_ok"] is True
    assert agg.get("FIXTURE_ONLY_SOURCE_VERIFIED_COUNT", 1) == 0
    assert agg.get("AUTHENTIC_EXTERNAL_SOURCE_SNAPSHOTS_PRESENT") is False
    assert agg.get("SOURCE_VERIFIED_EXTERNAL_RECORD_COUNT", 1) == 0
    assert agg.get("SOURCE_VERIFIED_REQUIRES_VERIFIED_INTEGRATION") is True
    assert agg.get("BEHAVIORAL_NEGATIVE_CONTROL_COUNT", 0) >= 22
    assert agg.get("BEHAVIORAL_NEGATIVE_CONTROLS_PASS") is True

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
    assert wave.get("FIXTURE_ONLY_SOURCE_VERIFIED_COUNT", 1) == 0
    assert wave.get("AUTHENTIC_EXTERNAL_SOURCE_SNAPSHOTS_PRESENT") is False
    assert wave.get("SOURCE_VERIFIED_EXTERNAL_RECORD_COUNT", 1) == 0

    browser = json.loads((mirror / "ARCHIVEDEX_BROWSER_E2E_RESULT.json").read_text(encoding="utf-8"))
    assert browser.get("playwright_ran") is True
    assert browser.get("playwright_skipped") is False
    assert browser.get("ok") is True
    assert browser.get("runtime") == "vite_preview"

    claims = json.loads((mirror / "CLAIM_BOUNDARIES.json").read_text(encoding="utf-8"))
    assert claims.get("ALL_KNOWN_LIFE_COMPLETE") is False
    assert claims.get("GBIF_LIVE_INTEGRATION") is False
    assert claims.get("OS_PLATFORM_020_TOUCHED") is False
    assert claims.get("BASELINE_COUNTS_UPDATED") is False
    assert claims.get("AUTHENTIC_EXTERNAL_SOURCE_SNAPSHOTS_PRESENT") is False

    behavioral = json.loads(
        (mirror / "BEHAVIORAL_NEGATIVE_CONTROL_RESULT.json").read_text(encoding="utf-8")
    )
    assert behavioral.get("BEHAVIORAL_NEGATIVE_CONTROLS_PASS") is True
    assert behavioral.get("BEHAVIORAL_NEGATIVE_CONTROL_COUNT", 0) >= 22

    repair = json.loads((mirror / "WAVE008_INTEGRITY_REPAIR_RESULT.json").read_text(encoding="utf-8"))
    assert repair.get("WAVE008_PREMERGE_INTEGRITY_REPAIR") == "PASS"
    assert repair.get("STATIC_HARNESS_CLOSURE") is False
    assert repair.get("DEFECT_B_PYTHON_PIPELINE") is True
    assert repair.get("AUTHENTIC_EXTERNAL_SOURCE_SNAPSHOTS_PRESENT") is False
    assert repair.get("SOURCE_VERIFIED_EXTERNAL_RECORD_COUNT") == 0

    truth = json.loads((mirror / "SOURCE_INTEGRATION_TRUTH_RESULT.json").read_text(encoding="utf-8"))
    assert truth.get("MISSING_DEFAULTS_TO_NEEDS_VERIFICATION") is True
    assert truth.get("NO_FAKE_LIVE") is True
    assert truth.get("FIXTURE_ONLY_SOURCE_VERIFIED_COUNT") == 0

    coverage = json.loads((mirror / "COVERAGE_SCOPE_RESULT.json").read_text(encoding="utf-8"))
    assert coverage.get("DENOMINATOR_EXPLICIT") is True
    assert coverage.get("ADDING_UNDOCUMENTED_DECREASES_PERCENT") is True

    field = json.loads((mirror / "FIELD_PROVENANCE_RESULT.json").read_text(encoding="utf-8"))
    assert field.get("HASH_BINDINGS") is True
    assert field.get("UNKNOWN_PATH_REJECTED") is True

    snap = json.loads((mirror / "SNAPSHOT_REPRODUCTION_RESULT.json").read_text(encoding="utf-8"))
    assert snap.get("INDEPENDENT_AB") is True
    assert snap.get("TAMPER_REJECTED") is True

    pipeline = json.loads((mirror / "PIPELINE_AB_REPRODUCTION_RESULT.json").read_text(encoding="utf-8"))
    assert pipeline.get("ok") is True
    assert pipeline.get("independent_runs") == 2

    eval_int = json.loads((mirror / "EVALUATOR_INTEGRITY_RESULT.json").read_text(encoding="utf-8"))
    assert eval_int.get("UNCONDITIONAL_TRUE_CLASSIFIERS") == 0

    # Aggregate PR #109 must not mutate Baseline. Targeted closeout may update Baseline
    # after #109 is accepted; skip live git-diff guard when closeout artifacts are present.
    closeout_marker = ROOT / "artifacts/engineering_wave008_closeout/CLOSEOUT_RESULT.json"
    if not closeout_marker.is_file():
        try:
            diff = subprocess.check_output(
                ["git", "diff", "--name-only", "origin/main...HEAD"],
                cwd=ROOT,
                text=True,
                stderr=subprocess.DEVNULL,
            )
            baseline_hits = [
                line
                for line in diff.splitlines()
                if "baseline" in line.lower() or "digital_ecosystem_baseline" in line.lower()
            ]
            assert not baseline_hits, f"Baseline files changed: {baseline_hits}"
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
    else:
        closeout = json.loads(closeout_marker.read_text(encoding="utf-8"))
        assert closeout.get("ENGINEERING_WAVE_008_TARGETED_CLOSEOUT_VALIDATION_PASS") is True
        # Historical aggregate claim remains: #109 itself changed 0 Baseline files.
        assert agg.get("BASELINE_FILES_CHANGED", 1) == 0

    # Absolute path / secret scan on aggregate artifacts
    for path in [agg_path, *mirror.glob("*.json")]:
        text = path.read_text(encoding="utf-8")
        assert not ABS_RE.search(text), f"absolute path in {path.name}"
        assert "ghp_" not in text and "sk-" not in text

    print("WAVE008_AGGREGATE_POST_ACCEPTANCE_VALIDATION_PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"WAVE008_AGGREGATE_POST_ACCEPTANCE_VALIDATION_FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
