#!/usr/bin/env python3
"""Engineering Wave 001 targeted closeout — update 14 register rows only."""

from __future__ import annotations

import copy
import json
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "program" / "digital_ecosystem_baseline_v2"
CLOSEOUT_ART = ROOT / "artifacts" / "engineering_wave001_closeout"
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from baseline_v2_evidence_census import build_end_goal_matrix, compute_totals  # noqa: E402
from validate_baseline_v2_b4_register_integrity import main as validate_b41  # noqa: E402

TARGET_IDS = [
    "FULL-OPS-017",
    *[f"GAME-CROSS-{i:03d}" for i in range(1, 12)],
    "GATE-1-005",
    "SYS-MISSION-006",
]

ACCEPTED_MAIN = {
    "gunnchos-7gc-ai-ran-field-kit": "a8396cd01797cbd01209a5e449bd110ced82b7fc",
    "anime-aggressors": "0afe3079db474fcfd75cd8a40659e96a5867b8fc",
    "pedestrian-pursuit": "3f8fdb5f0f2f6459e42cd38cf0e067084a7a0791",
    "archive-of-life-artifact-world": "3e638fea1500019a423b2d85fa2136ca7b12ee21",
    "beatlink-party": "8ed975bafc228e9730238333163e9cf8ee9c6930",
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
)

GAME_IMPL = (
    "anime-aggressors:game-godot/scripts/cross_device/CrossDeviceContractProvider.gd;"
    "pedestrian-pursuit:scripts/cross_device/CrossDeviceContractProvider.gd;"
    "archive-of-life-artifact-world:gate1/tools/export_cross_device_contract.ts;"
    "beatlink-party:gate1/cross_device/contractProvider.ts"
)

GAME_VAL = (
    "gunnchos-7gc-ai-ran-field-kit:artifacts/engineering_wave001/PARITY_MATRIX.json;"
    "gunnchos-7gc-ai-ran-field-kit:tests/engineering_wave001/test_cross_device_contract.py"
)

