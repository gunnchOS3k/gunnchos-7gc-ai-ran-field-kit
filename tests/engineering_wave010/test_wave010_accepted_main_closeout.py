"""Validate Wave 010 accepted-main closeout for GAME-PP-001..015."""
from __future__ import annotations

import json
from pathlib import Path

TARGET_IDS = [f"GAME-PP-{i:03d}" for i in range(1, 16)]
PP22_FINAL_HEAD = "7e64e40c5b960678bfe9e5991db26717fc32f743"
PP22_MERGE = "5950ea791ed37addb26c80be84a64c20f589f4b4"
PP_TREE = "475cb9c14f7a842ec251cb37064ffdbf5cd700ee"
TOKEN = "ENGINEERING_WAVE_010_ACCEPTED_MAIN_CLOSEOUT_PASS"


def _root() -> Path:
    return Path(__file__).resolve().parents[2]


def _load(rel: str):
    return json.loads((_root() / rel).read_text(encoding="utf-8"))


def test_closeout_token_and_provenance():
    result = _load("artifacts/engineering_wave010_closeout/WAVE010_ACCEPTED_MAIN_CLOSEOUT.json")
    prov = _load("artifacts/engineering_wave010_closeout/WAVE010_ACCEPTED_MAIN_PROVENANCE.json")
    assert result["WAVE010_ACCEPTED_MAIN_CLOSEOUT"] == "PASS"
    assert result["token"] == TOKEN
    assert result["ENGINEERING_WAVE_010_ACCEPTED_MAIN_CLOSEOUT_PASS"] is True
    assert result["CURSOR_MERGED_NOTHING"] is True
    assert result["GAME_PP_ROWS_CLOSED"] == 15
    assert result["TARGETED_ROWS_CHANGED"] == 15
    assert result["UNTARGETED_ROWS_CHANGED"] == 0
    assert result["UNRELATED_IMPLEMENTATION_QUEUE_ROWS_CHANGED"] == 0
    assert result["VALIDATION_QUEUE_ROWS_CHANGED"] == 0
    assert prov["PP22_FINAL_HEAD_SHA"] == PP22_FINAL_HEAD
    assert prov["PP22_MERGE_SHA"] == PP22_MERGE
    assert prov["PEDESTRIAN_ACCEPTED_MAIN_TREE"] == PP_TREE
    assert prov["TREE_EQUIVALENCE_STATUS"] == "TREE_EQUIVALENT_TO_PR22_FINAL_HEAD"
    assert prov["authoritative_premerge_ci"]["run_id"] == 32546701777
    assert prov["authoritative_premerge_ci"]["artifact_id"] == 9468808889
    assert (
        prov["authoritative_premerge_ci"]["digest"]
        == "sha256:1bd73dfad87bec4cf4babb85b8c691b436fa0317c1acda28d8d93a7352f5cadf"
    )
    assert prov["authoritative_premerge_ci"]["head_sha"] == PP22_FINAL_HEAD
    assert prov["binding"]["trees_identical"] is True


def test_accepted_main_reproduction_gates():
    result = _load("artifacts/engineering_wave010_closeout/WAVE010_ACCEPTED_MAIN_CLOSEOUT.json")
    wave = _load(
        "artifacts/engineering_wave010_closeout/_accepted_main_reproduction/WAVE010_RESULT.json"
    )
    mastery = _load(
        "artifacts/engineering_wave010_closeout/_accepted_main_reproduction/MASTERY_RESULT.json"
    )
    mut = _load(
        "artifacts/engineering_wave010_closeout/_accepted_main_reproduction/MUTATION_RESULT.json"
    )
    assert wave["ENGINEERING_WAVE_010"] == "PASS"
    assert wave["IMPLEMENTED_COUNT"] == 15
    assert mastery["ALL_10_FINISH"] is True
    assert mastery["pairwise_advanced_faster"] >= 4
    assert mastery["BASIC_HANDICAP_PRESENT"] is False
    assert mastery["FRAME_COUNT_SKILL_TIMING"] is False
    assert mut["WAVE010_MUTATIONS_ATTEMPTED"] >= 11
    assert mut["WAVE010_MUTATIONS_KILLED"] == mut["WAVE010_MUTATIONS_ATTEMPTED"]
    assert mut["WAVE010_INVALID_MUTATIONS"] == 0
    assert wave["NEW_S0"] == 0 and wave["NEW_S1"] == 0
    assert all(result["accepted_main_reproduction"]["gates"].values())


