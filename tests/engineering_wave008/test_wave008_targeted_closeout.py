"""Validate Wave 008 targeted closeout artifact and register freeze."""
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
    "GAME-AOL-001",
    "GAME-AOL-002",
    "GAME-AOL-003",
    "GAME-AOL-004",
    "GAME-AOL-005",
    "GAME-AOL-006",
    "GAME-AOL-007",
    "GAME-AOL-008",
    "GAME-AOL-009",
    "GAME-AOL-010",
    "GAME-AOL-011",
    "GAME-AOL-012",
    "GAME-AOL-013",
    "GAME-AOL-014",
    "GAME-AOL-015",
}


def test_targeted_row_diff_freeze():
    root = Path(__file__).resolve().parents[2]
    diff_path = root / "artifacts/engineering_wave008_closeout/TARGETED_ROW_DIFF.json"
    data = json.loads(diff_path.read_text(encoding="utf-8"))
    assert data["untargeted_rows_changed"] == 0
    assert data["unexpected_changed_ids"] == []
    assert set(data["target_ids"]) == TARGET_IDS
    assert set(data["changed_ids"]) == TARGET_IDS
    assert data["OS_PLATFORM_020_CHANGED"] is False
    assert data["closeout_validation"]["ENGINEERING_WAVE_008_TARGETED_CLOSEOUT_VALIDATION_PASS"] is True
    assert data["claim_boundaries"]["AUTHENTIC_EXTERNAL_SOURCE_SNAPSHOTS_PRESENT"] is False
    assert data["claim_boundaries"]["ALL_KNOWN_LIFE_COMPLETE"] is False
    assert data["claim_boundaries"]["GBIF_LIVE_INTEGRATION"] is False
    assert data["claim_boundaries"]["OS_PLATFORM_020_TOUCHED"] is False
    assert data["closeout_assessment"]["OS_PLATFORM_020_NOT_COMPLETE"] is True
    assert data["closeout_assessment"]["targets_remaining_validation_open"] == []
    assert set(data["closeout_assessment"]["targets_digital_implementation_complete"]) == TARGET_IDS
    x = data["closeout_validation"]["cross_checks"]
    assert x["complete_delta"] == 15
    assert x["impl_open_delta"] == 15
    assert x["validation_open_unchanged"] is True
    assert x["next_val_only_020"] is True
    ind = data["closeout_validation"]["independent_fields"]
    assert ind["IMPLEMENTED_AND_VALIDATED_15"] is True
    assert ind["PARTIAL_false"] is True
    assert ind["ACTUAL_PRODUCT_BROWSER_E2E_true"] is True
    assert ind["PYTHON_PIPELINE_EXECUTED_true"] is True
    assert ind["AUTHENTIC_EXTERNAL_false"] is True
    assert ind["UNCONDITIONAL_TRUE_0"] is True
    assert ind["provenance_trees_identical"] is True
    assert ind["BEHAVIORAL_COUNT_GE_22"] is True


def test_provenance_binding():
    root = Path(__file__).resolve().parents[2]
    prov = json.loads(
        (root / "artifacts/engineering_wave008_closeout/PROVENANCE_BINDING_RESULT.json").read_text(
            encoding="utf-8"
        )
    )
    assert prov["ENGINEERING_WAVE_008_PROVENANCE_BINDING"] == "PASS"
    assert prov["archive_pr"] == 35
    assert prov["archive_final_head"] == "0a8089ad50df36a738743e358dcc039f97a004cb"
    assert prov["archive_merge_sha"] == "069243c365552f00707650e9d81a8046ba3075d8"
    assert prov["archive_tested_tree"] == prov["archive_accepted_tree"] == "3b68a460365bb7e1773da1423e8c89d9986a6a36"
    assert prov["archive_tree_equivalence"] is True
    assert prov["field_kit_109_head"] == "8fa2b466bbb881d472268215693dd32a54411325"
    assert prov["field_kit_109_merge_sha"] == "2999004793a593009c38f130e57946f317db27e1"
    assert prov["binding"]["trees_identical"] is True
    assert prov["generation_sha_notes"]["BLOCKED_STALE_EVIDENCE"] is False
    assert prov["authoritative_ci"]["run_id"] == 32447982081
    assert prov["authoritative_ci"]["artifact_id"] == 9434750630
    assert prov["authoritative_ci"]["expired"] is False


def test_closeout_result_and_queues():
    root = Path(__file__).resolve().parents[2]
    result = json.loads(
        (root / "artifacts/engineering_wave008_closeout/CLOSEOUT_RESULT.json").read_text(encoding="utf-8")
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
    assert result["ENGINEERING_WAVE_008_TARGETED_CLOSEOUT_VALIDATION_PASS"] is True
    assert result["ENGINEERING_WAVE_008_CLOSEOUT"] == "PASS"
    assert result["CURSOR_MERGED_NOTHING"] is True
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
    # Prior wave history preserved; Wave008 appended
    assert "ENGINEERING_WAVE_001_TARGETED_CLOSEOUT" in baseline
    assert "ENGINEERING_WAVE_007_TARGETED_CLOSEOUT" in baseline
    assert "ENGINEERING_WAVE_008_TARGETED_CLOSEOUT" in baseline
    assert "wave001_targeted_closeout" in reg
    assert "wave007_targeted_closeout" in reg
    assert "wave008_targeted_closeout" in reg
    assert baseline["AUTHENTIC_EXTERNAL_SOURCE_SNAPSHOTS_PRESENT"] is False
    assert baseline["SOURCE_VERIFIED_EXTERNAL_RECORD_COUNT"] == 0
