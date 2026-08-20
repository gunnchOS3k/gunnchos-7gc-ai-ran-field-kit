#!/usr/bin/env python3
"""Engineering Wave 003 targeted closeout — update 19 AI-LOCAL/AI-GOV register rows only."""

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
CLOSEOUT_ART = ROOT / "artifacts" / "engineering_wave003_closeout"
WAVE003_ART = ROOT / "artifacts" / "engineering_wave003"
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from baseline_v2_evidence_census import build_end_goal_matrix, compute_totals  # noqa: E402
from validate_baseline_v2_b4_register_integrity import main as validate_b41  # noqa: E402

TARGET_IDS = [
    "AI-LOCAL-001",
    "AI-LOCAL-002",
    "AI-LOCAL-003",
    "AI-LOCAL-005",
    "AI-LOCAL-006",
    "AI-LOCAL-007",
    "AI-LOCAL-008",
    "AI-LOCAL-009",
    "AI-LOCAL-011",
    "AI-GOV-001",
    "AI-GOV-003",
    "AI-GOV-004",
    "AI-GOV-005",
    "AI-GOV-006",
    "AI-GOV-007",
    "AI-GOV-008",
    "AI-GOV-010",
    "AI-GOV-011",
    "AI-GOV-012",
]

ACCEPTED_MAIN = {
    "gunnchAI3k": "4b4f411710e8cdb8102a7e11502f8497f68156b1",
    "gunnchos-7gc-ai-ran-field-kit": "b0ff3aad9a32472afef284ccec50b9e8d48583af",
}