def test_per_row_matrix_independent():
    matrix = _load("artifacts/engineering_wave010_closeout/GAME_PP_CLOSEOUT_MATRIX.json")
    assert matrix["rows_closed"] == 15
    assert matrix["BLANKET_GAME_PP_ASSIGNMENT"] is False
    for rid in TARGET_IDS:
        row = matrix["rows"][rid]
        assert row["pre_state"] == "DIGITAL_IMPLEMENTATION_OPEN"
        assert row["post_state"] == "DIGITAL_IMPLEMENTATION_COMPLETE"
        assert row["accepted_main_sha"] == PP22_MERGE
        assert row["BLANKET"] is False
        assert row["production_paths"]
        assert row["runtime_evidence"]
        assert row["behavioral_evidence"]
        assert row["mutation_evidence"]


def test_register_and_queues():
    reg = _load("program/digital_ecosystem_baseline_v2/MASTER_COMPLETION_REGISTER.json")
    impl = _load("program/digital_ecosystem_baseline_v2/NEXT_DIGITAL_IMPLEMENTATION_WORK.json")
    val = _load("program/digital_ecosystem_baseline_v2/NEXT_DIGITAL_VALIDATION_WORK.json")
    pending = _load("program/digital_ecosystem_baseline_v2/NON_DIGITAL_PENDING_REGISTER.json")
    diff = _load("artifacts/engineering_wave010_closeout/TARGETED_ROW_DIFF.json")
    totals = reg["totals"]
    assert totals["ATOMIC_TOTAL"] == 419
    # Wave010 closed to 126/36; later waves may raise COMPLETE / lower OPEN.
    assert totals["DIGITAL_IMPLEMENTATION_COMPLETE"] >= 126
    assert totals["DIGITAL_IMPLEMENTATION_OPEN"] <= 36
    assert totals["DIGITAL_VALIDATION_OPEN"] == 0
    assert totals["EVIDENCE_MAPPING_OPEN"] == 0
    assert (
        totals["DIGITAL_IMPLEMENTATION_COMPLETE"]
        + totals["DIGITAL_IMPLEMENTATION_OPEN"]
        + totals["DIGITAL_VALIDATION_OPEN"]
        == 162
    )
    assert impl["total_open"] == totals["DIGITAL_IMPLEMENTATION_OPEN"]
    assert len(impl["all_items"]) == totals["DIGITAL_IMPLEMENTATION_OPEN"]
    assert val["total_open"] == 0
    assert val["all_items"] == []
    assert pending["total_pending_rows"] == 257
    assert diff["UNTARGETED_ROWS_CHANGED"] == 0
    assert diff["TARGETED_ROWS_CHANGED"] == 15
    for rid in TARGET_IDS:
        row = next(r for r in reg["requirements"] if r["requirement_id"] == rid)
        assert row["work_state"] == "DIGITAL_IMPLEMENTATION_COMPLETE"
        assert row["implementation_state"] == "IMPLEMENTED"
        assert row["verification_state"] == "INDEPENDENTLY_VERIFIED_DIGITAL"
        assert rid not in {i["requirement_id"] for i in impl["all_items"]}


def test_claim_boundaries_and_code_health():
    claims = _load("artifacts/engineering_wave010_closeout/CLAIM_BOUNDARIES.json")
    code = _load("artifacts/engineering_wave010_closeout/CODE_INTEGRITY_RECHECK.json")
    cb = claims["claim_boundaries"]
    assert claims["ENGINEERING_WAVE_010_CLAIM_BOUNDARIES"] == "PASS"
    for k in (
        "HUMAN_PLAYTEST_COMPLETE",
        "HUMAN_FUN_VALIDATED",
        "ESPORTS_BALANCE_VALIDATED",
        "PHYSICAL_ANDROID_VALIDATED",
        "CONSOLE_CERTIFIED",
        "STORE_APPROVED",
        "SHIPPING_PRODUCT",
    ):
        assert cb[k] is False
    assert code["CURRENT_OPEN_S0"] == 0
    assert code["CURRENT_OPEN_S1"] == 0
    assert code["NEW_S0"] == 0
    assert code["NEW_S1"] == 0
    assert code["S2_FINDINGS_PRESERVED"] is True
    assert "7gc-digital-twin" in code["S2_MUTATION_VALIDATION_INCOMPLETE_REPOS"]
    assert "readygary-6g-beam-selection" in code["S2_MUTATION_VALIDATION_INCOMPLETE_REPOS"]
    assert "gunnchos-emergent-service-intent-protocols" in code["S2_MUTATION_VALIDATION_INCOMPLETE_REPOS"]


def test_token_string_present():
    result = _load("artifacts/engineering_wave010_closeout/WAVE010_ACCEPTED_MAIN_CLOSEOUT.json")
    text = json.dumps(result)
    assert TOKEN in text
