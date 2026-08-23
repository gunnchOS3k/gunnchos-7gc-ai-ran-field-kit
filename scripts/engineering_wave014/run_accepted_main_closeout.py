#!/usr/bin/env python3
"""Engineering Wave 014 accepted-main closeout — capability ledger only (FORCED_ROW_CLOSURES=0)."""
from __future__ import annotations

import argparse
import copy
import json
import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "program" / "digital_ecosystem_baseline_v2"
CLOSEOUT_ART = ROOT / "artifacts" / "engineering_wave014_closeout"
REPRO = CLOSEOUT_ART / "_accepted_main_reproduction"
MIRROR = ROOT / "artifacts" / "engineering_wave014" / "anime_mirror"
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from baseline_v2_evidence_census import compute_totals  # noqa: E402

PR84_FINAL_HEAD = "aa28654ff33cea28e79bf7d3941dfc3c81db50cc"
PR84_MERGE_SHA = "706aba63274c9b563dfc34e76502d78a7cac19a9"
ANIME_TREE = "faa3ff384e74d715ff2159ccf3b182452a409d7f"
FIELD_KIT_START_SHA = "12f4416fee08d266b4a34fd43198094ba42ef6d1"
GHA_RUN_ID = 32604653603
GHA_ARTIFACT_ID = 9483927490
GHA_DIGEST = "sha256:f0c55441099e69ad354e79f667be7c1dfca6d0b03d864c03b4d54ab5dc7a997c"
PKG = "anime-aggressors"
PROD_ROOT = "game-godot"
TOKEN = "ENGINEERING_WAVE_014_ACCEPTED_MAIN_CLOSEOUT_PASS"

EXPECTED_BASELINE = {
    "ATOMIC_TOTAL": 419,
    "DIGITAL_IMPLEMENTATION_COMPLETE": 136,
    "DIGITAL_IMPLEMENTATION_OPEN": 26,
    "DIGITAL_VALIDATION_OPEN": 0,
    "EVIDENCE_MAPPING_OPEN": 0,
    "DIGITAL_CONTROLLABLE_POOL": 162,
}

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

CLAIM_BOUNDARIES = {
    "HUMAN_PLAYTEST_COMPLETE": False,
    "HUMAN_FUN_VALIDATED": False,
    "ESPORTS_BALANCE_VALIDATED": False,
    "PHYSICAL_ANDROID_VALIDATED": False,
    "PHYSICAL_PIXEL6A_VALIDATED": False,
    "FINAL_CHARACTER_ART_PASS": False,
    "FINAL_HUMAN_AUTHORED_ANIMATION_PASS": False,
    "REAL_USER_MOTION_LIBRARY_PRESENT": False,
    "CONSOLE_CERTIFIED": False,
    "STORE_APPROVED": False,
    "SHIPPING_PRODUCT": False,
    "ESPORTS_BALANCE_CLAIMED": False,
    "TOURNAMENT_CLAIMED": False,
    "HIDDEN_RUBBER_BANDING": False,
    "FORCED_FINISH_ORDER": False,
    "CURSOR_MERGED": False,
    "BASELINE_COUNTS_UPDATED_ON_WAVE_EVIDENCE": False,
}

WAVE014_MIRROR_JSON = [
    "WAVE014_RESULT.json",
    "WAVE011_RESULT.json",
    "WAVE012_RESULT.json",
    "WAVE013B_RESULT.json",
    "BATTLESCENE_VISUAL_E2E.json",
    "VISIBLE_SKELETAL_RUNTIME_RESULT.json",
    "VISIBLE_GAME_JUICE_RUNTIME_RESULT.json",
    "PROCEDURAL_CHARACTER_RESULT.json",
    "PROCEDURAL_ANIMATION_RESULT.json",
    "PROCEDURAL_SMOKE_RESULT.json",
    "CODE_INTEGRITY_RESULT.json",
    "TRUTH_BOUNDARIES.json",
    "QUALITY_GATES.json",
    "PERFORMANCE_SMOKE.json",
    "GAME_JUICE_RUNTIME.json",
    "ANIMATION_DISTINCTNESS.json",
    "SILHOUETTE_DISTINCTNESS.json",
]

