"""Validate Wave 007 targeted closeout artifact and register freeze."""
from __future__ import annotations

import json
from pathlib import Path


TARGET_IDS = {
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
}


def test_targeted_row_diff_freeze():
    root = Path(__file__).resolve().parents[2]
    diff_path = root / "artifacts/engineering_wave007_closeout/TARGETED_ROW_DIFF.json"
    data = json.loads(diff_path.read_text(encoding="utf-8"))
    assert data["untargeted_rows_changed"] == 0
    assert data["unexpected_changed_ids"] == []
    assert set(data["target_ids"]) == TARGET_IDS
    assert data["OS_PLATFORM_020_CHANGED"] is False
    assert data["VOCAL_PROMPT_TIMING_MODE"] == "VOCAL_PROMPT_TIMING_MODE"
    assert data["SERVER_RESTART_ROOM_PERSISTENCE"] is False
    assert data["closeout_validation"]["ENGINEERING_WAVE_007_TARGETED_CLOSEOUT_VALIDATION_PASS"] is True
    assert data["claim_boundaries"]["LINK_EQUALS_RIP_PERMISSION"] is False
    assert data["claim_boundaries"]["GENERAL_VOCAL_RECOGNITION"] is False
    assert data["claim_boundaries"]["MICROPHONE_PITCH_ANALYSIS"] is False
    assert data["claim_boundaries"]["SPOTIFY_PLAYBACK_INTEGRATION"] is False
    assert data["claim_boundaries"]["OS_PLATFORM_020_TOUCHED"] is False
    assert data["closeout_assessment"]["OS_PLATFORM_020_NOT_COMPLETE"] is True
    assert data["closeout_assessment"]["targets_remaining_validation_open"] == []
    assert set(data["closeout_assessment"]["targets_digital_implementation_complete"]) == TARGET_IDS
    x = data["closeout_validation"]["cross_checks"]
    assert x["complete_delta"] == 10
    assert x["impl_open_delta"] == 10
    assert x["validation_open_unchanged"] is True
    assert x["next_val_only_020"] is True
    # Independent fields — not a single wave007_ok bit
    ind = data["closeout_validation"]["independent_fields"]
    assert ind["IMPLEMENTED_AND_VALIDATED_10"] is True
    assert ind["PARTIAL_false"] is True
    assert ind["PLAYWRIGHT_MANDATORY_true"] is True
    assert ind["PLAYWRIGHT_SKIPPED_false"] is True
    assert ind["UNCONDITIONAL_TRUE_0"] is True
    assert ind["provenance_trees_identical"] is True


def test_provenance_binding():
    root = Path(__file__).resolve().parents[2]
    prov = json.loads(
        (root / "artifacts/engineering_wave007_closeout/PROVENANCE_BINDING_RESULT.json").read_text(
            encoding="utf-8"
        )
    )
    assert prov["ENGINEERING_WAVE_007_PROVENANCE_BINDING"] == "PASS"
    b = prov["binding"]
    assert b["PR_HEAD_TREE"] == b["SYNTHETIC_MERGE_TREE"] == b["ACCEPTED_MERGE_TREE"]
    assert b["trees_identical"] is True
    assert prov["generation_sha_notes"]["BLOCKED_STALE_EVIDENCE"] is False
    assert prov["authoritative_ci"]["run_id"] == 32437290296
    assert prov["authoritative_ci"]["artifact_id"] == 9431213525
    assert prov["authoritative_ci"]["expired"] is False


def test_closeout_result_and_queues():
    root = Path(__file__).resolve().parents[2]
    result = json.loads(
        (root / "artifacts/engineering_wave007_closeout/CLOSEOUT_RESULT.json").read_text(encoding="utf-8")
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
    assert result["ENGINEERING_WAVE_007_TARGETED_CLOSEOUT_VALIDATION_PASS"] is True
    assert result["ENGINEERING_WAVE_007_CLOSEOUT"] == "COMPLETE"
    assert result["CURSOR_MERGED_NOTHING"] is True
    assert result["VOCAL_PROMPT_TIMING_MODE"] == "VOCAL_PROMPT_TIMING_MODE"
    assert result["SERVER_RESTART_ROOM_PERSISTENCE"] is False
    assert result["OS_PLATFORM_020"]["validation_state"] == "DIGITAL_VALIDATION_OPEN"
    assert result["OS_PLATFORM_020"]["implementation_present"] is True
    assert result["OS_PLATFORM_020"]["blocker"] == "SANDBOX_ENFORCEMENT_ENVIRONMENT"
    assert result["OS_PLATFORM_020"]["OS_PLATFORM_020_CHANGED"] is False
    assert result["OS_PLATFORM_020"]["NOT_MARKED_COMPLETE"] is True
    assert totals["DIGITAL_IMPLEMENTATION_COMPLETE"] == 95
    assert totals["DIGITAL_IMPLEMENTATION_OPEN"] == 66
    assert totals["DIGITAL_VALIDATION_OPEN"] == 1
    assert totals["EVIDENCE_MAPPING_OPEN"] == 0
    assert result["post_closeout_baseline"]["DIGITAL_CONTROLLABLE_POOL"] == 162
    assert len(impl["all_items"]) == totals["DIGITAL_IMPLEMENTATION_OPEN"]
    assert impl["total_open"] == totals["DIGITAL_IMPLEMENTATION_OPEN"]
    assert len(val["all_items"]) == 1
    assert val["total_open"] == 1
    assert val["all_items"][0]["requirement_id"] == "OS-PLATFORM-020"
    assert not any(i["requirement_id"] in TARGET_IDS for i in impl["all_items"])
    row020 = next(r for r in reg["requirements"] if r["requirement_id"] == "OS-PLATFORM-020")
    assert row020["work_state"] == "DIGITAL_VALIDATION_OPEN"
    assert row020["implementation_state"] == "IMPLEMENTED"
    for rid in TARGET_IDS:
        row = next(r for r in reg["requirements"] if r["requirement_id"] == rid)
        assert row["work_state"] == "DIGITAL_IMPLEMENTATION_COMPLETE"
    # Wave001–006 history preserved; Wave007 appended
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
