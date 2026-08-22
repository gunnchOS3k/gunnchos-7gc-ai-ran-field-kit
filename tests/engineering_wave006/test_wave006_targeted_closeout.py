"""Validate Wave 006 targeted closeout artifact and register freeze."""
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
    "NET-ORCH-026",
    "NET-ORCH-027",
    "NET-ORCH-028",
    "NET-ORCH-029",
    "NET-ORCH-030",
    "NET-ORCH-031",
    "NET-ORCH-032",
    "NET-ORCH-033",
    "NET-ORCH-034",
    "NET-ORCH-035",
}


def test_targeted_row_diff_freeze():
    root = Path(__file__).resolve().parents[2]
    diff_path = root / "artifacts/engineering_wave006_closeout/TARGETED_ROW_DIFF.json"
    data = json.loads(diff_path.read_text(encoding="utf-8"))
    assert data["untargeted_rows_changed"] == 0
    assert data["unexpected_changed_ids"] == []
    assert set(data["target_ids"]) == TARGET_IDS
    assert data["OS_PLATFORM_020_CHANGED"] is False
    assert data["MULTIPATH_KIND"] == "APPLICATION_LEVEL_MULTIPATH"
    assert data["closeout_validation"]["ENGINEERING_WAVE_006_TARGETED_CLOSEOUT_VALIDATION_PASS"] is True
    assert data["claim_boundaries"]["CARRIER_ACCEPTED"] is False
    assert data["claim_boundaries"]["STANDARDIZED_6G"] is False
    assert data["claim_boundaries"]["REAL_MPTCP"] is False
    assert data["claim_boundaries"]["PRODUCTION_MPTCP_VALIDATED"] is False
    assert data["claim_boundaries"]["REAL_NTN_MODEM_VALIDATED"] is False
    assert data["claim_boundaries"]["FIELD_MEASURED_SATELLITE_VISIBILITY"] is False
    assert data["closeout_assessment"]["OS_PLATFORM_020_NOT_COMPLETE"] is True
    assert data["closeout_assessment"]["targets_remaining_validation_open"] == []
    assert set(data["closeout_assessment"]["targets_digital_implementation_complete"]) == TARGET_IDS
    x = data["closeout_validation"]["cross_checks"]
    assert x["complete_delta"] == 10
    assert x["impl_open_delta"] == 10
    assert x["validation_open_unchanged"] is True
    assert x["next_val_only_020"] is True


def test_closeout_result_and_queues():
    root = Path(__file__).resolve().parents[2]
    result = json.loads(
        (root / "artifacts/engineering_wave006_closeout/CLOSEOUT_RESULT.json").read_text(encoding="utf-8")
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
        (root / "program/digital_ecosystem_baseline_v2/BASELINE_V2_RESULT.json").read_text(encoding="utf-8")
    )
    totals = reg["totals"]
    assert result["ENGINEERING_WAVE_006_TARGETED_CLOSEOUT_VALIDATION_PASS"] is True
    assert result["ENGINEERING_WAVE_006_CLOSEOUT"] == "COMPLETE"
    assert result["CURSOR_MERGED_NOTHING"] is True
    assert result["MULTIPATH_KIND"] == "APPLICATION_LEVEL_MULTIPATH"
    assert result["OS_PLATFORM_020"]["validation_state"] == "DIGITAL_VALIDATION_OPEN"
    assert result["OS_PLATFORM_020"]["implementation_present"] is True
    assert result["OS_PLATFORM_020"]["blocker"] == "SANDBOX_ENFORCEMENT_ENVIRONMENT"
    assert result["OS_PLATFORM_020"]["OS_PLATFORM_020_CHANGED"] is False
    assert result["OS_PLATFORM_020"]["NOT_MARKED_COMPLETE"] is True
    assert totals["DIGITAL_IMPLEMENTATION_OPEN"] <= 51
    assert totals["DIGITAL_IMPLEMENTATION_COMPLETE"] + totals["DIGITAL_IMPLEMENTATION_OPEN"] + totals["DIGITAL_VALIDATION_OPEN"] == 162
    assert totals["EVIDENCE_MAPPING_OPEN"] == 0
    assert result["post_closeout_baseline"]["DIGITAL_CONTROLLABLE_POOL"] == 162
    assert len(impl["all_items"]) == totals["DIGITAL_IMPLEMENTATION_OPEN"]
    assert impl["total_open"] == totals["DIGITAL_IMPLEMENTATION_OPEN"]
    if _wave009_closeout_applied(baseline):
        assert totals["DIGITAL_IMPLEMENTATION_COMPLETE"] >= 111
        assert totals["DIGITAL_VALIDATION_OPEN"] == 0
        assert len(val["all_items"]) == 0
        assert val["total_open"] == 0
    else:
        assert totals["DIGITAL_IMPLEMENTATION_COMPLETE"] >= 110
        assert totals["DIGITAL_VALIDATION_OPEN"] == 1
        assert len(val["all_items"]) == 1
        assert val["total_open"] == 1
        assert val["all_items"][0]["requirement_id"] == "OS-PLATFORM-020"
    assert not any(i["requirement_id"] in TARGET_IDS for i in impl["all_items"])
    row020 = next(r for r in reg["requirements"] if r["requirement_id"] == "OS-PLATFORM-020")
    if _wave009_closeout_applied(baseline):
        assert row020["work_state"] == "DIGITAL_IMPLEMENTATION_COMPLETE"
    else:
        assert row020["work_state"] == "DIGITAL_VALIDATION_OPEN"
    assert row020["implementation_state"] == "IMPLEMENTED"
    for rid in TARGET_IDS:
        row = next(r for r in reg["requirements"] if r["requirement_id"] == rid)
        assert row["work_state"] == "DIGITAL_IMPLEMENTATION_COMPLETE"
    # Wave001–005 history preserved
    assert "ENGINEERING_WAVE_001_TARGETED_CLOSEOUT" in baseline
    assert "ENGINEERING_WAVE_002_TARGETED_CLOSEOUT" in baseline
    assert "ENGINEERING_WAVE_003_TARGETED_CLOSEOUT" in baseline
    assert "ENGINEERING_WAVE_004_TARGETED_PARTIAL_CLOSEOUT" in baseline
    assert "ENGINEERING_WAVE_005_TARGETED_CLOSEOUT" in baseline
    assert "ENGINEERING_WAVE_006_TARGETED_CLOSEOUT" in baseline
    assert "ENGINEERING_WAVE_007_TARGETED_CLOSEOUT" in baseline
    assert "wave001_targeted_closeout" in reg
    assert "wave002_targeted_closeout" in reg
    assert "wave003_targeted_closeout" in reg
    assert "wave004_targeted_partial_closeout" in reg
    assert "wave005_targeted_closeout" in reg
    assert "wave006_targeted_closeout" in reg
    assert "wave007_targeted_closeout" in reg
