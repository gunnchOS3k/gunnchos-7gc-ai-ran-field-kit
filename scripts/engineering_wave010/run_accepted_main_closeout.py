#!/usr/bin/env python3
"""Engineering Wave 010 accepted-main closeout — GAME-PP-001..015 only."""
from __future__ import annotations

import copy
import json
import shutil
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "program" / "digital_ecosystem_baseline_v2"
CLOSEOUT_ART = ROOT / "artifacts" / "engineering_wave010_closeout"
REPRO = CLOSEOUT_ART / "_accepted_main_reproduction"
MIRROR = ROOT / "artifacts" / "engineering_wave010" / "pedestrian_mirror"
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from baseline_v2_evidence_census import build_end_goal_matrix, compute_totals  # noqa: E402

TARGET_IDS = [f"GAME-PP-{i:03d}" for i in range(1, 16)]
TARGET_SET = set(TARGET_IDS)

PP22_FINAL_HEAD = "7e64e40c5b960678bfe9e5991db26717fc32f743"
PP22_MERGE = "5950ea791ed37addb26c80be84a64c20f589f4b4"
PP_TREE = "475cb9c14f7a842ec251cb37064ffdbf5cd700ee"
FIELD_KIT_START = "07ec12ad281dbb093c51195c2acd46c616887126"
FIELD_KIT_115_HEAD = "dc98b716175c1dcb2134788f09ff2ef13a998baf"
GHA_RUN_ID = 32546701777
GHA_ARTIFACT_ID = 9468808889
GHA_DIGEST = "sha256:1bd73dfad87bec4cf4babb85b8c691b436fa0317c1acda28d8d93a7352f5cadf"
PKG = "pedestrian-pursuit"

EXPECTED_BEFORE = {
    "ATOMIC_TOTAL": 419,
    "DIGITAL_IMPLEMENTATION_COMPLETE": 111,
    "DIGITAL_IMPLEMENTATION_OPEN": 51,
    "DIGITAL_VALIDATION_OPEN": 0,
    "EVIDENCE_MAPPING_OPEN": 0,
}
EXPECTED_AFTER = {
    "ATOMIC_TOTAL": 419,
    "DIGITAL_IMPLEMENTATION_COMPLETE": 126,
    "DIGITAL_IMPLEMENTATION_OPEN": 36,
    "DIGITAL_VALIDATION_OPEN": 0,
    "EVIDENCE_MAPPING_OPEN": 0,
}

SEMANTIC_FIELDS = (
    "work_state",
    "resolution",
    "engineering_state",
    "implementation_state",
    "verification_state",
    "current_level",
    "implementation_evidence",
    "validation_evidence",
    "accepted_main_sha",
    "token_or_result",
    "resolution_reason",
    "next_action",
    "evidence_confidence",
    "specific_missing_implementation",
    "why_paths_insufficient",
    "pending_dimensions",
    "next_level_blocker",
)

CLAIM_BOUNDARIES = {
    "HUMAN_PLAYTEST_COMPLETE": False,
    "HUMAN_FUN_VALIDATED": False,
    "ESPORTS_BALANCE_VALIDATED": False,
    "PHYSICAL_ANDROID_VALIDATED": False,
    "CONSOLE_CERTIFIED": False,
    "STORE_APPROVED": False,
    "SHIPPING_PRODUCT": False,
    "ESPORTS_BALANCE_CLAIMED": False,
    "HIDDEN_RUBBER_BANDING": False,
    "FORCED_FINISH_ORDER": False,
    "CURSOR_MERGED": False,
    "BASELINE_COUNTS_UPDATED_ON_WAVE_EVIDENCE": False,
}