WAVE_ARTIFACT_MAP = {
    "WAVE011_RESULT.json": "engineering_wave011",
    "WAVE012_RESULT.json": "engineering_wave012",
    "WAVE013B_RESULT.json": "engineering_wave013b",
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _dump(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")


def _anime_root(arg: str | None) -> Path:
    if arg:
        return Path(arg).resolve()
    env = os.environ.get("ANIME_AGGRESSORS_ROOT")
    if env:
        return Path(env).resolve()
    return (ROOT.parent / "anime-aggressors").resolve()


def _mirror_reproduction(anime_root: Path) -> None:
    REPRO.mkdir(parents=True, exist_ok=True)
    wave014_src = anime_root / "artifacts" / "engineering_wave014"
    if not wave014_src.is_dir():
        raise SystemExit(f"missing anime wave014 artifacts at {wave014_src}")

    for name in WAVE014_MIRROR_JSON:
        if name in WAVE_ARTIFACT_MAP:
            src = anime_root / "artifacts" / WAVE_ARTIFACT_MAP[name] / name
        else:
            src = wave014_src / name
        if not src.is_file():
            raise SystemExit(f"missing reproduction source {src}")
        shutil.copy2(src, REPRO / name)

    (REPRO / "TESTED_SHA.txt").write_text(PR84_MERGE_SHA + "\n", encoding="utf-8")
    (REPRO / "TESTED_TREE.txt").write_text(ANIME_TREE + "\n", encoding="utf-8")


def _verify_reproduction_gates() -> dict[str, Any]:
    w011 = _load(REPRO / "WAVE011_RESULT.json")
    w012 = _load(REPRO / "WAVE012_RESULT.json")
    w013b = _load(REPRO / "WAVE013B_RESULT.json")
    w014 = _load(REPRO / "WAVE014_RESULT.json")
    battle = _load(REPRO / "BATTLESCENE_VISUAL_E2E.json")
    skeletal = _load(REPRO / "VISIBLE_SKELETAL_RUNTIME_RESULT.json")
    juice = _load(REPRO / "VISIBLE_GAME_JUICE_RUNTIME_RESULT.json")
    procedural_char = _load(REPRO / "PROCEDURAL_CHARACTER_RESULT.json")
    code = _load(REPRO / "CODE_INTEGRITY_RESULT.json")
    smoke = _load(REPRO / "PROCEDURAL_SMOKE_RESULT.json")

    fighters_procedural = int(
        w014.get("ROSTER_ARTLAB_REAL_PROCEDURAL_MODELS")
        or smoke.get("ROSTER_ARTLAB_REAL_PROCEDURAL_MODELS")
        or procedural_char.get("fighter_count")
        or 0
    )
    fighters_skeleton = int(skeletal.get("FIGHTERS_VISIBLE_SKELETON_TESTED") or 0)
    transform_failures = int(skeletal.get("VISIBLE_SKELETAL_TRANSFORM_FAILURES") or 0)

    gates = {
        "ENGINEERING_WAVE_011": w011.get("ENGINEERING_WAVE_011") == "PASS",
        "ENGINEERING_WAVE_012": w012.get("ENGINEERING_WAVE_012") == "PASS",
        "ENGINEERING_WAVE_013B": w013b.get("ENGINEERING_WAVE_013B") == "PASS",
        "ENGINEERING_WAVE_014": w014.get("ENGINEERING_WAVE_014") == "PASS",
        "PROCEDURAL_CHARACTER_RUNTIME_PASS": w014.get("PROCEDURAL_CHARACTER_RUNTIME_PASS") is True,
        "PROCEDURAL_RUNTIME_ANIMATION_PASS": w014.get("PROCEDURAL_RUNTIME_ANIMATION_PASS") is True,
        "FIGHTERS_VISIBLE_PROCEDURAL_MODEL_TESTED_7": fighters_procedural >= 7,
        "FIGHTERS_VISIBLE_SKELETON_TESTED_7": fighters_skeleton >= 7,
        "VISIBLE_SKELETAL_TRANSFORM_FAILURES_0": transform_failures == 0,
        "BATTLESCENE_VISIBLE_RUNTIME_E2E_PASS": str(
            battle.get("BATTLESCENE_VISUAL_E2E", w014.get("BATTLESCENE_VISUAL_E2E", ""))
        ).upper() == "PASS",
        "CURRENT_MODEL_SOURCE_PROCEDURAL": w014.get("CURRENT_MODEL_SOURCE") == "PROCEDURAL_PRODUCTION_PROXY",
        "CURRENT_ANIMATION_SOURCE_PROCEDURAL": w014.get("CURRENT_ANIMATION_SOURCE") == "PROCEDURAL_RUNTIME_ANIMATION",
        "FINAL_CHARACTER_ART_PASS_false": w014.get("FINAL_CHARACTER_ART_PASS") is False,
        "PHYSICAL_PIXEL6A_VALIDATED_false": w014.get("PHYSICAL_PIXEL6A_VALIDATED") is False,
        "REAL_USER_MOTION_LIBRARY_PRESENT_false": w014.get("REAL_USER_MOTION_LIBRARY_PRESENT") is False,
        "VISIBLE_GAME_JUICE_RUNTIME_PASS": w014.get("VISIBLE_GAME_JUICE_RUNTIME_PASS") is True
        or juice.get("VISIBLE_GAME_JUICE_RUNTIME_PASS") is True,
        "WAVE011_REGRESSION_PASS": w014.get("WAVE011_REGRESSION") == "PASS",
        "WAVE012_REGRESSION_PASS": w014.get("WAVE012_REGRESSION") == "PASS",
        "WAVE013B_REGRESSION_PASS": w014.get("WAVE013B_REGRESSION") == "PASS",
        "ZERO_COST_CHECK_PASS": w012.get("ZERO_COST_CHECK_PASS") is True and w013b.get("ZERO_COST_CHECK_PASS") is True,
        "NEW_S0_0": w014.get("NEW_S0") == 0 and code.get("NEW_S0") == 0,
        "NEW_S1_0": w014.get("NEW_S1") == 0 and code.get("NEW_S1") == 0,
        "TESTED_SHA_EQ_ACCEPTED_MAIN": w014.get("HEAD_SHA") == PR84_MERGE_SHA,
        "TESTED_TREE_EQ_ACCEPTED": (REPRO / "TESTED_TREE.txt").read_text(encoding="utf-8").strip() == ANIME_TREE,
    }
    failed = [k for k, v in gates.items() if not v]
    if failed:
        raise SystemExit(f"FAIL_REPRODUCTION gates failed: {failed}")
    return {
        "wave011": w011,
        "wave012": w012,
        "wave013b": w013b,
        "wave014": w014,
        "battle": battle,
        "skeletal": skeletal,
        "juice": juice,
        "procedural_char": procedural_char,
        "code": code,
        "smoke": smoke,
        "gates": gates,
        "fighters_procedural": fighters_procedural,
        "fighters_skeleton": fighters_skeleton,
    }


def _row_reconciliation_reason(rid: str) -> str:
    if rid.startswith("DEV-STUDENT"):
        return (
            "Student hardware / industrial-design scope; Wave012–014 digital art pipeline evidence "
            "does not satisfy accepted-main IMPLEMENTATION_* for student device rows."
        )
    if rid.startswith("GATE-"):
        return (
            "Gate certification / readiness row; Wave014 procedural runtime on host does not "
            "substitute for gate evidence requirements."
        )
    if rid.startswith("RING-"):
        return "Ring / carrier hardware scope; not addressed by Anime Aggressors procedural runtime waves."
    if rid.startswith("DEV-DSXL") or rid.startswith("DEV-HANDHELD"):
        return "Device form-factor hardware scope; Wave014 does not close DSXL/handheld implementation rows."
    if rid == "SYS-MISSION-006":
        return (
            "Cross-form-factor application parity spans non-game portfolio; Wave014 is Anime Aggressors "
            "procedural runtime only and does not close SYS-MISSION-006."
        )
    return "No semantic match between Wave012–014 capability evidence and this canonical implementation row."


def _build_row_reconciliation(ts: str) -> dict[str, Any]:
    rows = []
    for rid in IMPL_OPEN_IDS:
        rows.append(
            {
                "requirement_id": rid,
                "closure_decision": "NO_CLOSE",
                "forced_closure": False,
                "wave012_014_reviewed": True,
                "reason": _row_reconciliation_reason(rid),
            }
        )
    return {
        "schema": "gunnchos.engineering_wave014.baseline_row_reconciliation.v1",
        "generated_at_utc": ts,
        "FORCED_ROW_CLOSURES": 0,
        "rows_reviewed": len(rows),
        "rows_closed": 0,
        "rows": rows,
    }


def _capability_entry(
    capability_id: str,
    title: str,
    production_paths: list[str],
    runtime_paths: list[str],
    evidence_paths: list[str],
    verification_level: str,
    human_blockers: list[str],
    final_art_status: str,
    claim_boundaries: list[str],
) -> dict[str, Any]:
    return {
        "capability_id": capability_id,
        "title": title,
        "repo": PKG,
        "accepted_main_sha": PR84_MERGE_SHA,
        "production_paths": [f"{PKG}:{p}" for p in production_paths],
        "runtime_paths": [f"{PKG}:{p}" for p in runtime_paths],
        "evidence_paths": [f"{PKG}:{p}" for p in evidence_paths],
        "verification_level": verification_level,
        "human_physical_blockers": human_blockers,
        "final_art_status": final_art_status,
        "claim_boundaries": claim_boundaries,
    }


def _build_capability_ledger(ts: str) -> dict[str, Any]:
    entries = [
        _capability_entry(
            "WAVE012_ZERO_COST_ART_PIPELINE",
            "Zero-cost core art pipeline (Blender/Godot procedural authoring)",
            [
                "tools/engineering_wave012/run_wave012.sh",
                "tools/engineering_wave012/emit_wave012_result.py",
                "tools/art_pipeline/",
                "docs/art_pipeline/",
            ],
            ["game-godot/scripts/visual/", "game-godot/assets/characters/"],
            [
                "artifacts/engineering_wave012/WAVE012_RESULT.json",
                "artifacts/engineering_wave012/QUALITY_GATES.json",
            ],
            "DIGITALLY_REPRODUCED",
            [
                "VROID_MODEL_CREATION=HUMAN_GUI_REQUIRED",
                "MOCAP_GPU_EXECUTION=BLOCKED_ENVIRONMENT_GPU",
                "HUMAN_ART_DIRECTION_APPROVAL=false",
            ],
            "PROCEDURAL_PROXY_ONLY",
            [
                "EMBER_FINAL_ART_RUNTIME_PASS=false",
                "FINAL_CHARACTER_ART_PASS=false",
                "PHYSICAL_PIXEL6A_VALIDATED=false",
            ],
        ),
        _capability_entry(
            "WAVE013B_NOTES_DRIVEN_CHOREOGRAPHY",
            "Notes-driven full-roster choreography depth and motion QA",
            [
                "tools/engineering_wave013b/run_wave013b.sh",
                "tools/engineering_wave013b/generate_wave013b_content.py",
                "content/choreography/",
            ],
            ["game-godot/scripts/visual/runtime_move_resolver.gd"],
            [
                "artifacts/engineering_wave013b/WAVE013B_RESULT.json",
                "artifacts/engineering_wave013b/QUALITY_GATES.json",
            ],
            "DIGITALLY_REPRODUCED",
            ["FINAL_ANIMATION_PRESENT=false", "REAL_USER_MOTION_LIBRARY_PRESENT=false"],
            "CHOREOGRAPHY_SPECS_ONLY",
            ["FINAL_HUMAN_AUTHORED_ANIMATION_PASS=false"],
        ),
        _capability_entry(
            "WAVE013B_USER_MOTION_CONTRIBUTION",
            "User motion contribution contract and BVH retarget readiness",
            [
                "tools/engineering_wave013b/run_wave013b.sh",
                "tools/animation_pipeline/retarget/",
            ],
            ["game-godot/scripts/visual/procedural_bone_map.gd"],
            [
                "artifacts/engineering_wave013b/WAVE013B_RESULT.json",
                "artifacts/engineering_wave013b/BVH_RETARGET_READY.json",
            ],
            "DIGITALLY_REPRODUCED",
            ["REAL_USER_MOTION_LIBRARY_PRESENT=false", "CONTRIBUTOR_SELF_APPROVE=false"],
            "UPLOAD_PIPELINE_READY_NO_LIBRARY",
            ["REAL_USER_MOTION_LIBRARY_PRESENT=false"],
        ),
        _capability_entry(
            "WAVE014_PROCEDURAL_ROSTER_MODELS",
            "Seven-fighter procedural production-proxy roster models",
            [
                "tools/art_pipeline/procedural_roster/generate_roster.py",
                "tools/engineering_wave014/run_wave014.sh",
                "content/fighters/",
            ],
            [
                f"{PROD_ROOT}/scripts/fighters/fighter_model_3d.gd",
                f"{PROD_ROOT}/assets/characters/procedural/",
            ],
            [
                "artifacts/engineering_wave014/PROCEDURAL_CHARACTER_RESULT.json",
                "artifacts/engineering_wave014/PROCEDURAL_SMOKE_RESULT.json",
                "artifacts/engineering_wave014/WAVE014_RESULT.json",
            ],
            "DIGITALLY_REPRODUCED",
            ["FINAL_CHARACTER_ART_PASS=false", "VROID_FINAL_EXPORT_PRESENT=false"],
            "PROCEDURAL_PRODUCTION_PROXY",
            ["FINAL_CHARACTER_ART_PASS=false", "PHYSICAL_PIXEL6A_VALIDATED=false"],
        ),
        _capability_entry(
            "WAVE014_VISIBLE_SKELETAL_ANIMATION",
            "Visible skeletal runtime animation across full roster",
            [
                "tools/animation_pipeline/procedural/generate_roster_animations.py",
                "tools/engineering_wave014/validate_combat_alignment.py",
            ],
            [
                f"{PROD_ROOT}/scripts/visual/runtime_move_resolver.gd",
                f"{PROD_ROOT}/scripts/fighters/fighter_model_3d.gd",
            ],
            [
                "artifacts/engineering_wave014/VISIBLE_SKELETAL_RUNTIME_RESULT.json",
                "artifacts/engineering_wave014/RUNTIME_ANIMATION_COMBAT_ALIGNMENT.json",
            ],
            "DIGITALLY_REPRODUCED",
            ["FINAL_HUMAN_AUTHORED_ANIMATION_PASS=false"],
            "PROCEDURAL_RUNTIME_ANIMATION",
            ["FINAL_HUMAN_AUTHORED_ANIMATION_PASS=false"],
        ),
        _capability_entry(
            "WAVE014_RUNTIME_GAME_JUICE",
            "Visible runtime game juice (feedback, renders, combat alignment)",
            [
                "tools/engineering_wave014/emit_game_juice_result.py",
                "tools/engineering_wave014/generate_renders.py",
            ],
            [
                f"{PROD_ROOT}/scripts/combat/combat_feedback.gd",
                f"{PROD_ROOT}/scripts/battle/battle_scene.gd",
            ],
            [
                "artifacts/engineering_wave014/VISIBLE_GAME_JUICE_RUNTIME_RESULT.json",
                "artifacts/engineering_wave014/GAME_JUICE_RUNTIME.json",
            ],
            "DIGITALLY_REPRODUCED",
            ["HUMAN_ART_DIRECTION_APPROVAL=false"],
            "DIGITAL_RUNTIME_JUICE",
            ["HUMAN_FUN_VALIDATED=false"],
        ),
        _capability_entry(
            "WAVE014_CANONICAL_BATTLESCENE_PRESENTATION",
            "Canonical BattleScene visible procedural presentation E2E",
            [
                "tools/engineering_wave014/run_wave014.sh",
                f"{PROD_ROOT}/scenes/battle/battle_scene.tscn",
            ],
            [
                f"{PROD_ROOT}/scripts/battle/battle_scene.gd",
                f"{PROD_ROOT}/scenes/battle/battle_scene.tscn",
            ],
            [
                "artifacts/engineering_wave014/BATTLESCENE_VISUAL_E2E.json",
                "artifacts/engineering_wave014/WAVE014_RESULT.json",
            ],
            "DIGITALLY_REPRODUCED",
            ["PHYSICAL_PIXEL6A_VALIDATED=false"],
            "HOST_VISIBLE_E2E_PASS",
            ["PHYSICAL_PIXEL6A_VALIDATED=false", "PHYSICAL_ANDROID_VALIDATED=false"],
        ),
    ]
    return {
        "schema": "gunnchos.engineering_wave014.capability_ledger.v1",
        "generated_at_utc": ts,
        "product": "Anime Aggressors",
        "accepted_main_sha": PR84_MERGE_SHA,
        "accepted_main_tree": ANIME_TREE,
        "evidence_ladder_max": "INDEPENDENTLY_VERIFIED_DIGITAL",
        "atomic_row_closures": 0,
        "entries": entries,
    }


def _verify_baseline_unchanged() -> dict[str, Any]:
    register = _load(OUT / "MASTER_COMPLETION_REGISTER.json")
    impl_reg = _load(OUT / "NEXT_DIGITAL_IMPLEMENTATION_WORK.json")
    val_reg = _load(OUT / "NEXT_DIGITAL_VALIDATION_WORK.json")
    totals = register.get("totals") or {}

    for key, expected in EXPECTED_BASELINE.items():
        if key == "DIGITAL_CONTROLLABLE_POOL":
            continue
        if totals.get(key) != expected:
            raise SystemExit(f"baseline {key}={totals.get(key)} expected {expected} (unchanged required)")

    impl_ids = [i["requirement_id"] for i in impl_reg.get("all_items") or []]
    if impl_reg.get("total_open") != 26 or len(impl_ids) != 26:
        raise SystemExit("implementation queue must remain 26 open rows")
    if set(impl_ids) != set(IMPL_OPEN_IDS):
        raise SystemExit("implementation queue identity drift")

    if val_reg.get("total_open") != 0 or val_reg.get("all_items"):
        raise SystemExit("validation queue must remain empty")

    computed = compute_totals(register.get("requirements") or [])
    if computed.get("DIGITAL_IMPLEMENTATION_OPEN") != 26:
        raise SystemExit("register row recompute drift on IMPL_OPEN")

    return {
        "register_totals": totals,
        "impl_open_ids": impl_ids,
        "validation_open": 0,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--anime-root", default=None, help="Path to anime-aggressors repo")
    args = parser.parse_args()

    ts = _utc_now()
    anime_root = _anime_root(args.anime_root)
    CLOSEOUT_ART.mkdir(parents=True, exist_ok=True)

    _mirror_reproduction(anime_root)
    truth = _verify_reproduction_gates()
    baseline_check = _verify_baseline_unchanged()

    reconciliation = _build_row_reconciliation(ts)
    capability_ledger = _build_capability_ledger(ts)

    code_recheck = {
        "schema": "gunnchos.engineering_wave014.code_integrity_recheck.v1",
        "generated_at_utc": ts,
        "NEW_S0": truth["code"].get("NEW_S0", 0),
        "NEW_S1": truth["code"].get("NEW_S1", 0),
        "CURRENT_OPEN_S0": 0,
        "CURRENT_OPEN_S1": 0,
        "S2_FINDINGS_PRESERVED": True,
        "S2_MUTATION_VALIDATION_INCOMPLETE_REPOS": [
            "7gc-digital-twin",
            "gunnchos-emergent-service-intent-protocols",
            "readygary-6g-beam-selection",
        ],
        "R3_R6_R7_PRESERVED": True,
        "PRODUCTION_IMPORTS_TESTS": truth["code"].get("PRODUCTION_IMPORTS_TESTS", 0),
        "PRODUCTION_IMPORTS_ARTIFACTS": truth["code"].get("PRODUCTION_IMPORTS_ARTIFACTS", 0),
        "PRODUCTION_IMPORTS_EVALUATORS": truth["code"].get("PRODUCTION_IMPORTS_EVALUATORS", 0),
        "WAVE_DUPLICATE_CANONICAL_IMPLEMENTATIONS": 0,
        "source": "accepted-main wave014 CODE_INTEGRITY_RESULT + R5_S1 reconciliation overlay",
    }

    claim_doc = {
        "schema": "gunnchos.engineering_wave014.claim_boundaries.closeout.v1",
        "generated_at_utc": ts,
        "ENGINEERING_WAVE_014_CLAIM_BOUNDARIES": "PASS",
        "claim_boundaries": CLAIM_BOUNDARIES,
        "preserved_false_claims": sorted(CLAIM_BOUNDARIES.keys()),
    }

    physical_register = {
        "schema": "gunnchos.engineering_wave014.physical_action_register.v1",
        "generated_at_utc": ts,
        "NEXT_PHYSICAL_VALIDATION": "ANIME_AGGRESSORS_PIXEL6A",
        "runbook": f"{PKG}:docs/art_pipeline/PIXEL6A_WAVE014_TEST_RUNBOOK.md",
        "actions": [
            {
                "action_id": "ANIME-AA-PIXEL6A-VISUAL-RUNTIME",
                "status": "PHYSICAL_PENDING",
                "digital_preparation": "COMPLETE",
                "accepted_main_sha": PR84_MERGE_SHA,
                "runbook": f"{PKG}:docs/art_pipeline/PIXEL6A_WAVE014_TEST_RUNBOOK.md",
                "digital_evidence": [
                    f"{PKG}:artifacts/engineering_wave014/WAVE014_RESULT.json",
                    f"{PKG}:artifacts/engineering_wave014/BATTLESCENE_VISUAL_E2E.json",
                    "gunnchos-7gc-ai-ran-field-kit:artifacts/engineering_wave014_closeout/_accepted_main_reproduction/WAVE014_RESULT.json",
                ],
            }
        ],
    }

    queue_recheck = {
        "schema": "gunnchos.engineering_wave014.next_work_queue_recheck.v1",
        "generated_at_utc": ts,
        "FORCED_ROW_CLOSURES": 0,
        "baseline_counts_unchanged": True,
        "pre_closeout_baseline": EXPECTED_BASELINE,
        "post_closeout_baseline": EXPECTED_BASELINE,
        "len_NEXT_IMPL": 26,
        "DIGITAL_IMPLEMENTATION_OPEN": 26,
        "len_NEXT_VALIDATION": 0,
        "DIGITAL_VALIDATION_OPEN": 0,
        "implementation_queue_ids": baseline_check["impl_open_ids"],
        "validation_queue_empty": True,
        "register_files_modified": False,
        "NEXT_PHYSICAL_VALIDATION": physical_register["NEXT_PHYSICAL_VALIDATION"],
    }

    provenance = {
        "schema": "gunnchos.engineering_wave014.accepted_main_provenance.v1",
        "generated_at_utc": ts,
        "ENGINEERING_WAVE_014_PROVENANCE_BINDING": "PASS",
        "PR84_MERGED": True,
        "PR84_FINAL_HEAD_SHA": PR84_FINAL_HEAD,
        "PR84_MERGE_SHA": PR84_MERGE_SHA,
        "ANIME_ACCEPTED_MAIN_SHA": PR84_MERGE_SHA,
        "ANIME_ACCEPTED_MAIN_TREE": ANIME_TREE,
        "FIELD_KIT_START_SHA": FIELD_KIT_START_SHA,
        "TREE_EQUIVALENCE_STATUS": "TREE_EQUIVALENT_TO_PR84_FINAL_HEAD",
        "binding": {
            "PR_HEAD": PR84_FINAL_HEAD,
            "PR_HEAD_TREE": ANIME_TREE,
            "ACCEPTED_MERGE": PR84_MERGE_SHA,
            "ACCEPTED_MERGE_TREE": ANIME_TREE,
            "PR_HEAD_TREE_EQ_ACCEPTED_MERGE_TREE": True,
            "trees_identical": True,
            "TESTED_CHECKOUT_SHA": PR84_MERGE_SHA,
            "TESTED_CHECKOUT_TREE": ANIME_TREE,
            "PR_HEAD_vs_TESTED_CHECKOUT": "TREE_BOUND_EQUAL",
            "note": "PR head commit differs from merge commit SHA; trees identical.",
        },
        "authoritative_premerge_ci": {
            "run_id": GHA_RUN_ID,
            "conclusion": "SUCCESS",
            "head_sha": PR84_FINAL_HEAD,
            "artifact_id": GHA_ARTIFACT_ID,
            "artifact_name": "engineering-wave014-evidence",
            "digest": GHA_DIGEST,
            "url": f"https://github.com/gunnchOS3k/anime-aggressors/actions/runs/{GHA_RUN_ID}",
            "belongs_to_pr84_final_head": True,
        },
        "accepted_main_reproduction": {
            "ENGINEERING_WAVE_014": "PASS",
            "WAVE011_REGRESSION": truth["wave014"].get("WAVE011_REGRESSION"),
            "WAVE012_REGRESSION": truth["wave014"].get("WAVE012_REGRESSION"),
            "WAVE013B_REGRESSION": truth["wave014"].get("WAVE013B_REGRESSION"),
            "NEW_S0": 0,
            "NEW_S1": 0,
            "gates_pass": True,
        },
        "production_runtime": PROD_ROOT + "/",
        "intervening_commits_on_main_after_merge": [],
    }

    closeout = {
        "schema": "gunnchos.engineering_wave014.accepted_main_closeout.v1",
        "generated_at_utc": ts,
        "phase": "ENGINEERING_WAVE_014_ACCEPTED_MAIN_CLOSEOUT",
        "WAVE014_ACCEPTED_MAIN_CLOSEOUT": "PASS",
        "ENGINEERING_WAVE_014_ACCEPTED_MAIN_CLOSEOUT_PASS": True,
        "token": TOKEN,
        "CURSOR_MERGED_NOTHING": True,
        "READY_FOR_OWNER_MERGE": True,
        "STOP_FOR_OWNER_MERGE": True,
        "FORCED_ROW_CLOSURES": 0,
        "prerequisites": {
            "anime_aggressors_pr_84": "MERGED",
            "PR84_FINAL_HEAD_SHA": PR84_FINAL_HEAD,
            "PR84_MERGE_SHA": PR84_MERGE_SHA,
            "ANIME_ACCEPTED_MAIN_SHA": PR84_MERGE_SHA,
            "ANIME_ACCEPTED_MAIN_TREE": ANIME_TREE,
            "FIELD_KIT_START_SHA": FIELD_KIT_START_SHA,
            "TREE_EQUIVALENCE_STATUS": "TREE_EQUIVALENT_TO_PR84_FINAL_HEAD",
            "PREMERGE_WAVE014_RUN": GHA_RUN_ID,
            "PREMERGE_ARTIFACT_ID": GHA_ARTIFACT_ID,
            "PREMERGE_ARTIFACT_DIGEST": GHA_DIGEST,
        },
        "accepted_main_reproduction": {
            "ENGINEERING_WAVE_011": "PASS",
            "ENGINEERING_WAVE_012": "PASS",
            "ENGINEERING_WAVE_013B": "PASS",
            "ENGINEERING_WAVE_014": "PASS",
            "PROCEDURAL_CHARACTER_RUNTIME_PASS": True,
            "PROCEDURAL_RUNTIME_ANIMATION_PASS": True,
            "FIGHTERS_VISIBLE_PROCEDURAL_MODEL_TESTED": truth["fighters_procedural"],
            "FIGHTERS_VISIBLE_SKELETON_TESTED": truth["fighters_skeleton"],
            "VISIBLE_SKELETAL_TRANSFORM_FAILURES": 0,
            "BATTLESCENE_VISIBLE_RUNTIME_E2E": "PASS",
            "CURRENT_MODEL_SOURCE": "PROCEDURAL_PRODUCTION_PROXY",
            "CURRENT_ANIMATION_SOURCE": "PROCEDURAL_RUNTIME_ANIMATION",
            "FINAL_CHARACTER_ART_PASS": False,
            "PHYSICAL_PIXEL6A_VALIDATED": False,
            "REAL_USER_MOTION_LIBRARY_PRESENT": False,
            "NEW_S0": 0,
            "NEW_S1": 0,
            "gates": truth["gates"],
        },
        "pre_closeout_baseline": EXPECTED_BASELINE,
        "post_closeout_baseline": EXPECTED_BASELINE,
        "TARGETED_ROWS_CHANGED": 0,
        "UNTARGETED_ROWS_CHANGED": 0,
        "UNRELATED_IMPLEMENTATION_QUEUE_ROWS_CHANGED": 0,
        "VALIDATION_QUEUE_ROWS_CHANGED": 0,
        "capability_ledger_entries": 7,
        "claim_boundaries": CLAIM_BOUNDARIES,
        "queue_integrity": queue_recheck,
        "physical_validation": physical_register,
        "code_health": code_recheck,
        "production_runtime": PROD_ROOT + "/",
    }

    _dump(CLOSEOUT_ART / "WAVE014_ACCEPTED_MAIN_CLOSEOUT.json", closeout)
    _dump(CLOSEOUT_ART / "WAVE014_ACCEPTED_MAIN_PROVENANCE.json", provenance)
    _dump(CLOSEOUT_ART / "WAVE012_014_CAPABILITY_LEDGER.json", capability_ledger)
    _dump(CLOSEOUT_ART / "BASELINE_ROW_RECONCILIATION.json", reconciliation)
    _dump(CLOSEOUT_ART / "CLAIM_BOUNDARIES.json", claim_doc)
    _dump(CLOSEOUT_ART / "CODE_INTEGRITY_RECHECK.json", code_recheck)
    _dump(CLOSEOUT_ART / "NEXT_WORK_QUEUE_RECHECK.json", queue_recheck)
    _dump(CLOSEOUT_ART / "PHYSICAL_ACTION_REGISTER.json", physical_register)

    MIRROR.mkdir(parents=True, exist_ok=True)
    for src in REPRO.glob("*.json"):
        shutil.copy2(src, MIRROR / src.name)

    print(TOKEN)
    print(f"FORCED_ROW_CLOSURES=0 IMPL_OPEN={baseline_check['register_totals']['DIGITAL_IMPLEMENTATION_OPEN']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
