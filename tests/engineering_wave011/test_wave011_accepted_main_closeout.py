"""Validate Wave 011 accepted-main closeout for GAME-AA-001..010."""
from __future__ import annotations

import json
from pathlib import Path

TARGET_IDS = [f"GAME-AA-{i:03d}" for i in range(1, 11)]
PR81_FINAL_HEAD = "9e2ab6a264e2e74ba0db0a203f51d21ad587502d"
PR81_MERGE = "3b01c3d3473ec5372c5c1e3126305488dc26a08a"
ANIME_TREE = "78e5d924bd61ddbebe8e142275f3dc562e62b199"
TOKEN = "ENGINEERING_WAVE_011_ACCEPTED_MAIN_CLOSEOUT_PASS"


def _root() -> Path:
    return Path(__file__).resolve().parents[2]


def _load(rel: str):
    return json.loads((_root() / rel).read_text(encoding="utf-8"))


def test_closeout_token_and_provenance():
    result = _load("artifacts/engineering_wave011_closeout/WAVE011_ACCEPTED_MAIN_CLOSEOUT.json")
    prov = _load("artifacts/engineering_wave011_closeout/WAVE011_ACCEPTED_MAIN_PROVENANCE.json")
    assert result["WAVE011_ACCEPTED_MAIN_CLOSEOUT"] == "PASS"
    assert result["token"] == TOKEN
    assert result["ENGINEERING_WAVE_011_ACCEPTED_MAIN_CLOSEOUT_PASS"] is True
    assert result["CURSOR_MERGED_NOTHING"] is True
    assert result["GAME_AA_ROWS_CLOSED"] == 10
    assert result["TARGETED_ROWS_CHANGED"] == 10
    assert result["UNTARGETED_ROWS_CHANGED"] == 0
    assert result["UNRELATED_IMPLEMENTATION_QUEUE_ROWS_CHANGED"] == 0
    assert result["VALIDATION_QUEUE_ROWS_CHANGED"] == 0
    assert prov["PR81_FINAL_HEAD_SHA"] == PR81_FINAL_HEAD
    assert prov["PR81_MERGE_SHA"] == PR81_MERGE
    assert prov["ANIME_ACCEPTED_MAIN_TREE"] == ANIME_TREE
    assert prov["TREE_EQUIVALENCE_STATUS"] == "TREE_EQUIVALENT_TO_PR81_FINAL_HEAD"
    assert prov["authoritative_premerge_ci"]["run_id"] == 32585438949
    assert prov["authoritative_premerge_ci"]["artifact_id"] == 9478976330
    assert (
        prov["authoritative_premerge_ci"]["digest"]
        == "sha256:41247b4b21db62a298d4bc5987eccb79475c6648e7344b05db718eb4042298b4"
    )
    assert prov["authoritative_premerge_ci"]["head_sha"] == PR81_FINAL_HEAD
    assert prov["binding"]["trees_identical"] is True


def test_accepted_main_reproduction_gates():
    result = _load("artifacts/engineering_wave011_closeout/WAVE011_ACCEPTED_MAIN_CLOSEOUT.json")
    wave = _load(
        "artifacts/engineering_wave011_closeout/_accepted_main_reproduction/WAVE011_RESULT.json"
    )
    mut = _load(
        "artifacts/engineering_wave011_closeout/_accepted_main_reproduction/MUTATION_RESULT.json"
    )
    throws = _load(
        "artifacts/engineering_wave011_closeout/_accepted_main_reproduction/DIRECTIONAL_THROW_RUNTIME_RESULT.json"
    )
    assert wave["ENGINEERING_WAVE_011"] == "PASS"
    assert wave["IMPLEMENTED_COUNT"] == 10
    assert wave["runtime_gates"]["CANONICAL_BATTLE_SCENE_EXECUTED"] is True
    assert wave["runtime_gates"]["CANONICAL_TRAINING_SCENE_EXECUTED"] is True
    assert wave["runtime_gates"]["FIGHTERS_RUNTIME_MOVEMENT_TESTED"] == 7
    assert wave["runtime_gates"]["FIGHTERS_RUNTIME_IDENTITY_TESTED"] == 7
    assert throws["REAL_FOUR_DIRECTION_THROW_PATH"] is True
    assert mut["WAVE011_MUTATIONS_ATTEMPTED"] == 13
    assert mut["WAVE011_MUTATIONS_KILLED"] == 13
    assert mut["WAVE011_INVALID_MUTATIONS"] == 0
    assert wave["NEW_S0"] == 0 and wave["NEW_S1"] == 0
    assert wave["WEAK_PROXY_CLOSURE_RULES"] == 0
    assert all(result["accepted_main_reproduction"]["gates"].values())


def test_per_row_matrix_independent():
    matrix = _load("artifacts/engineering_wave011_closeout/GAME_AA_CLOSEOUT_MATRIX.json")
    assert matrix["rows_closed"] == 10
    assert matrix["BLANKET_GAME_AA_ASSIGNMENT"] is False
    for rid in TARGET_IDS:
        row = matrix["rows"][rid]
        assert row["pre_state"] == "DIGITAL_IMPLEMENTATION_OPEN"
        assert row["post_state"] == "DIGITAL_IMPLEMENTATION_COMPLETE"
        assert row["accepted_main_sha"] == PR81_MERGE
        assert row["BLANKET"] is False
        assert row["production_paths"]
        assert row["canonical_runtime_evidence"]
        assert row["behavioral_evidence"]
        assert row["mutation_evidence"]
        assert row["closeout_reason"]


def test_register_and_queues():
    reg = _load("program/digital_ecosystem_baseline_v2/MASTER_COMPLETION_REGISTER.json")
    impl = _load("program/digital_ecosystem_baseline_v2/NEXT_DIGITAL_IMPLEMENTATION_WORK.json")
    val = _load("program/digital_ecosystem_baseline_v2/NEXT_DIGITAL_VALIDATION_WORK.json")
    pending = _load("program/digital_ecosystem_baseline_v2/NON_DIGITAL_PENDING_REGISTER.json")
    diff = _load("artifacts/engineering_wave011_closeout/TARGETED_ROW_DIFF.json")
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
    assert pending["total_pending_rows"] == 257
    assert diff["UNTARGETED_ROWS_CHANGED"] == 0
    assert diff["TARGETED_ROWS_CHANGED"] == 10
    for rid in TARGET_IDS:
        row = next(r for r in reg["requirements"] if r["requirement_id"] == rid)
        assert row["work_state"] == "DIGITAL_IMPLEMENTATION_COMPLETE"
        assert row["implementation_state"] == "IMPLEMENTED"
        assert row["verification_state"] == "INDEPENDENTLY_VERIFIED_DIGITAL"
        assert rid not in {i["requirement_id"] for i in impl["all_items"]}
    # Non-GAME-AA digital rows unchanged in queue sense: no GAME-AA remain open except AA-011 physical
    aa_open = [i for i in impl["all_items"] if i["requirement_id"].startswith("GAME-AA-")]
    assert aa_open == []


def test_claim_boundaries_and_code_health():
    claims = _load("artifacts/engineering_wave011_closeout/CLAIM_BOUNDARIES.json")
    code = _load("artifacts/engineering_wave011_closeout/CODE_INTEGRITY_RECHECK.json")
    cb = claims["claim_boundaries"]
    assert claims["ENGINEERING_WAVE_011_CLAIM_BOUNDARIES"] == "PASS"
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
    result = _load("artifacts/engineering_wave011_closeout/WAVE011_ACCEPTED_MAIN_CLOSEOUT.json")
    text = json.dumps(result)
    assert TOKEN in text