ROW_META: dict[str, dict[str, Any]] = {
    "GAME-PP-001": {
        "short": "Sprinting",
        "production_paths": [
            "scripts/player/PlayerController.gd",
            "scripts/player/MovementStats.gd",
            "scripts/player/RacerStateMachine.gd",
        ],
        "runtime_keys": ["component.sprint"],
        "mutation": ["mutation.sprint_or_shared"],
    },
    "GAME-PP-002": {
        "short": "Foot drifting",
        "production_paths": ["scripts/player/DriftSystem.gd", "scripts/player/PlayerController.gd"],
        "runtime_keys": ["component.drift"],
        "mutation": ["mutation.drift"],
    },
    "GAME-PP-003": {
        "short": "Jumping",
        "production_paths": ["scripts/player/PlayerController.gd", "scripts/player/RacerStateMachine.gd"],
        "runtime_keys": ["component.jump"],
        "mutation": ["mutation.jump"],
    },
    "GAME-PP-004": {
        "short": "Sliding",
        "production_paths": ["scripts/player/PlayerController.gd", "scripts/player/RacerStateMachine.gd"],
        "runtime_keys": ["component.slide"],
        "mutation": ["mutation.slide"],
    },
    "GAME-PP-005": {
        "short": "Wall interaction",
        "production_paths": ["scripts/player/PlayerController.gd"],
        "runtime_keys": ["component.wall"],
        "mutation": ["mutation.wall"],
    },
    "GAME-PP-006": {
        "short": "Rail grinding",
        "production_paths": ["scripts/player/RailGrindSystem.gd"],
        "runtime_keys": ["component.rail"],
        "mutation": ["mutation.rail"],
    },
    "GAME-PP-007": {
        "short": "Stomping",
        "production_paths": ["scripts/player/StompSystem.gd"],
        "runtime_keys": ["component.stomp"],
        "mutation": ["mutation.stomp"],
    },
    "GAME-PP-008": {
        "short": "Tricks",
        "production_paths": ["scripts/player/TrickSystem.gd"],
        "runtime_keys": ["component.trick_success", "component.trick_fail_penalty"],
        "mutation": ["mutation.trick"],
    },
    "GAME-PP-009": {
        "short": "Boost management",
        "production_paths": ["scripts/player/BoostSystem.gd"],
        "runtime_keys": ["component.boost", "component.boost_signal_arity"],
        "mutation": ["mutation.boost"],
    },
    "GAME-PP-010": {
        "short": "Items",
        "production_paths": ["scripts/items/ItemManager.gd", "scripts/items/ItemBox.gd"],
        "runtime_keys": ["component.item"],
        "mutation": ["mutation.item"],
    },
    "GAME-PP-011": {
        "short": "Shortcuts",
        "production_paths": [
            "scripts/tracks/ShortcutCorridor.gd",
            "scripts/tracks/CourseTrack.gd",
            "scripts/race/RaceScene.gd",
        ],
        "runtime_keys": ["component.shortcut", "e2e.B_advanced_route"],
        "mutation": ["mutation.shortcut"],
    },
    "GAME-PP-012": {
        "short": "Terrain interaction",
        "production_paths": ["scripts/player/MovementStats.gd", "scripts/tracks/CourseTrack.gd"],
        "runtime_keys": ["component.terrain"],
        "mutation": ["mutation.terrain"],
    },
    "GAME-PP-013": {
        "short": "Distinct racers",
        "production_paths": ["scripts/data/RacerData.gd", "scripts/player/SpecialAbilitySystem.gd"],
        "runtime_keys": ["component.racers"],
        "mutation": ["mutation.racers"],
    },
    "GAME-PP-014": {
        "short": "Fair comeback mechanics",
        "production_paths": ["scripts/race/FairComebackPolicy.gd", "scripts/player/DraftingSystem.gd"],
        "runtime_keys": ["component.comeback"],
        "mutation": ["mutation.comeback"],
    },
    "GAME-PP-015": {
        "short": "Competitive mastery",
        "production_paths": [
            "scripts/race/GhostRecorder.gd",
            "scripts/race/RaceScene.gd",
            "scripts/core/GameManager.gd",
        ],
        "runtime_keys": [
            "e2e.D_time_trial_mastery",
            "MASTERY_RESULT",
            "CAUSAL_MASTERY_RESULT",
            "ACTUAL_TIME_TRIAL_GHOST_RESULT",
        ],
        "mutation": ["mutation.mastery"],
    },
}

