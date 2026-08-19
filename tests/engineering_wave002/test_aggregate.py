"""Validate Wave 002 aggregate artifact without mutating baseline counts."""
from __future__ import annotations

import json
from pathlib import Path


def test_aggregate_marker_and_counts():
    root = Path(__file__).resolve().parents[2]
    path = root / "artifacts/engineering_wave002/ENGINEERING_WAVE002_AGGREGATE.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["DO_NOT_MERGE_UNTIL_DEPENDENCY_PRS_ACCEPTED"] is True
    assert data["DO_NOT_UPDATE_BASELINE_COUNTS"] is True
    assert data["impl_open_count_post_pr92"] == 123
    assert data["ENGINEERING_WAVE_002"] == "PARTIAL"
    assert len(data["requirement_classification"]) == 14
    assert data["CURSOR_MERGED_NOTHING"] is True
