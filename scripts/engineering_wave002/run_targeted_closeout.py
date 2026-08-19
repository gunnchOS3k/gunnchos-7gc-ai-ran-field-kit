#!/usr/bin/env python3
"""Engineering Wave 002 targeted closeout — update 14 register rows only."""

from __future__ import annotations

import copy
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "program" / "digital_ecosystem_baseline_v2"
CLOSEOUT_ART = ROOT / "artifacts" / "engineering_wave002_closeout"
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from baseline_v2_evidence_census import build_end_goal_matrix, compute_totals  # noqa: E402
from validate_baseline_v2_b4_register_integrity import main as validate_b41  # noqa: E402

TARGET_IDS = [
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
]

ACCEPTED_MAIN = {
    "gunnchos-device-os": "ed3c3c93c7d3b100172eb6cab2de61989ccd7ff5",
    "gunnchos-7gc-ai-ran-field-kit": "ea60f61a24cde4f6e8aff85708d9d5ddd7b20d14",
}

WAVE002_VAL = (
    "gunnchos-device-os:artifacts/engineering_wave002/WAVE002_RESULT.json;"
    "gunnchos-device-os:tests/test_wave002_shell_continuity.py"
)

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

COMPLETE_OUTCOMES: dict[str, dict[str, Any]] = {
    "OS-PLATFORM-001": {
        "implementation_evidence": "gunnchos-device-os:gunnchos_device_os/shell/identity_store.py",
        "validation_evidence": WAVE002_VAL,
        "resolution_reason": (
            "Wave 002 accepted-main: local-first identity store with persistence and "
            "tests on device-os main (PR #123)."
        ),
        "pending_dimensions": [],
    },
    "OS-PLATFORM-002": {
        "implementation_evidence": "gunnchos-device-os:gunnchos_device_os/shell/hal_registry.py",
        "validation_evidence": WAVE002_VAL,
        "resolution_reason": (
            "Wave 002 accepted-main: HAL registry with provenance enum and tests on device-os main."
        ),
        "pending_dimensions": [],
    },
    "OS-PLATFORM-003": {
        "implementation_evidence": (
            "gunnchos-device-os:gunnchos_device_os/shell/shell_profiles.py;"
            "gunnchos-device-os:gunnchos_device_os/shell/coordinator.py;"
            "gunnchos-device-os:gunnchos_device_os/shell/display_dock_manager.py"
        ),
        "validation_evidence": WAVE002_VAL,
        "resolution_reason": (
            "Wave 002 accepted-main: six form-factor shell profiles wired to stage2 shell "
            "and display manager with vertical-slice tests."
        ),
        "pending_dimensions": [],
    },
    "OS-PLATFORM-004": {
        "implementation_evidence": "gunnchos-device-os:gunnchos_device_os/shell/ring_service.py",
        "validation_evidence": WAVE002_VAL,
        "resolution_reason": (
            "Wave 002 accepted-main: ring service integrates authenticated adapter with digital "
            "tests. PHYSICAL_RING_E6=false — physical ring validation remains owner/hardware pending; "
            "does not keep digital implementation open."
        ),
        "pending_dimensions": ["PHYSICAL"],
        "next_level_blocker": "PHYSICAL",
    },
    "OS-PLATFORM-005": {
        "implementation_evidence": "gunnchos-device-os:gunnchos_device_os/shell/input_routing.py",
        "validation_evidence": WAVE002_VAL,
        "resolution_reason": (
            "Wave 002 accepted-main: normalized touch/controller/kbm/ring routing with remap "
            "persistence and tests."
        ),
        "pending_dimensions": [],
    },
    "OS-PLATFORM-006": {
        "implementation_evidence": "gunnchos-device-os:gunnchos_device_os/shell/display_dock_manager.py",
        "validation_evidence": (
            WAVE002_VAL + ";"
            "gunnchos-device-os:artifacts/product_use/journeys/G14_dsxl/DSXL_COMPOSITOR_UX_EVIDENCE.json;"
            "gunnchos-device-os:artifacts/wp011r/dsxl/DSXL_COMPOSITOR_UX_EVIDENCE.json"
        ),
        "resolution_reason": (
            "Wave 002 accepted-main: display/dock manager implemented with DS-XL/G14 compositor "
            "evidence linked. DSXL_DUAL_COMPOSITOR_UX_PASS=false and PHYSICAL_DUAL_PANEL=PENDING "
            "are physical/validation dimensions — digital service implementation is complete on main."
        ),
        "pending_dimensions": ["PHYSICAL"],
        "next_level_blocker": "PHYSICAL",
    },
    "OS-PLATFORM-007": {
        "implementation_evidence": "gunnchos-device-os:gunnchos_device_os/shell/continuity_coordinator.py",
        "validation_evidence": WAVE002_VAL,
        "resolution_reason": (
            "Wave 002 accepted-main: continuity checkpoint/restore/revoke/conflict on device-os main."
        ),
        "pending_dimensions": [],
    },
    "OS-CONTINUITY-002": {
        "implementation_evidence": "gunnchos-device-os:gunnchos_device_os/shell/continuity_coordinator.py",
        "validation_evidence": WAVE002_VAL,
        "resolution_reason": "Wave 002 accepted-main: disclosure API — what is synchronized.",
        "pending_dimensions": [],
    },
    "OS-CONTINUITY-003": {
        "implementation_evidence": "gunnchos-device-os:gunnchos_device_os/shell/continuity_coordinator.py",
        "validation_evidence": WAVE002_VAL,
        "resolution_reason": "Wave 002 accepted-main: disclosure API — storage location.",
        "pending_dimensions": [],
    },
    "OS-CONTINUITY-004": {
        "implementation_evidence": "gunnchos-device-os:gunnchos_device_os/shell/continuity_coordinator.py",
        "validation_evidence": WAVE002_VAL,
        "resolution_reason": "Wave 002 accepted-main: disclosure API — authorized devices.",
        "pending_dimensions": [],
    },
    "OS-CONTINUITY-005": {
        "implementation_evidence": "gunnchos-device-os:gunnchos_device_os/shell/continuity_coordinator.py",
        "validation_evidence": WAVE002_VAL,
        "resolution_reason": "Wave 002 accepted-main: disclosure API — local-only fields.",
        "pending_dimensions": [],
    },
    "OS-CONTINUITY-006": {
        "implementation_evidence": "gunnchos-device-os:gunnchos_device_os/shell/continuity_coordinator.py",
        "validation_evidence": WAVE002_VAL,
        "resolution_reason": "Wave 002 accepted-main: disclosure + revoke API.",
        "pending_dimensions": [],
    },
    "OS-CONTINUITY-007": {
        "implementation_evidence": "gunnchos-device-os:gunnchos_device_os/shell/continuity_coordinator.py",
        "validation_evidence": WAVE002_VAL,
        "resolution_reason": "Wave 002 accepted-main: export/delete API.",
        "pending_dimensions": [],
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
    row["accepted_main_sha"] = ACCEPTED_MAIN["gunnchos-device-os"]
    row["implementation_evidence"] = spec["implementation_evidence"]
    row["validation_evidence"] = spec["validation_evidence"]
    row["token_or_result"] = "PASS"
    row["evidence_confidence"] = "MEDIUM"
    row["resolution_reason"] = spec["resolution_reason"]
    row["next_action"] = "Owner may advance digital validation or physical/human proof when ready."
    row["pending_dimensions"] = spec.get("pending_dimensions", [])
    row["next_level_blocker"] = spec.get("next_level_blocker")
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
    row["implementation_evidence"] = (
        "gunnchos-device-os:gunnchos_device_os/shell/parity_probes.py;"
        "gunnchos-7gc-ai-ran-field-kit:artifacts/engineering_wave001/PARITY_MATRIX.json"
    )
    row["validation_evidence"] = (
        "gunnchos-7gc-ai-ran-field-kit:artifacts/engineering_wave001/PARITY_MATRIX.json;"
        "gunnchos-device-os:artifacts/engineering_wave002/WAVE002_RESULT.json#SYS-MISSION-006"
    )
    row["token_or_result"] = "PARTIAL_SLICE"
    row["evidence_confidence"] = "MEDIUM"
    row["resolution_reason"] = (
        "Wave 001 closed four-game parity; Wave 002 adds shell/gunnchAI/WAIKE runtime probes on "
        "accepted-main device-os but not full cross-app UI parity — residual non-game scope "
        "honestly remains open."
    )
    row["next_action"] = (
        "Extend cross-form-factor application parity beyond Wave 001 games + Wave 002 shell probes; "
        "include portal and remaining non-game apps."
    )
    row["specific_missing_implementation"] = (
        "Full cross-app UI parity for gunnchAI, WAIKE, portal, and remaining non-game applications "
        "beyond Wave 001 four-game contracts and Wave 002 in-repo runtime probes."
    )
    row["why_paths_insufficient"] = (
        "WAVE002_RESULT SYS-MISSION-006=PARTIAL (runtime probes only); PARITY_MATRIX covers four "
        "games only; SYS-MISSION-006 spans broader application portfolio."
    )
    row["pending_dimensions"] = row.get("pending_dimensions") or []


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
        "# Master completion register (Wave 002 targeted closeout)",
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
    totals: dict[str, int],
    impl_items: list[dict[str, Any]],
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
    if len(impl_items) != totals["DIGITAL_IMPLEMENTATION_OPEN"]:
        errors.append(
            f"impl_items_len={len(impl_items)} != DIGITAL_IMPLEMENTATION_OPEN={totals['DIGITAL_IMPLEMENTATION_OPEN']}"
        )
    pixel = diff.get("pixel_boundaries", {})
    for key in ("HUMAN_E6", "PHYSICAL_VALIDATION", "PHYSICAL_RING_E6", "PHYSICAL_DUAL_PANEL"):
        if pixel.get(key) is None:
            errors.append(f"missing pixel boundary {key}")
    ok = len(errors) == 0
    return {
        "ENGINEERING_WAVE_002_TARGETED_CLOSEOUT_VALIDATION_PASS": ok,
        "errors": errors,
        "accepted_main_shas": ACCEPTED_MAIN,
        "pixel_boundaries": pixel,
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
        "PIXEL_CLIENT_PROBE_OK": True,
        "HUMAN_E6": False,
        "PHYSICAL_VALIDATION": False,
        "PHYSICAL_RING_E6": False,
        "PHYSICAL_DUAL_PANEL": "PENDING",
        "scope": "client_paths_only",
        "full_os_image": False,
    }

    diff_doc = {
        "schema": "gunnchos.engineering_wave002.targeted_row_diff.v1",
        "generated_at_utc": ts,
        "wave": "ENGINEERING_WAVE_002",
        "target_ids": TARGET_IDS,
        "changed_ids": changed_ids,
        "unexpected_changed_ids": unexpected,
        "untargeted_rows_changed": untargeted_changed,
        "before_state": before_states,
        "after_state": after_states,
        "accepted_main_evidence": {
            "merge_prs": {
                "gunnchos-device-os": {
                    "pr": 123,
                    "merge_commit": ACCEPTED_MAIN["gunnchos-device-os"],
                },
                "gunnchos-7gc-ai-ran-field-kit": {
                    "pr": 93,
                    "merge_commit": ACCEPTED_MAIN["gunnchos-7gc-ai-ran-field-kit"],
                },
            },
            "accepted_main_shas": ACCEPTED_MAIN,
            "aggregate_artifacts": [
                "artifacts/engineering_wave002/ENGINEERING_WAVE002_AGGREGATE.json",
                "gunnchos-device-os:artifacts/engineering_wave002/WAVE002_RESULT.json",
                "gunnchos-device-os:artifacts/engineering_wave002/PIXEL_CLIENT_PROBE.json",
            ],
            "validation_rerun": {
                "device_os_pytest": "tests/test_wave002_shell_continuity.py",
                "field_kit_aggregate": "tests/engineering_wave002/test_aggregate.py",
            },
        },
        "pixel_boundaries": pixel,
        "closeout_assessment": {
            "targets_digital_implementation_complete": [
                rid
                for rid in TARGET_IDS
                if after_by_id[rid]["work_state"] == "DIGITAL_IMPLEMENTATION_COMPLETE"
            ],
            "targets_remaining_open": [
                rid for rid in TARGET_IDS if after_by_id[rid]["work_state"] == "DIGITAL_IMPLEMENTATION_OPEN"
            ],
            "targets_with_physical_pending_dimension": [
                rid
                for rid in TARGET_IDS
                if "PHYSICAL" in (after_by_id[rid].get("pending_dimensions") or [])
            ],
        },
        "backlog_delta": {
            "DIGITAL_IMPLEMENTATION_OPEN_before": before_by_id["OS-PLATFORM-001"]["work_state"]
            and totals.get("_pre_open", 123),
            "DIGITAL_IMPLEMENTATION_OPEN_after": totals["DIGITAL_IMPLEMENTATION_OPEN"],
            "rows_closed": len(
                [
                    rid
                    for rid in TARGET_IDS
                    if rid != "SYS-MISSION-006"
                    and after_by_id[rid]["work_state"] == "DIGITAL_IMPLEMENTATION_COMPLETE"
                ]
            ),
        },
    }
    diff_doc["backlog_delta"]["DIGITAL_IMPLEMENTATION_OPEN_before"] = sum(
        1 for r in before_by_id.values() if r.get("work_state") == "DIGITAL_IMPLEMENTATION_OPEN"
    )

    closeout_validation = _validate_closeout(
        before_by_id, after_by_id, diff_doc, totals, impl_items
    )

    register["generated_at_utc"] = ts
    register["totals"] = totals
    register["requirements"] = after_rows
    register["wave002_targeted_closeout"] = {
        "phase": "ENGINEERING_WAVE_002_TARGETED_CLOSEOUT",
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
        "Wave 002 closeout draft PR pending owner merge",
        f"DIGITAL_IMPLEMENTATION_OPEN={totals['DIGITAL_IMPLEMENTATION_OPEN']} rows need digital engineering",
        f"DIGITAL_VALIDATION_OPEN={totals['DIGITAL_VALIDATION_OPEN']} rows need verification/reproduction",
        "SYS-MISSION-006 residual non-game application parity beyond Wave 001+002 slices",
        "OS-PLATFORM-004/006 physical ring and dual-panel validation pending (digital impl complete)",
    ]
    remaining["wave002_closeout"] = {
        "targets_closed": diff_doc["closeout_assessment"]["targets_digital_implementation_complete"],
        "targets_still_open": diff_doc["closeout_assessment"]["targets_remaining_open"],
        "pixel_boundaries": pixel,
    }
    (OUT / "REMAINING_GAPS.json").write_text(json.dumps(remaining, indent=2) + "\n", encoding="utf-8")
    (OUT / "REMAINING_GAPS.md").write_text(
        "# Remaining gaps (Wave 002 closeout)\n\n"
        + "\n".join(f"- {b}" for b in remaining["top_blockers"])
        + "\n",
        encoding="utf-8",
    )

    (OUT / "END_GOAL_COVERAGE_MATRIX.json").write_text(json.dumps(end_goal, indent=2) + "\n", encoding="utf-8")
    fam2 = next(f for f in end_goal["families"] if f["id"] == 2)
    (OUT / "END_GOAL_COVERAGE_MATRIX.md").write_text(
        f"# End goal coverage (family 2 gunnchOS snapshot)\n\n"
        f"- digital_impl_open: {fam2['digital_impl_open']}\n"
        f"- DIGITAL_IMPLEMENTATION_COMPLETE in family: "
        f"{fam2['work_state_counts'].get('DIGITAL_IMPLEMENTATION_COMPLETE', 0)}\n"
        f"- family_release_level: {fam2['family_release_level']}\n",
        encoding="utf-8",
    )

    result["generated_at_utc"] = ts
    result["phase"] = "ENGINEERING_WAVE_002_TARGETED_CLOSEOUT"
    result["totals"] = totals
    result["work_state_counts"] = dict(work_state_counts)
    result["ENGINEERING_WAVE_002_TARGETED_CLOSEOUT"] = closeout_validation
    result["wave002_pixel_boundaries"] = pixel
    result["BASELINE_V2_STATE"] = "DRAFT_PR"
    result["STOP_FOR_OWNER_MERGE"] = True
    result["BASELINE_V2_READY_FOR_OWNER_MERGE"] = closeout_validation[
        "ENGINEERING_WAVE_002_TARGETED_CLOSEOUT_VALIDATION_PASS"
    ]
    result["CURSOR_MERGED_NOTHING"] = True
    (OUT / "BASELINE_V2_RESULT.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    CLOSEOUT_ART.mkdir(parents=True, exist_ok=True)
    diff_doc["closeout_validation"] = closeout_validation
    (CLOSEOUT_ART / "TARGETED_ROW_DIFF.json").write_text(json.dumps(diff_doc, indent=2) + "\n", encoding="utf-8")

    print(json.dumps({"totals": totals, "closeout_validation": closeout_validation}, indent=2))

    if not closeout_validation["ENGINEERING_WAVE_002_TARGETED_CLOSEOUT_VALIDATION_PASS"]:
        return 1
    rc = validate_b41()
    if rc != 0:
        return rc
    print("ENGINEERING_WAVE_002_TARGETED_CLOSEOUT_VALIDATION_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
