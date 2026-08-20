"""Validate Wave 003 targeted closeout artifact and register freeze."""
from __future__ import annotations

import json
from pathlib import Path


TARGET_IDS = {
    "AI-LOCAL-001",
    "AI-LOCAL-002",
    "AI-LOCAL-003",
    "AI-LOCAL-005",
    "AI-LOCAL-006",
    "AI-LOCAL-007",
    "AI-LOCAL-008",
    "AI-LOCAL-009",
    "AI-LOCAL-011",
    "AI-GOV-001",
    "AI-GOV-003",
    "AI-GOV-004",
    "AI-GOV-005",
    "AI-GOV-006",
    "AI-GOV-007",
    "AI-GOV-008",
    "AI-GOV-010",
    "AI-GOV-011",
    "AI-GOV-012",
}


def test_targeted_row_diff_freeze():
    root = Path(__file__).resolve().parents[2]
    diff_path = root / "artifacts/engineering_wave003_closeout/TARGETED_ROW_DIFF.json"
    data = json.loads(diff_path.read_text(encoding="utf-8"))
    assert data["untargeted_rows_changed"] == 0
    assert data["unexpected_changed_ids"] == []
    assert set(data["target_ids"]) == TARGET_IDS
    assert data["closeout_validation"]["ENGINEERING_WAVE_003_TARGETED_CLOSEOUT_VALIDATION_PASS"] is True
    assert data["claim_boundaries"]["GENERAL_ASR"] is False
    assert data["claim_boundaries"]["GENERAL_VLM"] is False
    assert data["claim_boundaries"]["GENERAL_MT"] is False
    assert data["claim_boundaries"]["GENERAL_BIAS_AUDIT"] is False
    assert data["claim_boundaries"]["HUMAN_E6"] is False
    assert data["claim_boundaries"]["HUMAN_ACCESSIBILITY_VALIDATED"] is False
    assert data["claim_boundaries"]["NOT_TRAINED_GAME_PLAYING_AGENT"] is True
    assert data["claim_boundaries"]["VALIDATION_IMPORTS_REQUIREMENT_PROOF"] is False
    assert data["closeout_assessment"]["independent_digital_reproduction"] == "PASS"


def test_register_counts_arithmetic():
    root = Path(__file__).resolve().parents[2]
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
    totals = reg["totals"]
    assert len(impl["all_items"]) == totals["DIGITAL_IMPLEMENTATION_OPEN"]
    assert impl["total_open"] == totals["DIGITAL_IMPLEMENTATION_OPEN"]
    assert totals["DIGITAL_IMPLEMENTATION_OPEN"] == 98
    assert len(val["all_items"]) == totals["DIGITAL_VALIDATION_OPEN"]
    assert val["total_open"] == totals["DIGITAL_VALIDATION_OPEN"]
    assert totals["DIGITAL_IMPLEMENTATION_COMPLETE"] == 63
    assert totals["DIGITAL_VALIDATION_OPEN"] == 1
