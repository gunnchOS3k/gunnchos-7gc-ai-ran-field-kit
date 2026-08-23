"""Validate Wave 014 accepted-main closeout — capability ledger only (no row closures)."""
from __future__ import annotations

import json
from pathlib import Path

PR84_FINAL_HEAD = "aa28654ff33cea28e79bf7d3941dfc3c81db50cc"
PR84_MERGE_SHA = "706aba63274c9b563dfc34e76502d78a7cac19a9"
ANIME_TREE = "faa3ff384e74d715ff2159ccf3b182452a409d7f"
FIELD_KIT_START = "12f4416fee08d266b4a34fd43198094ba42ef6d1"
TOKEN = "ENGINEERING_WAVE_014_ACCEPTED_MAIN_CLOSEOUT_PASS"
IMPL_OPEN_IDS = [
    "SYS-MISSION-006",
    "DEV-STUDENT-001",
    "DEV-STUDENT-003",
    "DEV-STUDENT-004",
    "DEV-STUDENT-005",
    "DEV-STUDENT-006",
    "DEV-STUDENT-009",
    "DEV-STUDENT-010",
    "DEV-STUDENT-012",
    "DEV-DSXL-001",
    "DEV-HANDHELD-001",
    "RING-INPUT-001",
    "RING-INPUT-037",
    "RING-RELIAB-016",
    "GATE-0-002",
    "GATE-0-003",
    "GATE-0-005",
    "GATE-3-001",
    "GATE-3-002",
    "GATE-3-003",
    "GATE-3-004",
    "GATE-3-005",
    "GATE-3-006",
    "GATE-3-007",
    "GATE-5-005",
    "GATE-7-006",
]


def _root() -> Path:
    return Path(__file__).resolve().parents[2]


def _load(rel: str):
    return json.loads((_root() / rel).read_text(encoding="utf-8"))


def test_closeout_token_and_provenance():
    result = _load("artifacts/engineering_wave014_closeout/WAVE014_ACCEPTED_MAIN_CLOSEOUT.json")
    prov = _load("artifacts/engineering_wave014_closeout/WAVE014_ACCEPTED_MAIN_PROVENANCE.json")
    assert result["WAVE014_ACCEPTED_MAIN_CLOSEOUT"] == "PASS"
    assert result["token"] == TOKEN
    assert result["ENGINEERING_WAVE_014_ACCEPTED_MAIN_CLOSEOUT_PASS"] is True
    assert result["CURSOR_MERGED_NOTHING"] is True
    assert result["FORCED_ROW_CLOSURES"] == 0
    assert result["TARGETED_ROWS_CHANGED"] == 0
    assert result["UNTARGETED_ROWS_CHANGED"] == 0
    assert prov["PR84_FINAL_HEAD_SHA"] == PR84_FINAL_HEAD
    assert prov["PR84_MERGE_SHA"] == PR84_MERGE_SHA
    assert prov["ANIME_ACCEPTED_MAIN_TREE"] == ANIME_TREE
    assert prov["FIELD_KIT_START_SHA"] == FIELD_KIT_START
    assert prov["TREE_EQUIVALENCE_STATUS"] == "TREE_EQUIVALENT_TO_PR84_FINAL_HEAD"
    assert prov["authoritative_premerge_ci"]["run_id"] == 32604653603
    assert prov["authoritative_premerge_ci"]["artifact_id"] == 9483927490
    assert prov["binding"]["trees_identical"] is True


def test_accepted_main_reproduction_gates():
    result = _load("artifacts/engineering_wave014_closeout/WAVE014_ACCEPTED_MAIN_CLOSEOUT.json")
    wave = _load(
        "artifacts/engineering_wave014_closeout/_accepted_main_reproduction/WAVE014_RESULT.json"
    )
    assert wave["ENGINEERING_WAVE_014"] == "PASS"
    assert wave["PROCEDURAL_CHARACTER_RUNTIME_PASS"] is True
    assert wave["PROCEDURAL_RUNTIME_ANIMATION_PASS"] is True
    assert wave["FIGHTERS_VISIBLE_SKELETON_TESTED"] == 7
    assert wave["VISIBLE_SKELETAL_TRANSFORM_FAILURES"] == 0
    assert wave["CURRENT_MODEL_SOURCE"] == "PROCEDURAL_PRODUCTION_PROXY"
    assert wave["CURRENT_ANIMATION_SOURCE"] == "PROCEDURAL_RUNTIME_ANIMATION"
    assert wave["FINAL_CHARACTER_ART_PASS"] is False
    assert wave["PHYSICAL_PIXEL6A_VALIDATED"] is False
    assert wave["REAL_USER_MOTION_LIBRARY_PRESENT"] is False
    assert wave["NEW_S0"] == 0 and wave["NEW_S1"] == 0
    repro = result["accepted_main_reproduction"]
    assert repro["FIGHTERS_VISIBLE_PROCEDURAL_MODEL_TESTED"] >= 7
    assert repro["BATTLESCENE_VISIBLE_RUNTIME_E2E"] == "PASS"
    assert all(result["accepted_main_reproduction"]["gates"].values())