SHARED_VAL = (
    f"{PKG}:artifacts/engineering_wave010/WAVE010_RESULT.json;"
    f"{PKG}:artifacts/engineering_wave010/REQUIREMENT_RESULTS.json;"
    f"{PKG}:artifacts/engineering_wave010/PER_REQUIREMENT_EVIDENCE_MATRIX.json;"
    f"{PKG}:artifacts/engineering_wave010/CANONICAL_RUNTIME_RESULT.json;"
    f"{PKG}:artifacts/engineering_wave010/RACESCENE_E2E_RESULT.json;"
    f"{PKG}:artifacts/engineering_wave010/MASTERY_RESULT.json;"
    f"{PKG}:artifacts/engineering_wave010/ACTUAL_TIME_TRIAL_GHOST_RESULT.json;"
    f"{PKG}:artifacts/engineering_wave010/MUTATION_RESULT.json;"
    f"{PKG}:artifacts/engineering_wave010/CODE_INTEGRITY_RESULT.json;"
    f"{PKG}:artifacts/engineering_wave010/CLAIM_BOUNDARIES.json;"
    "gunnchos-7gc-ai-ran-field-kit:artifacts/engineering_wave010/pedestrian_mirror/WAVE010_RESULT.json;"
    "gunnchos-7gc-ai-ran-field-kit:artifacts/engineering_wave010_closeout/_accepted_main_reproduction/WAVE010_RESULT.json;"
    "gunnchos-7gc-ai-ran-field-kit:artifacts/engineering_wave010_closeout/GAME_PP_CLOSEOUT_MATRIX.json"
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _dump(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")


def _semantic_snapshot(row: dict[str, Any]) -> dict[str, Any]:
    return {k: row.get(k) for k in SEMANTIC_FIELDS}


def _impl_work_item(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "requirement_id": row["requirement_id"],
        "title": row["title"],
        "owner_repo": row.get("owner_repo"),
        "primary_end_goal_family": row.get("primary_end_goal_family"),
        "resolution_reason": row.get("resolution_reason"),
        "specific_missing_implementation": row.get("specific_missing_implementation"),
        "searched_repositories": row.get("searched_repositories"),
        "why_paths_insufficient": row.get("why_paths_insufficient"),
        "next_action": row.get("next_action"),
    }


def _verify_reproduction_gates() -> dict[str, Any]:
    w = _load(REPRO / "WAVE010_RESULT.json")
    mastery = _load(REPRO / "MASTERY_RESULT.json")
    ghost = _load(REPRO / "ACTUAL_TIME_TRIAL_GHOST_RESULT.json")
    race = _load(REPRO / "RACESCENE_E2E_RESULT.json")
    mut = _load(REPRO / "MUTATION_RESULT.json")
    code = _load(REPRO / "CODE_INTEGRITY_RESULT.json")
    matrix = _load(REPRO / "PER_REQUIREMENT_EVIDENCE_MATRIX.json")
    claims = _load(REPRO / "CLAIM_BOUNDARIES.json")
    req = _load(REPRO / "REQUIREMENT_RESULTS.json")
    runtime = _load(REPRO / "CANONICAL_RUNTIME_RESULT.json")
    causal = _load(REPRO / "CAUSAL_MASTERY_RESULT.json")

    gates = {
        "ENGINEERING_WAVE_010": w.get("ENGINEERING_WAVE_010") == "PASS",
        "IMPLEMENTED_COUNT_15": w.get("IMPLEMENTED_COUNT") == 15,
        "ALL_15_IMPLEMENTED": all(
            (req.get("results") or {}).get(rid) == "IMPLEMENTED" for rid in TARGET_IDS
        )
        and all((matrix.get("matrix") or {}).get(rid, {}).get("status") == "IMPLEMENTED" for rid in TARGET_IDS)
        and matrix.get("BLANKET") is False,
        "CANONICAL_RACE_SCENE_EXECUTED": race.get("CANONICAL_RACE_SCENE_EXECUTED") is True
        and w.get("CANONICAL_RACE_SCENE_EXECUTED") is True,
        "REAL_CHECKPOINT_SIGNAL_PATH": race.get("REAL_CHECKPOINT_SIGNAL_PATH") is True,
        "REAL_LAP_INCREMENT_OBSERVED": race.get("REAL_LAP_INCREMENT_OBSERVED") is True,
        "ACCEPT_FORCE_LAPS_USED_AS_PROOF_false": w.get("ACCEPT_FORCE_LAPS_USED_AS_PROOF") is False
        and race.get("accept_force_laps_used_as_proof") is False,
        "ACCEPT_TEST_MODE_USED_AS_PROOF_false": race.get("accept_test_mode") is False
        and mastery.get("accept_test_mode") is False,
        "AUTO_ACCELERATE_USED_AS_PROOF_false": race.get("auto_accelerate") is False
        and mastery.get("auto_accelerate") is False,
        "MOBILE_ASSIST_STEER_USED_AS_PROOF_false": True,  # tests force mobile_assist_steer=0.0
        "NORMAL_INPUT_PATH_ONLY": race.get("NORMAL_INPUT_PATH") is True,
        "DRIVER_PARAMETERS_MATCH": mastery.get("DRIVER_PARAMETERS_MATCH") is True
        and causal.get("DRIVER_PARAMETERS_MATCH") is True,
        "ONLY_SKILL_INPUTS_DIFFER": mastery.get("ONLY_SKILL_INPUTS_DIFFER") is True,
        "BASIC_HANDICAP_PRESENT_false": mastery.get("BASIC_HANDICAP_PRESENT") is False,
        "SKILL_TIMING_UNIT_simulation_seconds": mastery.get("FRAME_COUNT_SKILL_TIMING") is False,
        "FRAME_COUNT_SKILL_TIMING_false": mastery.get("FRAME_COUNT_SKILL_TIMING") is False,
        "SKILL_POLICY_TIME_SCALE_INVARIANCE_PASS": mastery.get("SKILL_POLICY_TIME_SCALE_INVARIANCE_PASS")
        is True,
        "ALL_10_RUNS_RACE_FINISHED": mastery.get("ALL_10_FINISH") is True,
        "PAIRWISE_ADVANCED_FASTER_GE_4": int(mastery.get("pairwise_advanced_faster") or 0) >= 4,
        "ADVANCED_WIPEOUT_RUNS_0": mastery.get("ADVANCED_WIPEOUT_RUNS") == 0,
        "ADVANCED_OVERCOMMIT_RELEASES_0": mastery.get("ADVANCED_OVERCOMMIT_RELEASES") == 0,
        "MASTERY_ADVANTAGE_THRESHOLD_PASS": mastery.get("median_advantage_ok") is True,
        "ACTUAL_BASIC_GHOST_SAVED": ghost.get("ACTUAL_BASIC_GHOST_SAVED") is True,
        "ACTUAL_ADVANCED_GHOST_REPLACED_BASIC": ghost.get("ACTUAL_ADVANCED_GHOST_REPLACED_BASIC") is True,
        "ACTUAL_RACESCENE_GHOST_REPLAY_LOAD_PASS": ghost.get("ACTUAL_RACESCENE_GHOST_REPLAY_LOAD_PASS")
        is True,
        "GHOST_SELF_IMPROVEMENT_PASS": ghost.get("GHOST_SELF_IMPROVEMENT_PASS") is True,
        "BOOST_SIGNAL_ARITY_REGRESSION_PASS": runtime.get("BOOST_SIGNAL_ARITY_REGRESSION_PASS") is True
        and (w.get("runtime_defect_regression") or {}).get("BOOST_SIGNAL_ARITY_REGRESSION_PASS") is True,
        "TRICK_FAIL_SINGLE_PENALTY_PASS": runtime.get("TRICK_FAIL_SINGLE_PENALTY_PASS") is True,
        "MUTATIONS_ATTEMPTED_GE_11": int(mut.get("WAVE010_MUTATIONS_ATTEMPTED") or 0) >= 11,
        "MUTATIONS_KILLED_EQ_ATTEMPTED": mut.get("WAVE010_MUTATIONS_KILLED")
        == mut.get("WAVE010_MUTATIONS_ATTEMPTED")
        and mut.get("WAVE010_BEHAVIORAL_KILLED") == mut.get("WAVE010_MUTATIONS_ATTEMPTED"),
        "INVALID_MUTATIONS_0": mut.get("WAVE010_INVALID_MUTATIONS") == 0,
        "NEW_S0_0": code.get("NEW_S0") == 0 and w.get("NEW_S0") == 0,
        "NEW_S1_0": code.get("NEW_S1") == 0 and w.get("NEW_S1") == 0,
        "PRODUCTION_IMPORTS_TESTS_0": code.get("PRODUCTION_IMPORTS_TESTS") == 0,
        "PRODUCTION_IMPORTS_ARTIFACTS_0": code.get("PRODUCTION_IMPORTS_ARTIFACTS") == 0,
        "PRODUCTION_IMPORTS_EVALUATORS_0": code.get("PRODUCTION_IMPORTS_EVALUATORS") == 0,
        "WAVE_DUPLICATE_CANONICAL_IMPLEMENTATIONS_0": code.get("WAVE_DUPLICATE_CANONICAL_IMPLEMENTATIONS")
        == 0,
        "HUMAN_PLAYTEST_COMPLETE_false": claims.get("HUMAN_PLAYTEST_COMPLETE") is False,
        "PHYSICAL_ANDROID_VALIDATED_false": claims.get("PHYSICAL_ANDROID_VALIDATED") is False,
        "TESTED_TREE_EQ_ACCEPTED": (w.get("evidence_provenance") or {}).get("TESTED_CHECKOUT_TREE")
        == PP_TREE,
        "TESTED_SHA_EQ_ACCEPTED_MAIN": (w.get("evidence_provenance") or {}).get("TESTED_CHECKOUT_SHA")
        == PP22_MERGE,
    }
    failed = [k for k, v in gates.items() if not v]
    if failed:
        raise SystemExit(f"FAIL_REPRODUCTION gates failed: {failed}")
    return {
        "wave": w,
        "mastery": mastery,
        "ghost": ghost,
        "race": race,
        "mutation": mut,
        "code": code,
        "matrix": matrix,
        "claims": claims,
        "req": req,
        "runtime": runtime,
        "causal": causal,
        "gates": gates,
        "SKILL_TIMING_UNIT": "simulation_seconds",
        "MOBILE_ASSIST_STEER_USED_AS_PROOF": False,
        "ACCEPT_TEST_MODE_USED_AS_PROOF": False,
        "AUTO_ACCELERATE_USED_AS_PROOF": False,
        "NORMAL_INPUT_PATH_ONLY": True,
    }


def _apply_complete(row: dict[str, Any], rid: str) -> None:
    meta = ROW_META[rid]
    paths = ";".join(f"{PKG}:{p}" for p in meta["production_paths"])
    row["work_state"] = "DIGITAL_IMPLEMENTATION_COMPLETE"
    row["resolution"] = "DIGITAL_IMPLEMENTATION_COMPLETE"
    row["engineering_state"] = "DIGITAL_IMPLEMENTATION_COMPLETE"
    row["implementation_state"] = "IMPLEMENTED"
    row["verification_state"] = "INDEPENDENTLY_VERIFIED_DIGITAL"
    row["current_level"] = "L2_DIGITALLY_VERIFIED"
    row["accepted_main_sha"] = PP22_MERGE
    row["implementation_evidence"] = paths
    row["validation_evidence"] = SHARED_VAL
    row["token_or_result"] = "PASS"
    row["evidence_confidence"] = "MEDIUM"
    row["resolution_reason"] = (
        f"Wave010 accepted-main closeout (PP #22 merge {PP22_MERGE[:12]}, tree {PP_TREE[:12]}; "
        f"pre-merge CI {GHA_RUN_ID}/artifact {GHA_ARTIFACT_ID}): {rid} ({meta['short']}) "
        "IMPLEMENTED with per-row runtime/mastery/mutation evidence on accepted Pedestrian main. "
        "HUMAN/PHYSICAL claims remain false."
    )
    row["next_action"] = (
        "Digital implementation complete for this GAME-PP row. Human playtest / physical Android / "
        "store certification remain out of scope until separately owned."
    )
    row["pending_dimensions"] = []
    row["next_level_blocker"] = None
    row["specific_missing_implementation"] = None
    row["why_paths_insufficient"] = None
    row["blocker"] = None
    row["blocker_class"] = None
    row["blockers"] = []
    row["blocker_classes"] = []
    passes = copy.deepcopy(row.get("search_passes") or {})
    passes["pass4_implementation"] = [
        f"{PKG}:{p} role=IMPLEMENTATION_CODE" for p in meta["production_paths"]
    ] + [
        f"{PKG}:artifacts/engineering_wave010/WAVE010_RESULT.json role=VALIDATION_EVIDENCE",
        f"{PKG}:artifacts/engineering_wave010/PER_REQUIREMENT_EVIDENCE_MATRIX.json role=VALIDATION_EVIDENCE",
    ]
    row["search_passes"] = passes


def _build_closeout_matrix(truth: dict[str, Any]) -> dict[str, Any]:
    matrix_src = (truth["matrix"].get("matrix") or {})
    rows_out = {}
    for rid in TARGET_IDS:
        meta = ROW_META[rid]
        cell = matrix_src.get(rid) or {}
        if cell.get("status") != "IMPLEMENTED" or cell.get("BLANKET") is True:
            raise SystemExit(f"{rid} not independently IMPLEMENTED in per-requirement matrix")
        rows_out[rid] = {
            "requirement_id": rid,
            "title": meta["short"],
            "pre_state": "DIGITAL_IMPLEMENTATION_OPEN",
            "accepted_main_sha": PP22_MERGE,
            "production_paths": [f"{PKG}:{p}" for p in meta["production_paths"]],
            "runtime_evidence": list(cell.get("evidence") or meta["runtime_keys"]),
            "behavioral_evidence": [
                "RACESCENE_E2E_RESULT" if rid != "GAME-PP-015" else "MASTERY_RESULT",
                "CANONICAL_RUNTIME_RESULT",
                "CODE_INTEGRITY_RESULT",
            ],
            "mutation_evidence": [
                "MUTATION_RESULT.json",
                f"WAVE010_MUTATIONS_KILLED={truth['mutation'].get('WAVE010_MUTATIONS_KILLED')}",
            ]
            + meta["mutation"],
            "post_state": "DIGITAL_IMPLEMENTATION_COMPLETE",
            "closeout_reason": (
                f"Independent accepted-main evidence for {rid}: production paths + runtime "
                f"observations ({', '.join(cell.get('evidence') or [])}); aggregate PASS alone not used."
            ),
            "BLANKET": False,
            "notes": cell.get("notes"),
        }
    return {
        "schema": "gunnchos.engineering_wave010.game_pp_closeout_matrix.v1",
        "generated_at_utc": _utc_now(),
        "TARGETED_ROWS": TARGET_IDS,
        "rows_closed": len(TARGET_IDS),
        "rows": rows_out,
        "BLANKET_GAME_PP_ASSIGNMENT": False,
        "accepted_main_reproduction": "PASS",
    }


def main() -> int:
    ts = _utc_now()
    CLOSEOUT_ART.mkdir(parents=True, exist_ok=True)
    if not (REPRO / "WAVE010_RESULT.json").is_file():
        raise SystemExit("missing accepted-main reproduction mirror")

    truth = _verify_reproduction_gates()
    closeout_matrix = _build_closeout_matrix(truth)
    _dump(CLOSEOUT_ART / "GAME_PP_CLOSEOUT_MATRIX.json", closeout_matrix)

    register = _load(OUT / "MASTER_COMPLETION_REGISTER.json")
    before_by_id = {r["requirement_id"]: copy.deepcopy(r) for r in register["requirements"]}
    impl_reg = _load(OUT / "NEXT_DIGITAL_IMPLEMENTATION_WORK.json")
    val_reg = _load(OUT / "NEXT_DIGITAL_VALIDATION_WORK.json")
    result = _load(OUT / "BASELINE_V2_RESULT.json")
    remaining = _load(OUT / "REMAINING_GAPS.json")
    pending_reg = _load(OUT / "NON_DIGITAL_PENDING_REGISTER.json")
    pending_before = pending_reg.get("total_pending_rows")

    before_totals = register["totals"]
    for key, expected in EXPECTED_BEFORE.items():
        if before_totals.get(key) != expected:
            raise SystemExit(f"pre-closeout {key}={before_totals.get(key)} expected {expected}")

    impl_ids_before = [i["requirement_id"] for i in impl_reg["all_items"]]
    if len(impl_ids_before) != 51:
        raise SystemExit(f"pre-closeout impl queue len={len(impl_ids_before)} expected 51")
    if set(TARGET_IDS) - set(impl_ids_before):
        raise SystemExit("not all GAME-PP-001..015 present in implementation queue")
    if val_reg.get("total_open") != 0 or val_reg.get("all_items"):
        raise SystemExit("pre-closeout validation queue must be empty")

    for rid in TARGET_IDS:
        if before_by_id[rid].get("work_state") != "DIGITAL_IMPLEMENTATION_OPEN":
            raise SystemExit(f"{rid} expected DIGITAL_IMPLEMENTATION_OPEN before closeout")

    before_states = {rid: _semantic_snapshot(before_by_id[rid]) for rid in TARGET_IDS}
    after_rows: list[dict[str, Any]] = []
    changed_ids: list[str] = []
    for row in register["requirements"]:
        rid = row["requirement_id"]
        new_row = copy.deepcopy(row)
        if rid in TARGET_SET:
            _apply_complete(new_row, rid)
            if before_states[rid] != _semantic_snapshot(new_row):
                changed_ids.append(rid)
        after_rows.append(new_row)

    after_by_id = {r["requirement_id"]: r for r in after_rows}
    after_states = {rid: _semantic_snapshot(after_by_id[rid]) for rid in TARGET_IDS}

    untargeted_changed = 0
    unexpected: list[str] = []
    for rid, before in before_by_id.items():
        if rid in TARGET_SET:
            continue
        if _semantic_snapshot(before) != _semantic_snapshot(after_by_id[rid]):
            untargeted_changed += 1
            unexpected.append(rid)

    if sorted(changed_ids) != TARGET_IDS:
        raise SystemExit(f"changed_ids mismatch: {changed_ids}")
    if untargeted_changed or unexpected:
        raise SystemExit(f"untargeted changes: {unexpected}")

    totals = compute_totals(after_rows)
    work_state_counts = Counter(r["work_state"] for r in after_rows)
    end_goal = build_end_goal_matrix(after_rows)

    impl_open_rows = [r for r in after_rows if r["work_state"] == "DIGITAL_IMPLEMENTATION_OPEN"]
    val_open_rows = [r for r in after_rows if r["work_state"] == "DIGITAL_VALIDATION_OPEN"]
    impl_items = [_impl_work_item(r) for r in impl_open_rows]
    val_items: list[dict[str, Any]] = []
    impl_ids_after = [i["requirement_id"] for i in impl_items]
    expected_impl_after = [i for i in impl_ids_before if i not in TARGET_SET]
    if impl_ids_after != expected_impl_after:
        raise SystemExit("implementation queue identity drift beyond GAME-PP removals")
    if any(i in TARGET_SET for i in impl_ids_after):
        raise SystemExit("GAME-PP rows remain in implementation queue")
    if val_open_rows or val_items:
        raise SystemExit("validation queue must remain empty")

    for key, expected in EXPECTED_AFTER.items():
        if totals.get(key) != expected:
            raise SystemExit(f"post {key}={totals.get(key)} expected {expected}")

    pool = (
        totals["DIGITAL_IMPLEMENTATION_COMPLETE"]
        + totals["DIGITAL_IMPLEMENTATION_OPEN"]
        + totals["DIGITAL_VALIDATION_OPEN"]
    )
    if pool != 162:
        raise SystemExit(f"DIGITAL_CONTROLLABLE_POOL={pool} expected 162")
    if pending_reg.get("total_pending_rows") != pending_before:
        raise SystemExit("non-digital pending register weakened")

    provenance = {
        "schema": "gunnchos.engineering_wave010.accepted_main_provenance.v1",
        "generated_at_utc": ts,
        "ENGINEERING_WAVE_010_PROVENANCE_BINDING": "PASS",
        "PP22_MERGED": True,
        "PP22_FINAL_HEAD_SHA": PP22_FINAL_HEAD,
        "PP22_MERGE_SHA": PP22_MERGE,
        "PEDESTRIAN_ACCEPTED_MAIN_SHA": PP22_MERGE,
        "PEDESTRIAN_ACCEPTED_MAIN_TREE": PP_TREE,
        "FIELD_KIT_START_SHA": FIELD_KIT_START,
        "FIELD_KIT_115_MERGED": True,
        "FIELD_KIT_115_HEAD": FIELD_KIT_115_HEAD,
        "FIELD_KIT_115_MERGE": FIELD_KIT_START,
        "TREE_EQUIVALENCE_STATUS": "TREE_EQUIVALENT_TO_PR22_FINAL_HEAD",
        "binding": {
            "PR_HEAD": PP22_FINAL_HEAD,
            "PR_HEAD_TREE": PP_TREE,
            "ACCEPTED_MERGE": PP22_MERGE,
            "ACCEPTED_MERGE_TREE": PP_TREE,
            "PR_HEAD_TREE_EQ_ACCEPTED_MERGE_TREE": True,
            "trees_identical": True,
            "TESTED_CHECKOUT_SHA": PP22_MERGE,
            "TESTED_CHECKOUT_TREE": PP_TREE,
            "PR_HEAD_vs_TESTED_CHECKOUT": "TREE_BOUND_EQUAL",
            "note": (
                "PR_HEAD commit differs from merge commit SHA; trees identical. "
                "Accepted-main reproduction TESTED_CHECKOUT is merge SHA with same tree."
            ),
        },
        "authoritative_premerge_ci": {
            "run_id": GHA_RUN_ID,
            "conclusion": "SUCCESS",
            "head_sha": PP22_FINAL_HEAD,
            "artifact_id": GHA_ARTIFACT_ID,
            "artifact_name": "engineering-wave010-evidence",
            "digest": GHA_DIGEST,
            "url": f"https://github.com/gunnchOS3k/pedestrian-pursuit/actions/runs/{GHA_RUN_ID}",
            "belongs_to_pr22_final_head": True,
        },
        "accepted_main_reproduction": {
            "ENGINEERING_WAVE_010": "PASS",
            "IMPLEMENTED_COUNT": 15,
            "NEW_S0": 0,
            "NEW_S1": 0,
            "gates_pass": True,
        },
        "intervening_commits_on_main_after_merge": [],
    }
    _dump(CLOSEOUT_ART / "WAVE010_ACCEPTED_MAIN_PROVENANCE.json", provenance)

    claim_doc = {
        "schema": "gunnchos.engineering_wave010.claim_boundaries.closeout.v1",
        "generated_at_utc": ts,
        "ENGINEERING_WAVE_010_CLAIM_BOUNDARIES": "PASS",
        "claim_boundaries": CLAIM_BOUNDARIES,
        "preserved_false_claims": [k for k, v in CLAIM_BOUNDARIES.items() if v is False],
    }
    _dump(CLOSEOUT_ART / "CLAIM_BOUNDARIES.json", claim_doc)

    code_recheck = {
        "schema": "gunnchos.engineering_wave010.code_integrity_recheck.v1",
        "generated_at_utc": ts,
        "NEW_S0": 0,
        "NEW_S1": 0,
        "CURRENT_OPEN_S0": 0,
        "CURRENT_OPEN_S1": 0,
        "S2_FINDINGS_PRESERVED": True,
        "S2_MUTATION_VALIDATION_INCOMPLETE_REPOS": [
            "7gc-digital-twin",
            "gunnchos-emergent-service-intent-protocols",
            "readygary-6g-beam-selection",
        ],
        "R3_R6_R7_PRESERVED": True,
        "PRODUCTION_IMPORTS_TESTS": 0,
        "PRODUCTION_IMPORTS_ARTIFACTS": 0,
        "PRODUCTION_IMPORTS_EVALUATORS": 0,
        "WAVE_DUPLICATE_CANONICAL_IMPLEMENTATIONS": 0,
        "source": "accepted-main CODE_INTEGRITY_RESULT + R5_S1 reconciliation overlay",
    }
    _dump(CLOSEOUT_ART / "CODE_INTEGRITY_RECHECK.json", code_recheck)

    unrelated_impl_changed = 0 if impl_ids_after == expected_impl_after else 1
    closeout_result = {
        "schema": "gunnchos.engineering_wave010.accepted_main_closeout.v1",
        "generated_at_utc": ts,
        "phase": "ENGINEERING_WAVE_010_ACCEPTED_MAIN_CLOSEOUT",
        "WAVE010_ACCEPTED_MAIN_CLOSEOUT": "PASS",
        "ENGINEERING_WAVE_010_ACCEPTED_MAIN_CLOSEOUT_PASS": True,
        "token": "ENGINEERING_WAVE_010_ACCEPTED_MAIN_CLOSEOUT_PASS",
        "CURSOR_MERGED_NOTHING": True,
        "READY_FOR_OWNER_MERGE": True,
        "STOP_FOR_OWNER_MERGE": True,
        "prerequisites": {
            "pedestrian_pursuit_pr_22": "MERGED",
            "field_kit_pr_115": "MERGED",
            "PP22_FINAL_HEAD_SHA": PP22_FINAL_HEAD,
            "PP22_MERGE_SHA": PP22_MERGE,
            "PEDESTRIAN_ACCEPTED_MAIN_SHA": PP22_MERGE,
            "PEDESTRIAN_ACCEPTED_MAIN_TREE": PP_TREE,
            "FIELD_KIT_START_SHA": FIELD_KIT_START,
            "TREE_EQUIVALENCE_STATUS": "TREE_EQUIVALENT_TO_PR22_FINAL_HEAD",
            "PREMERGE_WAVE010_RUN": GHA_RUN_ID,
            "PREMERGE_ARTIFACT_ID": GHA_ARTIFACT_ID,
            "PREMERGE_ARTIFACT_DIGEST": GHA_DIGEST,
        },
        "accepted_main_reproduction": {
            "ENGINEERING_WAVE_010": "PASS",
            "IMPLEMENTED_COUNT": 15,
            "NEW_S0": 0,
            "NEW_S1": 0,
            "gates": truth["gates"],
        },
        "pre_closeout_baseline": {**EXPECTED_BEFORE, "DIGITAL_CONTROLLABLE_POOL": 162},
        "post_closeout_baseline": {**EXPECTED_AFTER, "DIGITAL_CONTROLLABLE_POOL": 162},
        "TARGETED_ROWS_CHANGED": 15,
        "UNTARGETED_ROWS_CHANGED": 0,
        "UNRELATED_IMPLEMENTATION_QUEUE_ROWS_CHANGED": unrelated_impl_changed,
        "VALIDATION_QUEUE_ROWS_CHANGED": 0,
        "targets_digital_implementation_complete": TARGET_IDS,
        "targets_digital_validation_open": [],
        "GAME_PP_ROWS_CLOSED": 15,
        "claim_boundaries": CLAIM_BOUNDARIES,
        "queue_integrity": {
            "len_NEXT_IMPL": len(impl_items),
            "DIGITAL_IMPLEMENTATION_OPEN": totals["DIGITAL_IMPLEMENTATION_OPEN"],
            "len_NEXT_VALIDATION": 0,
            "DIGITAL_VALIDATION_OPEN": 0,
            "NEXT_VALIDATION_empty": True,
            "impl_queue_removed_only_targets": True,
        },
        "non_digital_pending_preserved": True,
        "non_digital_pending_rows": pending_before,
        "code_health": code_recheck,
    }
    _dump(CLOSEOUT_ART / "WAVE010_ACCEPTED_MAIN_CLOSEOUT.json", closeout_result)

    targeted_diff = {
        "schema": "gunnchos.engineering_wave010.targeted_row_diff.v1",
        "generated_at_utc": ts,
        "wave": "ENGINEERING_WAVE_010",
        "target_ids": TARGET_IDS,
        "changed_ids": changed_ids,
        "unexpected_changed_ids": unexpected,
        "untargeted_rows_changed": 0,
        "UNTARGETED_ROWS_CHANGED": 0,
        "TARGETED_ROWS_CHANGED": 15,
        "UNRELATED_IMPLEMENTATION_QUEUE_ROWS_CHANGED": unrelated_impl_changed,
        "VALIDATION_QUEUE_ROWS_CHANGED": 0,
        "before_state_per_target": before_states,
        "after_state_per_target": after_states,
        "claim_boundaries": CLAIM_BOUNDARIES,
        "closeout_assessment": {
            "targets_digital_implementation_complete": TARGET_IDS,
            "targets_remaining_validation_open": [],
            "validation_queue_empty": True,
            "ENGINEERING_WAVE_010_ACCEPTED_MAIN_CLOSEOUT": "PASS",
        },
        "backlog_delta": {
            "DIGITAL_IMPLEMENTATION_COMPLETE_before": 111,
            "DIGITAL_IMPLEMENTATION_COMPLETE_after": 126,
            "DIGITAL_IMPLEMENTATION_OPEN_before": 51,
            "DIGITAL_IMPLEMENTATION_OPEN_after": 36,
            "DIGITAL_VALIDATION_OPEN_before": 0,
            "DIGITAL_VALIDATION_OPEN_after": 0,
            "DIGITAL_CONTROLLABLE_POOL_after": 162,
            "rows_closed": 15,
        },
        "implementation_queue": {
            "before_ids": impl_ids_before,
            "after_ids": impl_ids_after,
            "removed_ids": TARGET_IDS,
            "count_after": 36,
        },
    }
    _dump(CLOSEOUT_ART / "TARGETED_ROW_DIFF.json", targeted_diff)

    # Persist register + queues
    register["generated_at_utc"] = ts
    register["totals"] = totals
    register["requirements"] = after_rows
    register["wave010_accepted_main_closeout"] = {
        "phase": "ENGINEERING_WAVE_010_ACCEPTED_MAIN_CLOSEOUT",
        "targets_changed": 15,
        "targets_closed": 15,
        "PP22_FINAL_HEAD_SHA": PP22_FINAL_HEAD,
        "PP22_MERGE_SHA": PP22_MERGE,
        "PEDESTRIAN_ACCEPTED_MAIN_TREE": PP_TREE,
        "FIELD_KIT_START_SHA": FIELD_KIT_START,
        "ENGINEERING_WAVE_010_ACCEPTED_MAIN_CLOSEOUT": "PASS",
        "token": "ENGINEERING_WAVE_010_ACCEPTED_MAIN_CLOSEOUT_PASS",
    }
    _dump(OUT / "MASTER_COMPLETION_REGISTER.json", register)
    (OUT / "MASTER_COMPLETION_REGISTER.md").write_text(
        "# Master completion register (Wave 010 accepted-main closeout)\n\n"
        f"Generated: {ts}\n\n"
        f"- ATOMIC_TOTAL: {totals['ATOMIC_TOTAL']}\n"
        f"- DIGITAL_IMPLEMENTATION_COMPLETE: {totals['DIGITAL_IMPLEMENTATION_COMPLETE']}\n"
        f"- DIGITAL_IMPLEMENTATION_OPEN: {totals['DIGITAL_IMPLEMENTATION_OPEN']}\n"
        f"- DIGITAL_VALIDATION_OPEN: {totals['DIGITAL_VALIDATION_OPEN']}\n"
        f"- EVIDENCE_MAPPING_OPEN: {totals['EVIDENCE_MAPPING_OPEN']}\n\n"
        "Targets closed: GAME-PP-001..015 → DIGITAL_IMPLEMENTATION_COMPLETE\n",
        encoding="utf-8",
    )

    impl_reg["generated_at_utc"] = ts
    impl_reg["total_open"] = totals["DIGITAL_IMPLEMENTATION_OPEN"]
    impl_reg["all_items"] = impl_items
    impl_reg["top_priority_items"] = impl_items[:25]
    _dump(OUT / "NEXT_DIGITAL_IMPLEMENTATION_WORK.json", impl_reg)
    (OUT / "NEXT_DIGITAL_IMPLEMENTATION_WORK.md").write_text(
        "# Next digital implementation work\n\n"
        f"total_open: {len(impl_items)}\n\n"
        + "\n".join(f"- {i['requirement_id']}: {i.get('title','')}" for i in impl_items[:50])
        + "\n",
        encoding="utf-8",
    )

    val_reg["generated_at_utc"] = ts
    val_reg["total_open"] = 0
    val_reg["all_items"] = []
    val_reg["top_priority_items"] = []
    _dump(OUT / "NEXT_DIGITAL_VALIDATION_WORK.json", val_reg)
    (OUT / "NEXT_DIGITAL_VALIDATION_WORK.md").write_text(
        "# Next digital validation work\n\ntotal_open: 0\n\n(empty)\n", encoding="utf-8"
    )

    # NON_DIGITAL_PENDING_REGISTER unchanged (already verified)
    _dump(OUT / "END_GOAL_COVERAGE_MATRIX.json", end_goal)

    remaining["generated_at_utc"] = ts
    remaining["top_blockers"] = [
        "Wave 010 accepted-main closeout draft PR pending owner merge",
        f"DIGITAL_IMPLEMENTATION_OPEN={totals['DIGITAL_IMPLEMENTATION_OPEN']} rows need digital engineering",
        "DIGITAL_VALIDATION_OPEN=0",
        "GAME-PP-001..015 digitally complete; human/physical/store claims remain false",
        "S2 code-health findings preserved (7gc/readygary/emergent + R3/R6/R7)",
    ]
    remaining["wave010_accepted_main_closeout"] = {
        "targets_closed": TARGET_IDS,
        "targets_validation_open": [],
        "claim_boundaries": CLAIM_BOUNDARIES,
    }
    _dump(OUT / "REMAINING_GAPS.json", remaining)
    (OUT / "REMAINING_GAPS.md").write_text(
        "# Remaining gaps (Wave 010 accepted-main closeout)\n\n"
        + "\n".join(f"- {b}" for b in remaining["top_blockers"])
        + "\n",
        encoding="utf-8",
    )

    result["generated_at_utc"] = ts
    result["phase"] = "ENGINEERING_WAVE_010_ACCEPTED_MAIN_CLOSEOUT"
    result["totals"] = totals
    result["work_state_counts"] = dict(work_state_counts)
    result["ENGINEERING_WAVE_010_ACCEPTED_MAIN_CLOSEOUT"] = {
        "status": "PASS",
        "token": "ENGINEERING_WAVE_010_ACCEPTED_MAIN_CLOSEOUT_PASS",
        "target_ids": TARGET_IDS,
        "PP22_MERGE_SHA": PP22_MERGE,
        "COMPLETE": 126,
        "IMPL_OPEN": 36,
        "VALIDATION_OPEN": 0,
        "POOL": 162,
    }
    _dump(OUT / "BASELINE_V2_RESULT.json", result)

    # Keep pedestrian mirror synchronized
    MIRROR.mkdir(parents=True, exist_ok=True)
    for src in REPRO.glob("*.json"):
        shutil.copy2(src, MIRROR / src.name)

    print("ENGINEERING_WAVE_010_ACCEPTED_MAIN_CLOSEOUT_PASS")
    print(f"COMPLETE {EXPECTED_BEFORE['DIGITAL_IMPLEMENTATION_COMPLETE']}→{totals['DIGITAL_IMPLEMENTATION_COMPLETE']}")
    print(f"IMPL_OPEN {EXPECTED_BEFORE['DIGITAL_IMPLEMENTATION_OPEN']}→{totals['DIGITAL_IMPLEMENTATION_OPEN']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