WAVE003_VAL = (
    "gunnchAI3k:evidence/engineering_wave003/WAVE003_RESULT.json;"
    "gunnchAI3k:evidence/engineering_wave003/INDEPENDENT_REPRODUCTION.json;"
    "gunnchAI3k:evidence/engineering_wave003/REQUIREMENT_RESULTS.json;"
    "gunnchos-7gc-ai-ran-field-kit:artifacts/engineering_wave003/ENGINEERING_WAVE003_AGGREGATE.json;"
    "gunnchos-7gc-ai-ran-field-kit:tests/engineering_wave003/test_wave003_aggregate.py;"
    "gunnchAI3k:tests/evals/wave003.test.ts"
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
    "AI-LOCAL-001": {
        "implementation_evidence": (
            "gunnchAI3k:fixtures/local-runtime/documents/tutoring-basics.md;"
            "gunnchAI3k:fixtures/waike/public/curriculum/digital_rc/GENERAL_IT/course.json"
        ),
        "resolution_reason": (
            "Wave 003 accepted-main: deterministic offline tutoring rubric with local-only network guard; "
            "WAIKE fixture present. Independent reproduction PASS (gunnchAI3k PR #45)."
        ),
    },
    "AI-LOCAL-002": {
        "implementation_evidence": (
            "gunnchAI3k:src/system-layer/local_inference/backends/deterministic.ts;"
            "gunnchAI3k:src/phase_xiv/computer_use/coding_agent.ts;"
            "gunnchAI3k:evals/wave003/fixtures/code_fixture_repo/README.md"
        ),
        "resolution_reason": (
            "Wave 003 accepted-main: structured local code assist plus sandboxed coding-agent E2E on "
            "ephemeral fixture repo. Independent reproduction PASS."
        ),
    },
    "AI-LOCAL-003": {
        "implementation_evidence": (
            "gunnchAI3k:evals/wave003/fixtures/device_state.json;"
            "gunnchAI3k:evals/wave003/fixtures/device_states.json"
        ),
        "resolution_reason": (
            "Wave 003 accepted-main: device help grounded to supplied fixture state; no invented telemetry."
        ),
    },
    "AI-LOCAL-005": {
        "implementation_evidence": "gunnchAI3k:src/system-layer/local_inference/backends/deterministic.ts#translation",
        "resolution_reason": (
            "Wave 003 accepted-main: offline glossary translation only. GENERAL_MT claim boundary remains false."
        ),
    },
    "AI-LOCAL-006": {
        "implementation_evidence": "gunnchAI3k:evals/wave003/fixtures/a11y_ui.json",
        "resolution_reason": (
            "Wave 003 accepted-main: structured a11y checklist from deterministic assistant; "
            "HUMAN_ACCESSIBILITY_VALIDATED remains false."
        ),
    },
    "AI-LOCAL-007": {
        "implementation_evidence": "gunnchAI3k:evals/wave003/fixtures/mini_corpus/doc-a.md",
        "resolution_reason": (
            "Wave 003 accepted-main: mini-corpus retrieval metrics on local RAG engine (not cloud search)."
        ),
    },
    "AI-LOCAL-008": {
        "implementation_evidence": "gunnchAI3k:evals/wave003/fixtures/game_state.json",
        "resolution_reason": (
            "Wave 003 accepted-main: deterministic game-state coach with NOT_TRAINED_GAME_PLAYING_AGENT=true; "
            "not a learned game-playing agent."
        ),
    },
    "AI-LOCAL-009": {
        "implementation_evidence": (
            "gunnchAI3k:evals/wave003/fixtures/connectivity_telemetry.json;"
            "gunnchAI3k:fixtures/local-runtime/documents/connectivity-diagnosis.md"
        ),
        "resolution_reason": (
            "Wave 003 accepted-main: connectivity diagnosis uses structured telemetry fixture + approved local pack."
        ),
    },
    "AI-LOCAL-011": {
        "implementation_evidence": (
            "gunnchAI3k:src/stage2/fleet/router.ts;"
            "gunnchAI3k:src/local-runtime/network.ts;"
            "gunnchAI3k:src/system-layer/product_service/service.ts"
        ),
        "resolution_reason": (
            "Wave 003 accepted-main: cross-cutting offline kill-switch — router + network guard + "
            "product assist remain local-viable."
        ),
    },
    "AI-GOV-001": {
        "implementation_evidence": "gunnchAI3k:src/system-layer/product_service/governance.ts#declarePurpose",
        "resolution_reason": (
            "Wave 003 accepted-main: purpose structure validated (users/uses/out-of-scope/limitations)."
        ),
    },
    "AI-GOV-003": {
        "implementation_evidence": "gunnchAI3k:src/system-layer/product_service/governance.ts#setMinimization",
        "resolution_reason": (
            "Wave 003 accepted-main: PII hint stripping + max query length minimization at decision time."
        ),
    },
    "AI-GOV-004": {
        "implementation_evidence": "gunnchAI3k:src/system-layer/privacy_policy.ts",
        "resolution_reason": (
            "Wave 003 accepted-main: user-visible local/cloud disclosure via governance + privacy policy evaluator."
        ),
    },
    "AI-GOV-005": {
        "implementation_evidence": "gunnchAI3k:src/system-layer/product_service/governance.ts#setModelVersion",
        "resolution_reason": (
            "Wave 003 accepted-main: model/version identification with bounded history (not cloud model registry)."
        ),
    },
    "AI-GOV-006": {
        "implementation_evidence": "gunnchAI3k:evidence/engineering_wave003/EVALUATION_BASELINE.json",
        "resolution_reason": (
            "Wave 003 accepted-main: versioned EVALUATION_BASELINE.json completeness + meaningful per-req thresholds."
        ),
    },
    "AI-GOV-007": {
        "implementation_evidence": "gunnchAI3k:src/system-layer/evaluation/metrics.ts",
        "resolution_reason": (
            "Wave 003 accepted-main: failure analysis via declared failureModes + structured metric scoring."
        ),
    },
    "AI-GOV-008": {
        "implementation_evidence": (
            "gunnchAI3k:evals/wave003/fixtures/bias_a11y_scope.json;"
            "gunnchAI3k:evidence/engineering_wave003/BIAS_ACCESSIBILITY_EVALUATION.json"
        ),
        "resolution_reason": (
            "Wave 003 accepted-main: bounded differential a11y/language/input/device-profile eval. "
            "GENERAL_BIAS_AUDIT remains false."
        ),
    },
    "AI-GOV-010": {
        "implementation_evidence": (
            "gunnchAI3k:src/stage2/fleet/router.ts;"
            "gunnchAI3k:src/system-layer/product_service/governance.ts#setSafeFallback"
        ),
        "resolution_reason": (
            "Wave 003 accepted-main: safe local fallback chain (nano tier) with governance fallbackSafe flag."
        ),
    },
    "AI-GOV-011": {
        "implementation_evidence": (
            "gunnchAI3k:src/system-layer/product_service/governance.ts#record;"
            "gunnchAI3k:evidence/engineering_wave003/MONITORING_PRIVACY_RESULT.json"
        ),
        "resolution_reason": (
            "Wave 003 accepted-main: monitoring covers invocation/identity/route/fallback/error/eval/rollback "
            "with privacy sentinels redacted."
        ),
    },
    "AI-GOV-012": {
        "implementation_evidence": (
            "gunnchAI3k:src/system-layer/product_service/governance.ts#rollback;"
            "gunnchAI3k:src/system-layer/product_service/governance.ts#rollbackModel"
        ),
        "resolution_reason": (
            "Wave 003 accepted-main: governance state + model version rollback with bounded snapshot history."
        ),
    },
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _semantic_snapshot(row: dict[str, Any]) -> dict[str, Any]:
    return {k: row.get(k) for k in SEMANTIC_FIELDS}


def _load_admissible_targets() -> dict[str, str]:
    agg = json.loads((WAVE003_ART / "ENGINEERING_WAVE003_AGGREGATE.json").read_text(encoding="utf-8"))
    wave = json.loads((WAVE003_ART / "WAVE003_RESULT.json").read_text(encoding="utf-8"))
    repro = json.loads((WAVE003_ART / "INDEPENDENT_REPRODUCTION.json").read_text(encoding="utf-8"))
    if agg.get("INDEPENDENT_DIGITAL_REPRODUCTION") != "PASS":
        raise SystemExit("INDEPENDENT_DIGITAL_REPRODUCTION must be PASS in aggregate evidence")
    if wave.get("independentDigitalReproduction") != "PASS" or not wave.get("releaseComplete"):
        raise SystemExit("WAVE003_RESULT must report independentDigitalReproduction=PASS and releaseComplete=true")
    if repro.get("result") != "PASS" or not repro.get("perRequirementStateMatch"):
        raise SystemExit("INDEPENDENT_REPRODUCTION must be PASS with perRequirementStateMatch=true")
    if wave.get("doctrine", {}).get("validationImportsRequirementProof") is not False:
        raise SystemExit("VALIDATION_IMPORTS_REQUIREMENT_PROOF must be false in WAVE003_RESULT doctrine")
    classification = agg.get("requirement_classification") or {}
    return {rid: state for rid, state in classification.items() if rid in TARGET_IDS}


def _apply_complete(row: dict[str, Any], rid: str) -> None:
    spec = COMPLETE_OUTCOMES[rid]
    row["work_state"] = "DIGITAL_IMPLEMENTATION_COMPLETE"
    row["resolution"] = "DIGITAL_IMPLEMENTATION_COMPLETE"
    row["engineering_state"] = "DIGITAL_IMPLEMENTATION_COMPLETE"
    row["implementation_state"] = "IMPLEMENTED"
    row["verification_state"] = "INDEPENDENTLY_VERIFIED_DIGITAL"
    row["current_level"] = "L2_DIGITALLY_VERIFIED"
    row["accepted_main_sha"] = ACCEPTED_MAIN["gunnchAI3k"]
    row["implementation_evidence"] = spec["implementation_evidence"]
    row["validation_evidence"] = WAVE003_VAL
    row["token_or_result"] = "PASS"
    row["evidence_confidence"] = "MEDIUM"
    row["resolution_reason"] = spec["resolution_reason"]
    row["next_action"] = "Owner may advance human/device proof or product RC when ready."
    row["pending_dimensions"] = row.get("pending_dimensions") or []
    row["next_level_blocker"] = row.get("next_level_blocker")
    row.pop("specific_missing_implementation", None)
    row.pop("why_paths_insufficient", None)


def _apply_validation_open(row: dict[str, Any], rid: str, reason: str) -> None:
    row["work_state"] = "DIGITAL_VALIDATION_OPEN"
    row["resolution"] = "DIGITAL_VALIDATION_OPEN"
    row["engineering_state"] = "DIGITAL_VALIDATION_OPEN"
    row["resolution_reason"] = reason
    row["next_action"] = "Provide admissible independent validation evidence before closeout."


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
        "# Master completion register (Wave 003 targeted closeout)",
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
    val_items: list[dict[str, Any]],
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
    if len(val_items) != totals["DIGITAL_VALIDATION_OPEN"]:
        errors.append(
            f"val_items_len={len(val_items)} != DIGITAL_VALIDATION_OPEN={totals['DIGITAL_VALIDATION_OPEN']}"
        )
    if totals["DIGITAL_IMPLEMENTATION_OPEN"] != 110:
        errors.append(f"DIGITAL_IMPLEMENTATION_OPEN={totals['DIGITAL_IMPLEMENTATION_OPEN']} expected 110")
    claim = diff.get("claim_boundaries", {})
    for key, expected in {
        "GENERAL_ASR": False,
        "GENERAL_VLM": False,
        "GENERAL_MT": False,
        "GENERAL_BIAS_AUDIT": False,
        "HUMAN_E6": False,
        "HUMAN_ACCESSIBILITY_VALIDATED": False,
        "NOT_TRAINED_GAME_PLAYING_AGENT": True,
    }.items():
        if claim.get(key) is not expected:
            errors.append(f"claim boundary {key}={claim.get(key)} expected {expected}")
    ok = len(errors) == 0
    return {
        "ENGINEERING_WAVE_003_TARGETED_CLOSEOUT_VALIDATION_PASS": ok,
        "errors": errors,
        "accepted_main_shas": ACCEPTED_MAIN,
        "claim_boundaries": claim,
    }


def main() -> int:
    ts = _utc_now()
    admissible = _load_admissible_targets()
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
    closed_ids: list[str] = []
    remaining_open: list[str] = []

    for row in register["requirements"]:
        rid = row["requirement_id"]
        new_row = copy.deepcopy(row)
        if rid not in TARGET_IDS:
            after_rows.append(new_row)
            continue
        before_states[rid] = _semantic_snapshot(row)
        if admissible.get(rid) == "VALIDATED":
            _apply_complete(new_row, rid)
            closed_ids.append(rid)
        else:
            _apply_validation_open(
                new_row,
                rid,
                f"Wave 003 closeout withheld: aggregate classification={admissible.get(rid)!r} (not VALIDATED).",
            )
            remaining_open.append(rid)
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
    fam4 = next(f for f in end_goal["families"] if f["id"] == 4)

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

    claim_boundaries = {
        "GENERAL_ASR": False,
        "GENERAL_VLM": False,
        "GENERAL_MT": False,
        "GENERAL_BIAS_AUDIT": False,
        "HUMAN_E6": False,
        "HUMAN_ACCESSIBILITY_VALIDATED": False,
        "NOT_TRAINED_GAME_PLAYING_AGENT": True,
        "VALIDATION_IMPORTS_REQUIREMENT_PROOF": False,
    }

    diff_doc = {
        "schema": "gunnchos.engineering_wave003.targeted_row_diff.v1",
        "generated_at_utc": ts,
        "wave": "ENGINEERING_WAVE_003",
        "target_ids": TARGET_IDS,
        "changed_ids": changed_ids,
        "unexpected_changed_ids": unexpected,
        "untargeted_rows_changed": untargeted_changed,
        "before_state": before_states,
        "after_state": after_states,
        "accepted_main_evidence": {
            "merge_prs": {
                "gunnchAI3k": {"pr": 45, "merge_commit": ACCEPTED_MAIN["gunnchAI3k"]},
                "gunnchos-7gc-ai-ran-field-kit": {
                    "pr": 95,
                    "merge_commit": ACCEPTED_MAIN["gunnchos-7gc-ai-ran-field-kit"],
                },
            },
            "accepted_main_shas": ACCEPTED_MAIN,
            "aggregate_artifacts": [
                "artifacts/engineering_wave003/ENGINEERING_WAVE003_AGGREGATE.json",
                "gunnchAI3k:evidence/engineering_wave003/WAVE003_RESULT.json",
                "gunnchAI3k:evidence/engineering_wave003/INDEPENDENT_REPRODUCTION.json",
            ],
            "validation_rerun": {
                "gunnchai_test_wave003": "gunnchAI3k:npm run test:wave003",
                "gunnchai_eval_wave003": "gunnchAI3k:npm run eval:wave003",
                "field_kit_aggregate": "tests/engineering_wave003/test_wave003_aggregate.py",
                "field_kit_closeout": "tests/engineering_wave003/test_wave003_targeted_closeout.py",
            },
        },
        "claim_boundaries": claim_boundaries,
        "closeout_assessment": {
            "targets_digital_implementation_complete": closed_ids,
            "targets_remaining_validation_open": remaining_open,
            "independent_digital_reproduction": "PASS",
            "release_complete": True,
        },
        "backlog_delta": {
            "DIGITAL_IMPLEMENTATION_COMPLETE_before": sum(
                1 for r in before_by_id.values() if r.get("work_state") == "DIGITAL_IMPLEMENTATION_COMPLETE"
            ),
            "DIGITAL_IMPLEMENTATION_COMPLETE_after": totals["DIGITAL_IMPLEMENTATION_COMPLETE"],
            "DIGITAL_VALIDATION_OPEN_before": sum(
                1 for r in before_by_id.values() if r.get("work_state") == "DIGITAL_VALIDATION_OPEN"
            ),
            "DIGITAL_VALIDATION_OPEN_after": totals["DIGITAL_VALIDATION_OPEN"],
            "DIGITAL_IMPLEMENTATION_OPEN_before": sum(
                1 for r in before_by_id.values() if r.get("work_state") == "DIGITAL_IMPLEMENTATION_OPEN"
            ),
            "DIGITAL_IMPLEMENTATION_OPEN_after": totals["DIGITAL_IMPLEMENTATION_OPEN"],
            "rows_closed": len(closed_ids),
        },
        "family_4_gunnchai": {
            "family_release_level": fam4.get("family_release_level"),
            "validation_open": fam4.get("validation_open"),
            "digital_impl_open": fam4.get("digital_impl_open"),
            "work_state_counts": fam4.get("work_state_counts"),
        },
    }

    closeout_validation = _validate_closeout(
        before_by_id, after_by_id, diff_doc, totals, impl_items, val_items
    )

    register["generated_at_utc"] = ts
    register["totals"] = totals
    register["requirements"] = after_rows
    register["wave003_targeted_closeout"] = {
        "phase": "ENGINEERING_WAVE_003_TARGETED_CLOSEOUT",
        "targets_changed": len(changed_ids),
        "targets_closed": len(closed_ids),
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
        "Wave 003 closeout draft PR pending owner merge",
        f"DIGITAL_IMPLEMENTATION_OPEN={totals['DIGITAL_IMPLEMENTATION_OPEN']} rows need digital engineering",
        f"DIGITAL_VALIDATION_OPEN={totals['DIGITAL_VALIDATION_OPEN']} rows need verification/reproduction",
        "gunnchAI local-intelligence Wave 003 independently validated on accepted main; claim boundaries preserved",
    ]
    remaining["wave003_closeout"] = {
        "targets_closed": closed_ids,
        "targets_still_open": remaining_open,
        "claim_boundaries": claim_boundaries,
    }
    (OUT / "REMAINING_GAPS.json").write_text(json.dumps(remaining, indent=2) + "\n", encoding="utf-8")
    (OUT / "REMAINING_GAPS.md").write_text(
        "# Remaining gaps (Wave 003 closeout)\n\n"
        + "\n".join(f"- {b}" for b in remaining["top_blockers"])
        + "\n",
        encoding="utf-8",
    )

    (OUT / "END_GOAL_COVERAGE_MATRIX.json").write_text(json.dumps(end_goal, indent=2) + "\n", encoding="utf-8")
    (OUT / "END_GOAL_COVERAGE_MATRIX.md").write_text(
        f"# End goal coverage (family 4 gunnchAI snapshot)\n\n"
        f"- family_release_level: {fam4['family_release_level']}\n"
        f"- validation_open: {fam4['validation_open']}\n"
        f"- digital_impl_open: {fam4['digital_impl_open']}\n"
        f"- DIGITAL_IMPLEMENTATION_COMPLETE in family: "
        f"{fam4['work_state_counts'].get('DIGITAL_IMPLEMENTATION_COMPLETE', 0)}\n",
        encoding="utf-8",
    )

    result["generated_at_utc"] = ts
    result["phase"] = "ENGINEERING_WAVE_003_TARGETED_CLOSEOUT"
    result["totals"] = totals
    result["work_state_counts"] = dict(work_state_counts)
    result["ENGINEERING_WAVE_003_TARGETED_CLOSEOUT"] = closeout_validation
    result["wave003_claim_boundaries"] = claim_boundaries
    result["BASELINE_V2_STATE"] = "DRAFT_PR"
    result["STOP_FOR_OWNER_MERGE"] = True
    result["BASELINE_V2_READY_FOR_OWNER_MERGE"] = closeout_validation[
        "ENGINEERING_WAVE_003_TARGETED_CLOSEOUT_VALIDATION_PASS"
    ]
    result["CURSOR_MERGED_NOTHING"] = True
    (OUT / "BASELINE_V2_RESULT.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    CLOSEOUT_ART.mkdir(parents=True, exist_ok=True)
    diff_doc["closeout_validation"] = closeout_validation
    (CLOSEOUT_ART / "TARGETED_ROW_DIFF.json").write_text(json.dumps(diff_doc, indent=2) + "\n", encoding="utf-8")

    print(json.dumps({"totals": totals, "closeout_validation": closeout_validation}, indent=2))

    if not closeout_validation["ENGINEERING_WAVE_003_TARGETED_CLOSEOUT_VALIDATION_PASS"]:
        return 1
    rc = validate_b41()
    if rc != 0:
        return rc
    print("ENGINEERING_WAVE_003_TARGETED_CLOSEOUT_VALIDATION_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
