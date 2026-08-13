"""Pinned IMT-2030 Rel-20/21 tracker — no standardized 6G claim."""
from __future__ import annotations

from pathlib import Path

from standards.harnesses.imt2030_rel20_rel21_tracker import (
    CARRIER_ACCEPTED,
    STANDARDIZED_6G,
    evaluate,
)


def test_tracker_pass_without_6g_or_carrier_claim(tmp_path: Path):
    report = evaluate(tmp_path)
    assert report["ok"] is True
    assert report["STANDARDIZED_6G"] is False
    assert report["CARRIER_ACCEPTED"] is False
    assert report["GATE_8_PASS"] is False
    assert report["rel21"]["status"] == "TRACKER_ONLY"
    assert report["rel21"]["freeze_claimed"] is False
    assert report["rm520n_ntn_claimed"] is False
    assert report["rm520n_6g_claimed"] is False
    assert STANDARDIZED_6G is False
    assert CARRIER_ACCEPTED is False
    assert (tmp_path / "IMT2030_REL20_REL21_TRACKER.json").is_file()
    assert "ubiquitous_connectivity" in report["usage_scenarios"]
