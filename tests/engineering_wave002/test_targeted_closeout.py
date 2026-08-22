"""Validate Wave 002 targeted closeout artifact and register freeze."""
from __future__ import annotations

import json
from pathlib import Path


TARGET_IDS = {
    "SYS-MISSION-006",
    "OS-PLATFORM-001",
    "OS-PLATFORM-002",
    "OS-PLATFORM-003",
    "OS-PLATFORM-004",
    "OS-PLATFORM-005",
    "OS-PLATFORM-006",
    "OS-PLATFORM-007",
    "OS-CONTINUITY-002",
    "OS-CONTINUITY-003",
    "OS-CONTINUITY-004",
    "OS-CONTINUITY-005",
    "OS-CONTINUITY-006",
    "OS-CONTINUITY-007",
}


def test_targeted_row_diff_freeze():
    root = Path(__file__).resolve().parents[2]
    diff_path = root / "artifacts/engineering_wave002_closeout/TARGETED_ROW_DIFF.json"
    data = json.loads(diff_path.read_text(encoding="utf-8"))
    assert data["untargeted_rows_changed"] == 0
    assert data["unexpected_changed_ids"] == []
    assert set(data["target_ids"]) == TARGET_IDS
    assert data["closeout_validation"]["ENGINEERING_WAVE_002_TARGETED_CLOSEOUT_VALIDATION_PASS"] is True
    assert data["pixel_boundaries"]["HUMAN_E6"] is False
    assert data["pixel_boundaries"]["PHYSICAL_VALIDATION"] is False


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
    totals = reg["totals"]
    assert len(impl["all_items"]) == totals["DIGITAL_IMPLEMENTATION_OPEN"]
    assert impl["total_open"] == totals["DIGITAL_IMPLEMENTATION_OPEN"]
    assert totals["DIGITAL_IMPLEMENTATION_OPEN"] <= 51
    assert totals["DIGITAL_IMPLEMENTATION_COMPLETE"] + totals["DIGITAL_IMPLEMENTATION_OPEN"] + totals["DIGITAL_VALIDATION_OPEN"] == 162
