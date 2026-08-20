"""Validate Wave003 aggregate artifact without mutating baseline counts."""
from __future__ import annotations

import json
from pathlib import Path


def test_wave003_aggregate_integrity_repair_metadata():
    root = Path(__file__).resolve().parents[2]
    agg_path = root / "artifacts/engineering_wave003/ENGINEERING_WAVE003_AGGREGATE.json"
    wave_path = root / "artifacts/engineering_wave003/WAVE003_RESULT.json"
    repro_path = root / "artifacts/engineering_wave003/INDEPENDENT_REPRODUCTION.json"

    agg = json.loads(agg_path.read_text(encoding="utf-8"))
    wave = json.loads(wave_path.read_text(encoding="utf-8"))
    repro = json.loads(repro_path.read_text(encoding="utf-8"))

    assert agg["DO_NOT_MERGE_UNTIL_GUNNCHAI_WAVE003_INTEGRITY_REPAIR_ACCEPTED"] is True
    assert agg["BASELINE_COUNTS_UPDATED"] is False
    assert agg["historical_gunnchai_pr"]["number"] == 44
    assert agg["authoritative_repair_pr"]["head_sha"] == "5b924a30e240495a9f3325fbd14cc3d3fd1abc4c"
    assert agg["INDEPENDENT_DIGITAL_REPRODUCTION"] == "PASS"
    assert agg["VALIDATED"] == 19
    assert len(agg["requirement_classification"]) == 19
    assert all(v == "VALIDATED" for v in agg["requirement_classification"].values())

    assert wave["independentDigitalReproduction"] == "PASS"
    assert wave["releaseComplete"] is True
    assert wave["branch"] == "eng/wave003-integrity-repair"
    assert repro["result"] == "PASS"
    assert repro["perRequirementStateMatch"] is True
    assert repro["unexpected_differences"] == []

    assert agg["CURSOR_MERGED_NOTHING"] is True
