"""Validate Wave 004 targeted partial closeout artifact and register freeze."""
from __future__ import annotations

import json
from pathlib import Path

def _wave009_closeout_applied(baseline: dict) -> bool:
    return baseline.get("phase") == "ENGINEERING_WAVE_009_TARGETED_CLOSEOUT" or bool(
        (baseline.get("ENGINEERING_WAVE_009_TARGETED_CLOSEOUT") or {}).get(
            "ENGINEERING_WAVE_009_TARGETED_CLOSEOUT_VALIDATION_PASS"
        )
    )


TARGET_IDS = {
    "OS-PLATFORM-008",
    "OS-PLATFORM-009",
    "OS-PLATFORM-010",
    "OS-PLATFORM-011",
    "OS-PLATFORM-012",
    "OS-PLATFORM-013",
    "OS-PLATFORM-016",
    "OS-PLATFORM-018",
    "OS-PLATFORM-020",
    "OS-PLATFORM-021",
    "OS-PLATFORM-022",
    "OS-PLATFORM-023",
}

COMPLETE_IDS = TARGET_IDS - {"OS-PLATFORM-020"}


def test_targeted_row_diff_freeze():
    root = Path(__file__).resolve().parents[2]
    diff_path = root / "artifacts/engineering_wave004_closeout/TARGETED_ROW_DIFF.json"
    data = json.loads(diff_path.read_text(encoding="utf-8"))
    assert data["untargeted_rows_changed"] == 0
    assert data["unexpected_changed_ids"] == []
    assert set(data["target_ids"]) == TARGET_IDS
    assert data["closeout_validation"]["ENGINEERING_WAVE_004_TARGETED_PARTIAL_CLOSEOUT_VALIDATION_PASS"] is True
    assert data["claim_boundaries"]["KERNEL_SANDBOX"] is False
    assert data["claim_boundaries"]["PLAIN_SUBPROCESS_COUNTS_AS_SANDBOX"] is False
    assert data["claim_boundaries"]["PRODUCTION_SIGNING"] is False
    assert data["claim_boundaries"]["WCAG_VALIDATED"] is False
    assert data["closeout_assessment"]["OS_PLATFORM_020_NOT_COMPLETE"] is True
    assert set(data["closeout_assessment"]["targets_remaining_validation_open"]) == {"OS-PLATFORM-020"}
    assert set(data["closeout_assessment"]["targets_digital_implementation_complete"]) == COMPLETE_IDS


def test_closeout_result_and_queues():
    root = Path(__file__).resolve().parents[2]
    result = json.loads(
        (root / "artifacts/engineering_wave004_closeout/CLOSEOUT_RESULT.json").read_text(encoding="utf-8")
    )
    reg = json.loads(
        (root / "program/digital_ecosystem_baseline_v2/MASTER_COMPLETION_REGISTER.json").read_text(
            encoding="utf-8"
        )
    )
    impl = json.loads(
        (root / "program/digital_ecosystem_baseline_v2/NEXT_DIGITAL_IMPLEMENTATION_WORK.json").read_text(
            encoding="utf-8"
        )
    )
    val = json.loads(
        (root / "program/digital_ecosystem_baseline_v2/NEXT_DIGITAL_VALIDATION_WORK.json").read_text(
            encoding="utf-8"
        )
    )
    baseline = json.loads(
        (root / "program/digital_ecosystem_baseline_v2/BASELINE_V2_RESULT.json").read_text(
            encoding="utf-8"
        )
    )
    totals = reg["totals"]
    assert result["ENGINEERING_WAVE_004_TARGETED_PARTIAL_CLOSEOUT_VALIDATION_PASS"] is True
    assert result["CURSOR_MERGED_NOTHING"] is True
    # Historical Wave004 CLOSEOUT_RESULT remains frozen at DIGITAL_VALIDATION_OPEN.
    assert result["OS_PLATFORM_020"]["validation_state"] == "DIGITAL_VALIDATION_OPEN"
    assert result["OS_PLATFORM_020"]["implementation_present"] is True
    assert result["OS_PLATFORM_020"]["blocker"] == "SANDBOX_ENFORCEMENT_ENVIRONMENT"
    assert result["OS_PLATFORM_020"]["plain_subprocess_counts_as_sandbox"] is False
    assert result["OS_PLATFORM_020"]["kernel_sandbox"] is False
    assert result["OS_PLATFORM_020"]["NOT_MARKED_COMPLETE"] is True
    assert totals["DIGITAL_IMPLEMENTATION_OPEN"] == 51
    assert totals["EVIDENCE_MAPPING_OPEN"] == 0
    assert len(impl["all_items"]) == totals["DIGITAL_IMPLEMENTATION_OPEN"]
    assert impl["total_open"] == totals["DIGITAL_IMPLEMENTATION_OPEN"]
    if _wave009_closeout_applied(baseline):
        assert totals["DIGITAL_IMPLEMENTATION_COMPLETE"] == 111
        assert totals["DIGITAL_VALIDATION_OPEN"] == 0
        assert len(val["all_items"]) == 0
        assert val["total_open"] == 0
    else:
        assert totals["DIGITAL_IMPLEMENTATION_COMPLETE"] == 110
        assert totals["DIGITAL_VALIDATION_OPEN"] == 1
        assert len(val["all_items"]) == 1
        assert val["total_open"] == 1
        assert val["all_items"][0]["requirement_id"] == "OS-PLATFORM-020"
        assert val["all_items"][0]["implementation_present"] is True
        assert val["all_items"][0]["blocker_class"] == "BLOCKED_ENVIRONMENT"
    assert not any(i["requirement_id"] in TARGET_IDS for i in impl["all_items"])
    row020 = next(r for r in reg["requirements"] if r["requirement_id"] == "OS-PLATFORM-020")
    if _wave009_closeout_applied(baseline):
        assert row020["work_state"] == "DIGITAL_IMPLEMENTATION_COMPLETE"
    else:
        assert row020["work_state"] == "DIGITAL_VALIDATION_OPEN"
    assert row020["implementation_state"] == "IMPLEMENTED"