def test_capability_ledger_and_no_row_closure():
    ledger = _load("artifacts/engineering_wave014_closeout/WAVE012_014_CAPABILITY_LEDGER.json")
    recon = _load("artifacts/engineering_wave014_closeout/BASELINE_ROW_RECONCILIATION.json")
    assert ledger["atomic_row_closures"] == 0
    assert len(ledger["entries"]) == 7
    ids = {e["capability_id"] for e in ledger["entries"]}
    assert ids == {
        "WAVE012_ZERO_COST_ART_PIPELINE",
        "WAVE013B_NOTES_DRIVEN_CHOREOGRAPHY",
        "WAVE013B_USER_MOTION_CONTRIBUTION",
        "WAVE014_PROCEDURAL_ROSTER_MODELS",
        "WAVE014_VISIBLE_SKELETAL_ANIMATION",
        "WAVE014_RUNTIME_GAME_JUICE",
        "WAVE014_CANONICAL_BATTLESCENE_PRESENTATION",
    }
    for entry in ledger["entries"]:
        assert entry["verification_level"] in (
            "DIGITALLY_EXECUTED",
            "DIGITALLY_REPRODUCED",
            "INDEPENDENTLY_VERIFIED_DIGITAL",
        )
        assert entry["accepted_main_sha"] == PR84_MERGE_SHA
    assert recon["FORCED_ROW_CLOSURES"] == 0
    assert recon["rows_closed"] == 0
    assert recon["rows_reviewed"] == 26
    assert {r["requirement_id"] for r in recon["rows"]} == set(IMPL_OPEN_IDS)
    assert all(r["closure_decision"] == "NO_CLOSE" for r in recon["rows"])


def test_register_and_queues_unchanged():
    reg = _load("program/digital_ecosystem_baseline_v2/MASTER_COMPLETION_REGISTER.json")
    impl = _load("program/digital_ecosystem_baseline_v2/NEXT_DIGITAL_IMPLEMENTATION_WORK.json")
    val = _load("program/digital_ecosystem_baseline_v2/NEXT_DIGITAL_VALIDATION_WORK.json")
    recheck = _load("artifacts/engineering_wave014_closeout/NEXT_WORK_QUEUE_RECHECK.json")
    totals = reg["totals"]
    assert totals["ATOMIC_TOTAL"] == 419
    assert totals["DIGITAL_IMPLEMENTATION_COMPLETE"] == 136
    assert totals["DIGITAL_IMPLEMENTATION_OPEN"] == 26
    assert totals["DIGITAL_VALIDATION_OPEN"] == 0
    assert totals["EVIDENCE_MAPPING_OPEN"] == 0
    assert impl["total_open"] == 26
    assert len(impl["all_items"]) == 26
    assert val["total_open"] == 0
    assert val["all_items"] == []
    assert recheck["baseline_counts_unchanged"] is True
    assert recheck["FORCED_ROW_CLOSURES"] == 0
    assert recheck["register_files_modified"] is False


def test_physical_validation_pointer():
    physical = _load("artifacts/engineering_wave014_closeout/PHYSICAL_ACTION_REGISTER.json")
    assert physical["NEXT_PHYSICAL_VALIDATION"] == "ANIME_AGGRESSORS_PIXEL6A"
    assert "PIXEL6A_WAVE014_TEST_RUNBOOK.md" in physical["runbook"]
    action = physical["actions"][0]
    assert action["action_id"] == "ANIME-AA-PIXEL6A-VISUAL-RUNTIME"
    assert action["status"] == "PHYSICAL_PENDING"
    assert action["digital_preparation"] == "COMPLETE"


def test_claim_boundaries_and_code_health():
    claims = _load("artifacts/engineering_wave014_closeout/CLAIM_BOUNDARIES.json")
    code = _load("artifacts/engineering_wave014_closeout/CODE_INTEGRITY_RECHECK.json")
    cb = claims["claim_boundaries"]
    assert claims["ENGINEERING_WAVE_014_CLAIM_BOUNDARIES"] == "PASS"
    assert cb["PHYSICAL_PIXEL6A_VALIDATED"] is False
    assert cb["FINAL_CHARACTER_ART_PASS"] is False
    assert cb["BASELINE_COUNTS_UPDATED_ON_WAVE_EVIDENCE"] is False
    assert code["CURRENT_OPEN_S0"] == 0
    assert code["CURRENT_OPEN_S1"] == 0
    assert code["S2_FINDINGS_PRESERVED"] is True


def test_token_string_present():
    result = _load("artifacts/engineering_wave014_closeout/WAVE014_ACCEPTED_MAIN_CLOSEOUT.json")
    text = json.dumps(result)
    assert TOKEN in text