COMPLETE_OUTCOMES: dict[str, dict[str, str]] = {
    "FULL-OPS-017": {
        "implementation_evidence": "gunnchos-7gc-ai-ran-field-kit:artifacts/engineering_wave001/FULL_OPS_017_RESULT.json",
        "validation_evidence": (
            "gunnchos-7gc-ai-ran-field-kit:scripts/engineering_wave001/run_full_ops_wave001.py;"
            "gunnchos-7gc-ai-ran-field-kit:tests/engineering_wave001/test_cross_device_contract.py"
        ),
        "resolution_reason": (
            "Wave 001 accepted-main aggregate verifier PASS: four-game cross-device contracts "
            "with operational probes on field-kit main (PR #91)."
        ),
    },
    "GAME-CROSS-001": {
        "implementation_evidence": GAME_IMPL,
        "validation_evidence": GAME_VAL,
        "resolution_reason": "Four-game capability_model parity/adaptation in accepted-main cross-device contracts.",
    },
    "GAME-CROSS-002": {
        "implementation_evidence": GAME_IMPL,
        "validation_evidence": (
            "gunnchos-7gc-ai-ran-field-kit:artifacts/engineering_wave001/PARITY_MATRIX.json#rules_parity"
        ),
        "resolution_reason": "Canonical rules_version/hash surface stable per game in accepted-main contracts.",
    },
    "GAME-CROSS-003": {
        "implementation_evidence": GAME_IMPL,
        "validation_evidence": GAME_VAL,
        "resolution_reason": "save_roundtrip probe PASS on accepted-main contracts (all four games).",
    },
    "GAME-CROSS-004": {
        "implementation_evidence": GAME_IMPL,
        "validation_evidence": GAME_VAL,
        "resolution_reason": "score probe PASS on accepted-main contracts (all four games).",
    },
    "GAME-CROSS-005": {
        "implementation_evidence": GAME_IMPL,
        "validation_evidence": GAME_VAL,
        "resolution_reason": (
            "deterministic_replay probe PASS or not_applicable with honest boundaries "
            "(archive single-player)."
        ),
    },
    "GAME-CROSS-006": {
        "implementation_evidence": GAME_IMPL,
        "validation_evidence": GAME_VAL,
        "resolution_reason": (
            "multiplayer probe PASS or not_applicable; archive honestly N/A for solo exploration."
        ),
    },
    "GAME-CROSS-007": {
        "implementation_evidence": GAME_IMPL,
        "validation_evidence": GAME_VAL,
        "resolution_reason": "accessibility probe PASS with setting mechanisms in accepted-main contracts.",
    },
    "GAME-CROSS-008": {
        "implementation_evidence": GAME_IMPL,
        "validation_evidence": GAME_VAL,
        "resolution_reason": "input/action probe PASS with normalized bindings in accepted-main contracts.",
    },
    "GAME-CROSS-009": {
        "implementation_evidence": GAME_IMPL,
        "validation_evidence": GAME_VAL,
        "resolution_reason": "presentation probe PASS with device-role presentation profiles on accepted main.",
    },
    "GAME-CROSS-010": {
        "implementation_evidence": (
            "anime-aggressors:game-godot/scripts/input/InputPersistenceService.gd;"
            "archive-of-life-artifact-world:src/systems/inputBindings.ts;"
            "pedestrian-pursuit:scripts/cross_device/CrossDeviceContractProvider.gd;"
            "beatlink-party:gate1/cross_device/contractProvider.ts"
        ),
        "validation_evidence": GAME_VAL,
        "resolution_reason": (
            "Remapping persistence in anime+archive; profile/layout behavior validated in "
            "pedestrian+beatlink accepted-main contracts. PIXEL_REMAPPING_RESTART_VERIFY remains "
            "BLOCKED_AUTOMATION."
        ),
    },
    "GAME-CROSS-011": {
        "implementation_evidence": GAME_IMPL,
        "validation_evidence": GAME_VAL,
        "resolution_reason": "quality/presentation tier probe PASS without gameplay semantic downgrade.",
    },
    "GATE-1-005": {
        "implementation_evidence": (
            "anime-aggressors:gate1/tools/core_loop_runner.mjs;"
            "pedestrian-pursuit:gate1/tools/core_loop_runner.py;"
            "archive-of-life-artifact-world:gate1/tools/core_loop_runner.mjs;"
            "beatlink-party:gate1/tools/core_loop_runner.ts"
        ),
        "validation_evidence": GAME_VAL,
        "resolution_reason": (
            "core_loop probe PASS on accepted main for all four games. "
            "PIXEL_6A_DEVICE_CORE_LOOP=NOT_PROVEN (install/launch smoke only)."
        ),
    },
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _semantic_snapshot(row: dict[str, Any]) -> dict[str, Any]:
    return {k: row.get(k) for k in SEMANTIC_FIELDS}


def _apply_complete(row: dict[str, Any], rid: str) -> None:
    spec = COMPLETE_OUTCOMES[rid]
    row["work_state"] = "DIGITAL_IMPLEMENTATION_COMPLETE"
    row["resolution"] = "DIGITAL_IMPLEMENTATION_COMPLETE"
    row["engineering_state"] = "DIGITAL_IMPLEMENTATION_COMPLETE"
    row["implementation_state"] = "IMPLEMENTED"
    row["verification_state"] = "NOT_VERIFIED"
    row["current_level"] = "L1_IMPLEMENTED"
    row["accepted_main_sha"] = ACCEPTED_MAIN["gunnchos-7gc-ai-ran-field-kit"]
    row["implementation_evidence"] = spec["implementation_evidence"]
    row["validation_evidence"] = spec["validation_evidence"]
    row["token_or_result"] = "PASS"
    row["evidence_confidence"] = "MEDIUM"
    row["resolution_reason"] = spec["resolution_reason"]
    row["next_action"] = "Owner may advance digital validation or human/device proof when ready."
    row.pop("specific_missing_implementation", None)
    row.pop("why_paths_insufficient", None)


def _apply_sys_mission_partial(row: dict[str, Any]) -> None:
    row["work_state"] = "DIGITAL_IMPLEMENTATION_OPEN"
    row["resolution"] = "DIGITAL_IMPLEMENTATION_OPEN"
    row["engineering_state"] = "DIGITAL_IMPLEMENTATION_OPEN"
    row["implementation_state"] = "NOT_IMPLEMENTED"
    row["verification_state"] = "NOT_VERIFIED"
    row["current_level"] = "L0_DEFINED"
    row["accepted_main_sha"] = ACCEPTED_MAIN["gunnchos-7gc-ai-ran-field-kit"]
    row["implementation_evidence"] = ""
    row["validation_evidence"] = (
        "gunnchos-7gc-ai-ran-field-kit:artifacts/engineering_wave001/PARITY_MATRIX.json"
    )
    row["token_or_result"] = "PARTIAL_SLICE"
    row["evidence_confidence"] = "MEDIUM"
    row["resolution_reason"] = (
        "Wave 001 proves four-game cross-form-factor application parity only. Residual scope "
        "includes gunnchAI, gunnchOS shell, WAIKE, and non-game apps — not over-closed."
    )
    row["next_action"] = (
        "Extend cross-form-factor parity beyond the four Wave 001 games; preserve honest residual."
    )
    row["specific_missing_implementation"] = (
        "Non-game application parity (gunnchAI, gunnchOS/device-os shell, WAIKE, portal) beyond "
        "Wave 001 four-game contract slice on accepted main."
    )
    row["why_paths_insufficient"] = (
        "PARITY_MATRIX covers anime-aggressors, pedestrian-pursuit, archive-of-life-artifact-world, "
        "beatlink-party only; SYS-MISSION-006 spans broader application portfolio."
    )


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


def _write_md_register(rows: list[dict[str, Any]], totals: dict[str, int], path: Path) -> None:
    lines = [
        "# Master completion register (Wave 001 targeted closeout)",
        "",
        f"Generated: {_utc_now()}",
        "",
        f"- ATOMIC_TOTAL: {totals['ATOMIC_TOTAL']}",
        f"- DIGITAL_IMPLEMENTATION_COMPLETE: {totals['DIGITAL_IMPLEMENTATION_COMPLETE']}",
        f"- DIGITAL_IMPLEMENTATION_OPEN: {totals['DIGITAL_IMPLEMENTATION_OPEN']}",
        f"- DIGITAL_VALIDATION_OPEN: {totals['DIGITAL_VALIDATION_OPEN']}",
        "",
    ]
    for row in rows:
        if row["requirement_id"] in TARGET_IDS:
            lines.append(
                f"- **{row['requirement_id']}** — {row['work_state']} — {row.get('resolution_reason', '')[:120]}"
            )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_work_md(items: list[dict[str, Any]], title: str, path: Path) -> None:
    lines = [f"# {title}", "", f"Count: {len(items)}", ""]
    for it in items[:50]:
        lines.append(f"- {it['requirement_id']}: {it.get('title', '')}")
    if len(items) > 50:
        lines.append(f"- … and {len(items) - 50} more")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _validate_closeout(
    before_rows: dict[str, dict[str, Any]],
    after_rows: dict[str, dict[str, Any]],
    diff: dict[str, Any],
) -> dict[str, Any]:
    errors: list[str] = []
    for tid in TARGET_IDS:
        if tid not in after_rows:
            errors.append(f"missing target {tid}")
    for rid, before in before_rows.items():
        if rid in TARGET_IDS:
            continue
        if _semantic_snapshot(before) != _semantic_snapshot(after_rows[rid]):
            errors.append(f"untargeted semantic change: {rid}")
    if diff.get("unexpected_changed_ids"):
        errors.append(f"unexpected_changed_ids={diff['unexpected_changed_ids']}")
    if diff.get("untargeted_rows_changed", -1) != 0:
        errors.append(f"untargeted_rows_changed={diff.get('untargeted_rows_changed')}")
    for key in (
        "PIXEL_6A_INSTALL_LAUNCH_SMOKE",
        "PIXEL_6A_DEVICE_CORE_LOOP",
        "PIXEL_REMAPPING_RESTART_VERIFY",
    ):
        if diff.get("pixel_boundaries", {}).get(key) is None:
            errors.append(f"missing pixel boundary {key}")
    ok = len(errors) == 0
    return {
        "ENGINEERING_WAVE_001_TARGETED_CLOSEOUT_VALIDATION_PASS": ok,
        "errors": errors,
        "accepted_main_shas": ACCEPTED_MAIN,
        "pixel_boundaries": diff.get("pixel_boundaries", {}),
    }


def main() -> int:
    ts = _utc_now()
    register_path = OUT / "MASTER_COMPLETION_REGISTER.json"
    register = json.loads(register_path.read_text(encoding="utf-8"))
    before_by_id = {r["requirement_id"]: copy.deepcopy(r) for r in register["requirements"]}

    impl_reg = json.loads((OUT / "NEXT_DIGITAL_IMPLEMENTATION_WORK.json").read_text(encoding="utf-8"))
    val_reg = json.loads((OUT / "NEXT_DIGITAL_VALIDATION_WORK.json").read_text(encoding="utf-8"))
    result = json.loads((OUT / "BASELINE_V2_RESULT.json").read_text(encoding="utf-8"))
    remaining = json.loads((OUT / "REMAINING_GAPS.json").read_text(encoding="utf-8"))

    after_rows: list[dict[str, Any]] = []
    changed_ids: list[str] = []
    before_states: dict[str, Any] = {}
    after_states: dict[str, Any] = {}

    for row in register["requirements"]:
        rid = row["requirement_id"]
        new_row = copy.deepcopy(row)
        if rid not in TARGET_IDS:
            after_rows.append(new_row)
            continue
        before_states[rid] = _semantic_snapshot(row)
        if rid == "SYS-MISSION-006":
            _apply_sys_mission_partial(new_row)
        else:
            _apply_complete(new_row, rid)
        after_states[rid] = _semantic_snapshot(new_row)
        if before_states[rid] != after_states[rid]:
            changed_ids.append(rid)
        after_rows.append(new_row)

    after_by_id = {r["requirement_id"]: r for r in after_rows}
    untargeted_changed = 0
    unexpected: list[str] = []
    for rid, before in before_by_id.items():
        if rid in TARGET_IDS:
            continue
        if _semantic_snapshot(before) != _semantic_snapshot(after_by_id[rid]):
            untargeted_changed += 1
            unexpected.append(rid)

    totals = compute_totals(after_rows)
    work_state_counts = Counter(r["work_state"] for r in after_rows)
    end_goal = build_end_goal_matrix(after_rows)

    impl_open_rows = [r for r in after_rows if r["work_state"] == "DIGITAL_IMPLEMENTATION_OPEN"]
    val_open_rows = [r for r in after_rows if r["work_state"] == "DIGITAL_VALIDATION_OPEN"]
    impl_items = [_impl_work_item(r) for r in impl_open_rows]
    val_items = [
        {
            "requirement_id": r["requirement_id"],
            "title": r["title"],
            "owner_repo": r.get("owner_repo"),
            "primary_end_goal_family": r.get("primary_end_goal_family"),
            "implementation_evidence": r.get("implementation_evidence"),
            "validation_evidence": r.get("validation_evidence"),
            "next_action": r.get("next_action"),
        }
        for r in val_open_rows
    ]

    pixel = {
        "PIXEL_6A_INSTALL_LAUNCH_SMOKE": "4/4",
        "PIXEL_6A_DEVICE_CORE_LOOP": "NOT_PROVEN",
        "PIXEL_REMAPPING_RESTART_VERIFY": "BLOCKED_AUTOMATION",
        "HUMAN_PLAYTEST": False,
        "FUN_VALIDATED": False,
        "BALANCE_VALIDATED": False,
    }

    diff_doc = {
        "schema": "gunnchos.engineering_wave001.targeted_row_diff.v1",
        "generated_at_utc": ts,
        "wave": "ENGINEERING_WAVE_001",
        "target_ids": TARGET_IDS,
        "changed_ids": changed_ids,
        "unexpected_changed_ids": unexpected,
        "untargeted_rows_changed": untargeted_changed,
        "before_state": before_states,
        "after_state": after_states,
        "accepted_main_evidence": {
            "merge_prs": {
                "anime-aggressors": {"pr": 80, "merge_commit": ACCEPTED_MAIN["anime-aggressors"]},
                "pedestrian-pursuit": {"pr": 21, "merge_commit": ACCEPTED_MAIN["pedestrian-pursuit"]},
                "archive-of-life-artifact-world": {"pr": 34, "merge_commit": ACCEPTED_MAIN["archive-of-life-artifact-world"]},
                "beatlink-party": {"pr": 24, "merge_commit": ACCEPTED_MAIN["beatlink-party"]},
                "gunnchos-7gc-ai-ran-field-kit": {"pr": 91, "merge_commit": ACCEPTED_MAIN["gunnchos-7gc-ai-ran-field-kit"]},
            },
            "accepted_main_shas": ACCEPTED_MAIN,
            "aggregate_artifacts": [
                "artifacts/engineering_wave001/FULL_OPS_017_RESULT.json",
                "artifacts/engineering_wave001/PARITY_MATRIX.json",
            ],
            "validation_rerun": {
                "field_kit_pytest": "5 passed (tests/engineering_wave001/test_cross_device_contract.py)",
                "game_ci_main": "success on accepted main for all four games + field-kit",
            },
        },
        "pixel_boundaries": pixel,
        "closeout_assessment": {
            "targets_digital_implementation_complete": [
                rid for rid in TARGET_IDS if after_by_id[rid]["work_state"] == "DIGITAL_IMPLEMENTATION_COMPLETE"
            ],
            "targets_remaining_open": [
                rid for rid in TARGET_IDS if after_by_id[rid]["work_state"] == "DIGITAL_IMPLEMENTATION_OPEN"
            ],
        },
    }

    closeout_validation = _validate_closeout(before_by_id, after_by_id, diff_doc)

    register["generated_at_utc"] = ts
    register["totals"] = totals
    register["requirements"] = after_rows
    register["wave001_targeted_closeout"] = {
        "phase": "ENGINEERING_WAVE_001_TARGETED_CLOSEOUT",
        "targets_changed": len(changed_ids),
        "accepted_main_shas": ACCEPTED_MAIN,
    }
    (OUT / "MASTER_COMPLETION_REGISTER.json").write_text(json.dumps(register, indent=2) + "\n", encoding="utf-8")
    _write_md_register(after_rows, totals, OUT / "MASTER_COMPLETION_REGISTER.md")

    impl_reg["generated_at_utc"] = ts
    impl_reg["total_open"] = totals["DIGITAL_IMPLEMENTATION_OPEN"]
    impl_reg["all_items"] = impl_items
    impl_reg["top_priority_items"] = impl_items[:25]
    (OUT / "NEXT_DIGITAL_IMPLEMENTATION_WORK.json").write_text(json.dumps(impl_reg, indent=2) + "\n", encoding="utf-8")
    _write_work_md(impl_items, "Next digital implementation work", OUT / "NEXT_DIGITAL_IMPLEMENTATION_WORK.md")

    val_reg["generated_at_utc"] = ts
    val_reg["total_open"] = totals["DIGITAL_VALIDATION_OPEN"]
    val_reg["all_items"] = val_items
    val_reg["top_priority_items"] = val_items[:25]
    (OUT / "NEXT_DIGITAL_VALIDATION_WORK.json").write_text(json.dumps(val_reg, indent=2) + "\n", encoding="utf-8")
    _write_work_md(val_items, "Next digital validation work", OUT / "NEXT_DIGITAL_VALIDATION_WORK.md")

    remaining["generated_at_utc"] = ts
    remaining["top_blockers"] = [
        "Wave 001 closeout draft PR pending owner merge",
        "portal Phase-C snapshot refresh from LATEST stale references",
        f"DIGITAL_IMPLEMENTATION_OPEN={totals['DIGITAL_IMPLEMENTATION_OPEN']} rows need digital engineering",
        f"DIGITAL_VALIDATION_OPEN={totals['DIGITAL_VALIDATION_OPEN']} rows need verification/reproduction",
        "SYS-MISSION-006 residual non-game application parity beyond four-game slice",
        "gunnchAI Product Completion 002 blocked on 8GB host",
    ]
    remaining["wave001_closeout"] = {
        "targets_closed": diff_doc["closeout_assessment"]["targets_digital_implementation_complete"],
        "targets_still_open": diff_doc["closeout_assessment"]["targets_remaining_open"],
        "pixel_boundaries": pixel,
    }
    (OUT / "REMAINING_GAPS.json").write_text(json.dumps(remaining, indent=2) + "\n", encoding="utf-8")
    (OUT / "REMAINING_GAPS.md").write_text(
        "# Remaining gaps (Wave 001 closeout)\n\n"
        + "\n".join(f"- {b}" for b in remaining["top_blockers"])
        + "\n",
        encoding="utf-8",
    )

    (OUT / "END_GOAL_COVERAGE_MATRIX.json").write_text(json.dumps(end_goal, indent=2) + "\n", encoding="utf-8")
    fam1 = next(f for f in end_goal["families"] if f["id"] == 1)
    (OUT / "END_GOAL_COVERAGE_MATRIX.md").write_text(
        f"# End goal coverage (family 1 snapshot)\n\n"
        f"- digital_impl_open: {fam1['digital_impl_open']}\n"
        f"- DIGITAL_IMPLEMENTATION_COMPLETE in family: {fam1['work_state_counts'].get('DIGITAL_IMPLEMENTATION_COMPLETE', 0)}\n"
        f"- family_release_level: {fam1['family_release_level']}\n",
        encoding="utf-8",
    )

    result["generated_at_utc"] = ts
    result["phase"] = "ENGINEERING_WAVE_001_TARGETED_CLOSEOUT"
    result["totals"] = totals
    result["work_state_counts"] = dict(work_state_counts)
    result["ENGINEERING_WAVE_001_TARGETED_CLOSEOUT"] = closeout_validation
    result["wave001_pixel_boundaries"] = pixel
    result["BASELINE_V2_STATE"] = "DRAFT_PR"
    result["STOP_FOR_OWNER_MERGE"] = True
    result["BASELINE_V2_READY_FOR_OWNER_MERGE"] = closeout_validation["ENGINEERING_WAVE_001_TARGETED_CLOSEOUT_VALIDATION_PASS"]
    (OUT / "BASELINE_V2_RESULT.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    CLOSEOUT_ART.mkdir(parents=True, exist_ok=True)
    diff_doc["closeout_validation"] = closeout_validation
    (CLOSEOUT_ART / "TARGETED_ROW_DIFF.json").write_text(json.dumps(diff_doc, indent=2) + "\n", encoding="utf-8")

    print(json.dumps({"totals": totals, "closeout_validation": closeout_validation}, indent=2))

    if not closeout_validation["ENGINEERING_WAVE_001_TARGETED_CLOSEOUT_VALIDATION_PASS"]:
        return 1
    rc = validate_b41()
    if rc != 0:
        return rc
    print("ENGINEERING_WAVE_001_TARGETED_CLOSEOUT_VALIDATION_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
