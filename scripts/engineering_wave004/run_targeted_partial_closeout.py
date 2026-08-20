#!/usr/bin/env python3
"""Engineering Wave 004 targeted partial closeout — 12 OS-PLATFORM rows only."""

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
CLOSEOUT_ART = ROOT / "artifacts" / "engineering_wave004_closeout"
WAVE004_MIRROR = ROOT / "artifacts" / "engineering_wave004" / "device_os_mirror"
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from baseline_v2_evidence_census import build_end_goal_matrix, compute_totals  # noqa: E402
from validate_baseline_v2_b4_register_integrity import main as validate_b41  # noqa: E402

TARGET_IDS = [
    "OS-PLATFORM-008",
    "OS-PLATFORM-009",
    "OS-PLATFORM-010",
    "OS-PLATFORM-011",
    "OS-PLATFORM-012",
    "OS-PLATFORM-013",
    "OS-PLATFORM-016",
    "OS-PLATFORM-018",
    "OS-PLATFORM-020",
    "OS-PLATFORM-021",
    "OS-PLATFORM-022",
    "OS-PLATFORM-023",
]

COMPLETE_IDS = [rid for rid in TARGET_IDS if rid != "OS-PLATFORM-020"]

ACCEPTED_MAIN = {
    "gunnchos-device-os": "5084006d20d6ab0cf00ece92ca76095d98fb55d3",
    "gunnchos-7gc-ai-ran-field-kit": "c995c97707541dca57dde4990c4115dfa0d666d5",
}

MERGE_PRS = {
    "gunnchos-device-os": {
        "pr": 126,
        "merge_commit": ACCEPTED_MAIN["gunnchos-device-os"],
        "merged_at": "2026-08-20T17:14:25Z",
        "title": "Wave004 final integrity: secure package lifecycle, restart-safe sync, enforced sandbox",
    },
    "gunnchos-7gc-ai-ran-field-kit": {
        "pr": 99,
        "merge_commit": ACCEPTED_MAIN["gunnchos-7gc-ai-ran-field-kit"],
        "merged_at": "2026-08-20T17:21:32Z",
        "title": "Wave004 final integrity aggregate: package, sync, sandbox closure",
    },
}

WAVE004_VAL = (
    "gunnchos-device-os:artifacts/engineering_wave004/WAVE004_RESULT.json;"
    "gunnchos-device-os:artifacts/engineering_wave004/REQUIREMENT_RESULTS.json;"
    "gunnchos-device-os:artifacts/engineering_wave004/REQUIREMENT_EVALUATOR_MATRIX.json;"
    "gunnchos-7gc-ai-ran-field-kit:artifacts/engineering_wave004/WAVE004_FINAL_INTEGRITY_AGGREGATE.json;"
    "gunnchos-7gc-ai-ran-field-kit:artifacts/engineering_wave004/device_os_mirror/WAVE004_RESULT.json;"
    "gunnchos-device-os:tests/test_wave004_platform_security.py"
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
    "OS-PLATFORM-008": {
        "implementation_evidence": (
            "gunnchos-device-os:gunnchos_device_os/platform/package_lifecycle.py;"
            "gunnchos-device-os:gunnchos_device_os/platform/secure_packaging.py"
        ),
        "pass4": [
            "gunnchos-device-os:gunnchos_device_os/platform/package_lifecycle.py role=IMPLEMENTATION_CODE",
            "gunnchos-device-os:gunnchos_device_os/platform/secure_packaging.py role=IMPLEMENTATION_CODE",
        ],
        "resolution_reason": (
            "Wave 004 accepted-main (#126): secure persistent package lifecycle with DEV Ed25519 signing; "
            "PRODUCTION_SIGNING remains false. IMPLEMENTED_AND_VALIDATED."
        ),
    },
    "OS-PLATFORM-009": {
        "implementation_evidence": "gunnchos-device-os:gunnchos_device_os/permissions_manager.py",
        "pass4": [
            "gunnchos-device-os:gunnchos_device_os/permissions_manager.py role=IMPLEMENTATION_CODE",
        ],
        "resolution_reason": (
            "Wave 004 accepted-main (#126): PermissionsManager least-privilege with role allowlists. "
            "IMPLEMENTED_AND_VALIDATED."
        ),
    },
    "OS-PLATFORM-010": {
        "implementation_evidence": "gunnchos-device-os:gunnchos_device_os/phase_xiv/local_ai/__init__.py",
        "pass4": [
            "gunnchos-device-os:gunnchos_device_os/phase_xiv/local_ai/__init__.py role=IMPLEMENTATION_CODE",
        ],
        "resolution_reason": (
            "Wave 004 accepted-main (#126): local AI runtime micro-deterministic; GENERAL_VLM/GENERAL_ASR false. "
            "IMPLEMENTED_AND_VALIDATED."
        ),
    },
    "OS-PLATFORM-011": {
        "implementation_evidence": "gunnchos-device-os:gunnchos_device_os/connectivity_orchestrator.py",
        "pass4": [
            "gunnchos-device-os:gunnchos_device_os/connectivity_orchestrator.py role=IMPLEMENTATION_CODE",
        ],
        "resolution_reason": (
            "Wave 004 accepted-main (#126): ConnectivityOrchestrator software bearer selection; "
            "CARRIER_ACCEPTED/STANDARDIZED_6G remain false. IMPLEMENTED_AND_VALIDATED."
        ),
    },
    "OS-PLATFORM-012": {
        "implementation_evidence": "gunnchos-device-os:gunnchos_device_os/platform/persistent_sync.py",
        "pass4": [
            "gunnchos-device-os:gunnchos_device_os/platform/persistent_sync.py role=IMPLEMENTATION_CODE",
        ],
        "resolution_reason": (
            "Wave 004 accepted-main (#126): Persistent OfflineSyncEngine A→B→C restart apply-once; "
            "corruption safe-fails. IMPLEMENTED_AND_VALIDATED."
        ),
    },
    "OS-PLATFORM-013": {
        "implementation_evidence": "gunnchos-device-os:gunnchos_device_os/platform/encrypted_storage.py",
        "pass4": [
            "gunnchos-device-os:gunnchos_device_os/platform/encrypted_storage.py role=IMPLEMENTATION_CODE",
        ],
        "resolution_reason": (
            "Wave 004 accepted-main (#126): software Fernet keystore; TPM_KEYSTORE remains false. "
            "IMPLEMENTED_AND_VALIDATED."
        ),
    },
    "OS-PLATFORM-016": {
        "implementation_evidence": "gunnchos-device-os:gunnchos_device_os/release_engineering/ab_update.py",
        "pass4": [
            "gunnchos-device-os:gunnchos_device_os/release_engineering/ab_update.py role=IMPLEMENTATION_CODE",
        ],
        "resolution_reason": (
            "Wave 004 accepted-main (#126): ABUpdateManager DEV-signed OTA slots; not production signing. "
            "IMPLEMENTED_AND_VALIDATED."
        ),
    },
    "OS-PLATFORM-018": {
        "implementation_evidence": "gunnchos-device-os:gunnchos_device_os/platform/recovery_userspace.py",
        "pass4": [
            "gunnchos-device-os:gunnchos_device_os/platform/recovery_userspace.py role=IMPLEMENTATION_CODE",
        ],
        "resolution_reason": (
            "Wave 004 accepted-main (#126): userspace recovery env; not hardware recovery partition. "
            "IMPLEMENTED_AND_VALIDATED."
        ),
    },
    "OS-PLATFORM-021": {
        "implementation_evidence": "gunnchos-device-os:gunnchos_device_os/diagnostics_log.py",
        "pass4": [
            "gunnchos-device-os:gunnchos_device_os/diagnostics_log.py role=IMPLEMENTATION_CODE",
        ],
        "resolution_reason": (
            "Wave 004 accepted-main (#126): DiagnosticsLog persistent redacted JSONL. IMPLEMENTED_AND_VALIDATED."
        ),
    },
    "OS-PLATFORM-022": {
        "implementation_evidence": "gunnchos-device-os:gunnchos_device_os/platform/accessibility_store.py",
        "pass4": [
            "gunnchos-device-os:gunnchos_device_os/platform/accessibility_store.py role=IMPLEMENTATION_CODE",
        ],
        "resolution_reason": (
            "Wave 004 accepted-main (#126): persisted accessibility per profile; WCAG_VALIDATED/"
            "HUMAN_ACCESSIBILITY_VALIDATED remain false. IMPLEMENTED_AND_VALIDATED."
        ),
    },
    "OS-PLATFORM-023": {
        "implementation_evidence": "gunnchos-device-os:gunnchos_device_os/platform/role_policy.py",
        "pass4": [
            "gunnchos-device-os:gunnchos_device_os/platform/role_policy.py role=IMPLEMENTATION_CODE",
        ],
        "resolution_reason": (
            "Wave 004 accepted-main (#126): persisted role policy with admin-authorized role change. "
            "IMPLEMENTED_AND_VALIDATED."
        ),
    },
}

SANDBOX_020 = {
    # Single repo:path — integrity gate matches impl.split(":",1)[-1] inside pass4 entries.
    "implementation_evidence": "gunnchos-device-os:gunnchos_device_os/platform/sandbox_executor.py",
    "pass4": [
        "gunnchos-device-os:gunnchos_device_os/platform/sandbox_executor.py role=IMPLEMENTATION_CODE",
        "gunnchos-device-os:gunnchos_device_os/sandbox_policy.py role=IMPLEMENTATION_CODE",
    ],
    "resolution_reason": (
        "Wave 004 accepted-main (#126): sandbox implementation present; "
        "SANDBOX_EXECUTION_VALIDATED=false / LOCAL_SANDBOX_VALIDATION=BLOCKED_ENVIRONMENT "
        "(backend=sandbox_exec_unavailable). PLAIN_SUBPROCESS_COUNTS_AS_SANDBOX=false; KERNEL_SANDBOX=false. "
        "Not marked DIGITAL_IMPLEMENTATION_COMPLETE."
    ),
    "next_action": (
        "Re-run mandatory sandbox suite on working isolation backend environment "
        "(bubblewrap namespaces or proven sandbox-exec)."
    ),
}

CLAIM_BOUNDARIES = {
    "HUMAN_E6": False,
    "WCAG_VALIDATED": False,
    "HUMAN_ACCESSIBILITY_VALIDATED": False,
    "GENERAL_VLM": False,
    "GENERAL_ASR": False,
    "GENERAL_MT": False,
    "CARRIER_ACCEPTED": False,
    "STANDARDIZED_6G": False,
    "PRODUCTION_SIGNING": False,
    "TPM_KEYSTORE": False,
    "KERNEL_SANDBOX": False,
    "PLAIN_SUBPROCESS_COUNTS_AS_SANDBOX": False,
}

EXPECTED_AFTER = {
    "DIGITAL_IMPLEMENTATION_COMPLETE": 63,
    "DIGITAL_IMPLEMENTATION_OPEN": 98,
    "DIGITAL_VALIDATION_OPEN": 1,
    "EVIDENCE_MAPPING_OPEN": 0,
    "ATOMIC_TOTAL": 419,
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _semantic_snapshot(row: dict[str, Any]) -> dict[str, Any]:
    return {k: row.get(k) for k in SEMANTIC_FIELDS}


def _ensure_pass4(row: dict[str, Any], pass4: list[str]) -> None:
    passes = row.get("search_passes") or {}
    passes = copy.deepcopy(passes) if passes else {}
    passes["pass4_implementation"] = pass4
    row["search_passes"] = passes


def _apply_complete(row: dict[str, Any], rid: str) -> None:
    spec = COMPLETE_OUTCOMES[rid]
    row["work_state"] = "DIGITAL_IMPLEMENTATION_COMPLETE"
    row["resolution"] = "DIGITAL_IMPLEMENTATION_COMPLETE"
    row["engineering_state"] = "DIGITAL_IMPLEMENTATION_COMPLETE"
    row["implementation_state"] = "IMPLEMENTED"
    row["verification_state"] = "INDEPENDENTLY_VERIFIED_DIGITAL"
    row["current_level"] = "L2_DIGITALLY_VERIFIED"
    row["accepted_main_sha"] = ACCEPTED_MAIN["gunnchos-device-os"]
    row["implementation_evidence"] = spec["implementation_evidence"]
    row["validation_evidence"] = WAVE004_VAL
    row["token_or_result"] = "PASS"
    row["evidence_confidence"] = "MEDIUM"
    row["resolution_reason"] = spec["resolution_reason"]
    row["next_action"] = "Owner may advance human/device proof or product RC when ready."
    row["pending_dimensions"] = row.get("pending_dimensions") or []
    row["next_level_blocker"] = row.get("next_level_blocker")
    row["specific_missing_implementation"] = None
    row["why_paths_insufficient"] = None
    _ensure_pass4(row, spec["pass4"])


def _apply_validation_open_020(row: dict[str, Any]) -> None:
    spec = SANDBOX_020
    row["work_state"] = "DIGITAL_VALIDATION_OPEN"
    row["resolution"] = "DIGITAL_VALIDATION_OPEN"
    row["engineering_state"] = "DIGITAL_VALIDATION_OPEN"
    row["implementation_state"] = "IMPLEMENTED"
    row["verification_state"] = "NOT_VERIFIED"
    row["current_level"] = "L1_IMPLEMENTED"
    row["accepted_main_sha"] = ACCEPTED_MAIN["gunnchos-device-os"]
    row["implementation_evidence"] = spec["implementation_evidence"]
    row["validation_evidence"] = (
        "gunnchos-device-os:artifacts/engineering_wave004/SANDBOX_ENFORCEMENT_RESULT.json;"
        "gunnchos-7gc-ai-ran-field-kit:artifacts/engineering_wave004/device_os_mirror/SANDBOX_ENFORCEMENT_RESULT.json;"
        "gunnchos-device-os:artifacts/engineering_wave004/WAVE004_RESULT.json"
    )
    row["token_or_result"] = "BLOCKED_ENVIRONMENT"
    row["evidence_confidence"] = "MEDIUM"
    row["resolution_reason"] = spec["resolution_reason"]
    row["next_action"] = spec["next_action"]
    row["pending_dimensions"] = row.get("pending_dimensions") or []
    row["next_level_blocker"] = "SANDBOX_ENFORCEMENT_ENVIRONMENT"
    row["specific_missing_implementation"] = None
    row["why_paths_insufficient"] = None
    row["blocker_class"] = "BLOCKED_ENVIRONMENT"
    row["blocker"] = "SANDBOX_ENFORCEMENT_ENVIRONMENT"
    row["implementation_present"] = True
    row["plain_subprocess_counts_as_sandbox"] = False
    row["kernel_sandbox"] = False
    _ensure_pass4(row, spec["pass4"])


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


def _val_work_item(row: dict[str, Any]) -> dict[str, Any]:
    item: dict[str, Any] = {
        "requirement_id": row["requirement_id"],
        "title": row["title"],
        "owner_repo": row.get("owner_repo"),
        "primary_end_goal_family": row.get("primary_end_goal_family"),
        "implementation_evidence": row.get("implementation_evidence"),
        "validation_evidence": row.get("validation_evidence"),
        "next_action": row.get("next_action"),
    }
    if row["requirement_id"] == "OS-PLATFORM-020":
        item.update(
            {
                "implementation_present": True,
                "validation_state": "DIGITAL_VALIDATION_OPEN",
                "blocker_class": "BLOCKED_ENVIRONMENT",
                "blocker": "SANDBOX_ENFORCEMENT_ENVIRONMENT",
                "plain_subprocess_counts_as_sandbox": False,
                "kernel_sandbox": False,
            }
        )
    return item


def _write_md_register(rows: list[dict[str, Any]], totals: dict[str, int], path: Path) -> None:
    lines = [
        "# Master completion register (Wave 004 targeted partial closeout)",
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
                f"- **{row['requirement_id']}** — {row['work_state']} — {row.get('resolution_reason', '')[:140]}"
            )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_work_md(items: list[dict[str, Any]], title: str, path: Path) -> None:
    lines = [f"# {title}", "", f"Count: {len(items)}", ""]
    for it in items[:50]:
        lines.append(f"- {it['requirement_id']}: {it.get('title', '')}")
    if len(items) > 50:
        lines.append(f"- … and {len(items) - 50} more")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _load_wave004_truth() -> dict[str, Any]:
    wave = json.loads((WAVE004_MIRROR / "WAVE004_RESULT.json").read_text(encoding="utf-8"))
    sandbox = json.loads((WAVE004_MIRROR / "SANDBOX_ENFORCEMENT_RESULT.json").read_text(encoding="utf-8"))
    req = json.loads((WAVE004_MIRROR / "REQUIREMENT_RESULTS.json").read_text(encoding="utf-8"))
    classification = wave.get("requirement_classification") or req.get("requirements") or {}
    validated = sum(1 for v in classification.values() if v.get("classification") == "IMPLEMENTED_AND_VALIDATED")
    blocked = sum(1 for v in classification.values() if v.get("classification") == "BLOCKED_ENVIRONMENT")
    if wave.get("target_requirements") != 12:
        raise SystemExit(f"target_requirements={wave.get('target_requirements')} expected 12")
    if validated != 11 or blocked != 1:
        raise SystemExit(f"expected 11 validated + 1 blocked_environment; got validated={validated} blocked={blocked}")
    if classification.get("OS-PLATFORM-008", {}).get("classification") != "IMPLEMENTED_AND_VALIDATED":
        raise SystemExit("OS-PLATFORM-008 not IMPLEMENTED_AND_VALIDATED")
    if classification.get("OS-PLATFORM-012", {}).get("classification") != "IMPLEMENTED_AND_VALIDATED":
        raise SystemExit("OS-PLATFORM-012 not IMPLEMENTED_AND_VALIDATED")
    if classification.get("OS-PLATFORM-020", {}).get("classification") != "BLOCKED_ENVIRONMENT":
        raise SystemExit("OS-PLATFORM-020 must remain BLOCKED_ENVIRONMENT")
    if wave.get("UNCONDITIONAL_TRUE_CLASSIFIERS", -1) != 0:
        raise SystemExit("UNCONDITIONAL_TRUE_CLASSIFIERS must be 0")
    if wave.get("BASELINE_COUNTS_UPDATED") is not False:
        raise SystemExit("Wave004 evidence BASELINE_COUNTS_UPDATED must be false (pre-closeout)")
    if sandbox.get("SANDBOX_EXECUTION_VALIDATED") is not False:
        raise SystemExit("SANDBOX_EXECUTION_VALIDATED must be false")
    if sandbox.get("KERNEL_SANDBOX") is not False:
        raise SystemExit("KERNEL_SANDBOX must be false")
    if sandbox.get("PLAIN_SUBPROCESS_COUNTS_AS_SANDBOX") is not False:
        raise SystemExit("PLAIN_SUBPROCESS_COUNTS_AS_SANDBOX must be false")
    if sandbox.get("LOCAL_SANDBOX_VALIDATION") != "BLOCKED_ENVIRONMENT":
        raise SystemExit("LOCAL_SANDBOX_VALIDATION must be BLOCKED_ENVIRONMENT")
    return {
        "classification": classification,
        "validated": validated,
        "blocked_environment": blocked,
        "COMPLETE_GATE_REQUIRES_12_OF_12": True,
        "UNCONDITIONAL_TRUE_CLASSIFIERS": 0,
        "BASELINE_COUNTS_UPDATED_ON_EVIDENCE": False,
        "PLAIN_SUBPROCESS_COUNTS_AS_SANDBOX": False,
        "KERNEL_SANDBOX": False,
        "SANDBOX_EXECUTION_VALIDATED": False,
    }


def _validate_closeout(
    before_rows: dict[str, dict[str, Any]],
    after_rows: dict[str, dict[str, Any]],
    diff: dict[str, Any],
    totals: dict[str, int],
    impl_items: list[dict[str, Any]],
    val_items: list[dict[str, Any]],
    pending_before: int,
    pending_after: int,
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
    for key, expected in EXPECTED_AFTER.items():
        if totals.get(key) != expected:
            errors.append(f"{key}={totals.get(key)} expected {expected}")
    if {i["requirement_id"] for i in val_items} != {"OS-PLATFORM-020"}:
        errors.append(
            f"validation queue IDs={sorted(i['requirement_id'] for i in val_items)} expected only OS-PLATFORM-020"
        )
    wave_ids = set(TARGET_IDS)
    if any(i["requirement_id"] in wave_ids for i in impl_items):
        errors.append("Wave004 IDs still present in implementation queue")
    if after_rows["OS-PLATFORM-020"]["work_state"] != "DIGITAL_VALIDATION_OPEN":
        errors.append("OS-PLATFORM-020 must be DIGITAL_VALIDATION_OPEN")
    if after_rows["OS-PLATFORM-020"]["work_state"] == "DIGITAL_IMPLEMENTATION_COMPLETE":
        errors.append("OS-PLATFORM-020 must NOT be complete")
    for rid in COMPLETE_IDS:
        if after_rows[rid]["work_state"] != "DIGITAL_IMPLEMENTATION_COMPLETE":
            errors.append(f"{rid} expected DIGITAL_IMPLEMENTATION_COMPLETE")
    if pending_before != pending_after:
        errors.append(f"non-digital pending changed {pending_before}->{pending_after}")
    claim = diff.get("claim_boundaries", {})
    for key, expected in CLAIM_BOUNDARIES.items():
        if claim.get(key) is not expected:
            errors.append(f"claim boundary {key}={claim.get(key)} expected {expected}")
    ok = len(errors) == 0
    return {
        "ENGINEERING_WAVE_004_TARGETED_PARTIAL_CLOSEOUT_VALIDATION_PASS": ok,
        "errors": errors,
        "accepted_main_shas": ACCEPTED_MAIN,
        "claim_boundaries": claim,
        "EXPECTED_AFTER": EXPECTED_AFTER,
    }


def main() -> int:
    ts = _utc_now()
    truth = _load_wave004_truth()

    register_path = OUT / "MASTER_COMPLETION_REGISTER.json"
    register = json.loads(register_path.read_text(encoding="utf-8"))
    before_by_id = {r["requirement_id"]: copy.deepcopy(r) for r in register["requirements"]}

    impl_reg = json.loads((OUT / "NEXT_DIGITAL_IMPLEMENTATION_WORK.json").read_text(encoding="utf-8"))
    val_reg = json.loads((OUT / "NEXT_DIGITAL_VALIDATION_WORK.json").read_text(encoding="utf-8"))
    result = json.loads((OUT / "BASELINE_V2_RESULT.json").read_text(encoding="utf-8"))
    remaining = json.loads((OUT / "REMAINING_GAPS.json").read_text(encoding="utf-8"))
    pending_reg = json.loads((OUT / "NON_DIGITAL_PENDING_REGISTER.json").read_text(encoding="utf-8"))
    pending_before = pending_reg.get("total_pending_rows")

    before_totals = register["totals"]
    if before_totals.get("DIGITAL_IMPLEMENTATION_COMPLETE") != 52:
        raise SystemExit(f"pre-closeout COMPLETE={before_totals.get('DIGITAL_IMPLEMENTATION_COMPLETE')} expected 52")
    if before_totals.get("DIGITAL_IMPLEMENTATION_OPEN") != 110:
        raise SystemExit(f"pre-closeout IMPL_OPEN={before_totals.get('DIGITAL_IMPLEMENTATION_OPEN')} expected 110")
    if before_totals.get("DIGITAL_VALIDATION_OPEN") != 0:
        raise SystemExit(f"pre-closeout VALIDATION_OPEN={before_totals.get('DIGITAL_VALIDATION_OPEN')} expected 0")

    unrelated_impl_before = [
        i["requirement_id"] for i in impl_reg["all_items"] if i["requirement_id"] not in TARGET_IDS
    ]

    after_rows: list[dict[str, Any]] = []
    changed_ids: list[str] = []
    before_states: dict[str, Any] = {}
    after_states: dict[str, Any] = {}
    closed_ids: list[str] = []
    validation_open_ids: list[str] = []

    for row in register["requirements"]:
        rid = row["requirement_id"]
        new_row = copy.deepcopy(row)
        if rid not in TARGET_IDS:
            after_rows.append(new_row)
            continue
        before_states[rid] = _semantic_snapshot(row)
        cls = (truth["classification"].get(rid) or {}).get("classification")
        if rid == "OS-PLATFORM-020":
            if cls != "BLOCKED_ENVIRONMENT":
                raise SystemExit(f"020 classification={cls} — refusing to invent")
            _apply_validation_open_020(new_row)
            validation_open_ids.append(rid)
        else:
            if cls != "IMPLEMENTED_AND_VALIDATED":
                raise SystemExit(f"{rid} classification={cls} — refusing complete without evidence")
            _apply_complete(new_row, rid)
            closed_ids.append(rid)
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
    fam2 = next(f for f in end_goal["families"] if f["id"] == 2)

    impl_open_rows = [r for r in after_rows if r["work_state"] == "DIGITAL_IMPLEMENTATION_OPEN"]
    val_open_rows = [r for r in after_rows if r["work_state"] == "DIGITAL_VALIDATION_OPEN"]
    impl_items = [_impl_work_item(r) for r in impl_open_rows]
    val_items = [_val_work_item(r) for r in val_open_rows]

    unrelated_impl_after = [i["requirement_id"] for i in impl_items if i["requirement_id"] not in TARGET_IDS]
    unrelated_impl_changed = 0 if unrelated_impl_before == unrelated_impl_after else 1

    diff_doc = {
        "schema": "gunnchos.engineering_wave004.targeted_row_diff.v1",
        "generated_at_utc": ts,
        "wave": "ENGINEERING_WAVE_004",
        "target_ids": TARGET_IDS,
        "changed_ids": changed_ids,
        "unexpected_changed_ids": unexpected,
        "untargeted_rows_changed": untargeted_changed,
        "UNRELATED_IMPLEMENTATION_QUEUE_ROWS_CHANGED": unrelated_impl_changed,
        "before_state": before_states,
        "after_state": after_states,
        "accepted_main_evidence": {
            "merge_prs": MERGE_PRS,
            "accepted_main_shas": ACCEPTED_MAIN,
            "required_ci_state": "SUCCESS_ON_MERGED_PRS",
            "aggregate_artifacts": [
                "artifacts/engineering_wave004/WAVE004_FINAL_INTEGRITY_AGGREGATE.json",
                "artifacts/engineering_wave004/device_os_mirror/WAVE004_RESULT.json",
                "artifacts/engineering_wave004/device_os_mirror/SANDBOX_ENFORCEMENT_RESULT.json",
                "gunnchos-device-os:artifacts/engineering_wave004/WAVE004_RESULT.json",
            ],
            "wave004_truth": {
                "TARGET_REQUIREMENTS": 12,
                "IMPLEMENTED_AND_VALIDATED": 11,
                "OS-PLATFORM-020": "BLOCKED_ENVIRONMENT",
                "UNCONDITIONAL_TRUE_CLASSIFIERS": 0,
                "COMPLETE_GATE_REQUIRES_12_OF_12": True,
                "PLAIN_SUBPROCESS_COUNTS_AS_SANDBOX": False,
                "BASELINE_COUNTS_UPDATED_ON_WAVE_EVIDENCE": False,
            },
        },
        "claim_boundaries": CLAIM_BOUNDARIES,
        "closeout_assessment": {
            "targets_digital_implementation_complete": closed_ids,
            "targets_remaining_validation_open": validation_open_ids,
            "OS_PLATFORM_020_NOT_COMPLETE": True,
            "independent_digital_reproduction": "PARTIAL",
            "release_complete": False,
            "COMPLETE_GATE_REQUIRES_12_OF_12": True,
        },
        "backlog_delta": {
            "DIGITAL_IMPLEMENTATION_COMPLETE_before": before_totals["DIGITAL_IMPLEMENTATION_COMPLETE"],
            "DIGITAL_IMPLEMENTATION_COMPLETE_after": totals["DIGITAL_IMPLEMENTATION_COMPLETE"],
            "DIGITAL_VALIDATION_OPEN_before": before_totals["DIGITAL_VALIDATION_OPEN"],
            "DIGITAL_VALIDATION_OPEN_after": totals["DIGITAL_VALIDATION_OPEN"],
            "DIGITAL_IMPLEMENTATION_OPEN_before": before_totals["DIGITAL_IMPLEMENTATION_OPEN"],
            "DIGITAL_IMPLEMENTATION_OPEN_after": totals["DIGITAL_IMPLEMENTATION_OPEN"],
            "EVIDENCE_MAPPING_OPEN_before": before_totals.get("EVIDENCE_MAPPING_OPEN", 0),
            "EVIDENCE_MAPPING_OPEN_after": totals.get("EVIDENCE_MAPPING_OPEN", 0),
            "rows_closed": len(closed_ids),
            "rows_moved_to_validation_open": len(validation_open_ids),
        },
        "family_2_gunnchos_os": {
            "family_release_level": fam2.get("family_release_level"),
            "validation_open": fam2.get("validation_open"),
            "digital_impl_open": fam2.get("digital_impl_open"),
            "work_state_counts": fam2.get("work_state_counts"),
        },
    }

    closeout_validation = _validate_closeout(
        before_by_id,
        after_by_id,
        diff_doc,
        totals,
        impl_items,
        val_items,
        pending_before,
        pending_reg.get("total_pending_rows"),
    )
    diff_doc["closeout_validation"] = closeout_validation

    register["generated_at_utc"] = ts
    register["totals"] = totals
    register["requirements"] = after_rows
    register["wave004_targeted_partial_closeout"] = {
        "phase": "ENGINEERING_WAVE_004_TARGETED_PARTIAL_CLOSEOUT",
        "targets_changed": len(changed_ids),
        "targets_closed": len(closed_ids),
        "targets_validation_open": len(validation_open_ids),
        "accepted_main_shas": ACCEPTED_MAIN,
        "OS_PLATFORM_020": "DIGITAL_VALIDATION_OPEN",
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
        "Wave 004 targeted partial closeout draft PR pending owner merge",
        f"DIGITAL_IMPLEMENTATION_OPEN={totals['DIGITAL_IMPLEMENTATION_OPEN']} rows need digital engineering",
        f"DIGITAL_VALIDATION_OPEN={totals['DIGITAL_VALIDATION_OPEN']} (OS-PLATFORM-020 sandbox enforcement environment)",
        "OS-PLATFORM-020: re-run mandatory sandbox suite on working isolation backend; PLAIN_SUBPROCESS_COUNTS_AS_SANDBOX=false",
    ]
    remaining["wave004_closeout"] = {
        "targets_closed": closed_ids,
        "targets_validation_open": validation_open_ids,
        "claim_boundaries": CLAIM_BOUNDARIES,
        "OS_PLATFORM_020": {
            "implementation_present": True,
            "validation_state": "DIGITAL_VALIDATION_OPEN",
            "blocker_class": "BLOCKED_ENVIRONMENT",
            "blocker": "SANDBOX_ENFORCEMENT_ENVIRONMENT",
            "plain_subprocess_counts_as_sandbox": False,
            "kernel_sandbox": False,
        },
    }
    (OUT / "REMAINING_GAPS.json").write_text(json.dumps(remaining, indent=2) + "\n", encoding="utf-8")
    (OUT / "REMAINING_GAPS.md").write_text(
        "# Remaining gaps (Wave 004 targeted partial closeout)\n\n"
        + "\n".join(f"- {b}" for b in remaining["top_blockers"])
        + "\n",
        encoding="utf-8",
    )

    (OUT / "END_GOAL_COVERAGE_MATRIX.json").write_text(json.dumps(end_goal, indent=2) + "\n", encoding="utf-8")
    (OUT / "END_GOAL_COVERAGE_MATRIX.md").write_text(
        "# End goal coverage (family 2 gunnchOS snapshot)\n\n"
        f"- family_release_level: {fam2['family_release_level']}\n"
        f"- validation_open: {fam2['validation_open']}\n"
        f"- digital_impl_open: {fam2['digital_impl_open']}\n"
        f"- DIGITAL_IMPLEMENTATION_COMPLETE in family: "
        f"{fam2['work_state_counts'].get('DIGITAL_IMPLEMENTATION_COMPLETE', 0)}\n",
        encoding="utf-8",
    )

    result["generated_at_utc"] = ts
    result["phase"] = "ENGINEERING_WAVE_004_TARGETED_PARTIAL_CLOSEOUT"
    result["totals"] = totals
    result["work_state_counts"] = dict(work_state_counts)
    result["ENGINEERING_WAVE_004_TARGETED_PARTIAL_CLOSEOUT"] = closeout_validation
    result["wave004_claim_boundaries"] = CLAIM_BOUNDARIES
    result["BASELINE_V2_STATE"] = "DRAFT_PR"
    result["STOP_FOR_OWNER_MERGE"] = True
    result["BASELINE_V2_READY_FOR_OWNER_MERGE"] = closeout_validation[
        "ENGINEERING_WAVE_004_TARGETED_PARTIAL_CLOSEOUT_VALIDATION_PASS"
    ]
    result["CURSOR_MERGED_NOTHING"] = True
    result["ECOSYSTEM_DIGITAL_IMPLEMENTATION_COMPLETE"] = False
    result["ECOSYSTEM_DIGITAL_VALIDATION_COMPLETE"] = False
    result["USER_READY_DIGITAL_RELEASE_CANDIDATE"] = False
    result["HUMAN_E6_COMPLETE"] = False
    result["PHYSICAL_VALIDATION_COMPLETE"] = False
    result["EXTERNAL_CERTIFICATION_COMPLETE"] = False
    result["SHIPPING_PRODUCT"] = False
    result["STANDARDIZED_6G"] = False
    (OUT / "BASELINE_V2_RESULT.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    CLOSEOUT_ART.mkdir(parents=True, exist_ok=True)
    (CLOSEOUT_ART / "TARGETED_ROW_DIFF.json").write_text(json.dumps(diff_doc, indent=2) + "\n", encoding="utf-8")

    closeout_result = {
        "schema": "gunnchos.engineering_wave004.targeted_partial_closeout_result.v1",
        "generated_at_utc": ts,
        "phase": "ENGINEERING_WAVE_004_TARGETED_PARTIAL_CLOSEOUT",
        "ENGINEERING_WAVE_004_CLOSEOUT": "PARTIAL",
        "ENGINEERING_WAVE_004_TARGETED_PARTIAL_CLOSEOUT_VALIDATION_PASS": closeout_validation[
            "ENGINEERING_WAVE_004_TARGETED_PARTIAL_CLOSEOUT_VALIDATION_PASS"
        ],
        "CURSOR_MERGED_NOTHING": True,
        "READY_FOR_OWNER_MERGE": False,
        "STOP_FOR_OWNER_MERGE": True,
        "prerequisites": {
            "gunnchos-device-os_pr_126": MERGE_PRS["gunnchos-device-os"],
            "gunnchos-7gc-ai-ran-field-kit_pr_99": MERGE_PRS["gunnchos-7gc-ai-ran-field-kit"],
            "accepted_main_shas": ACCEPTED_MAIN,
            "required_ci_state": "SUCCESS",
        },
        "wave004_accepted_main_truth": {
            "TARGET_REQUIREMENTS": 12,
            "IMPLEMENTED_AND_VALIDATED": 11,
            "OS-PLATFORM-020": "BLOCKED_ENVIRONMENT",
            "UNCONDITIONAL_TRUE_CLASSIFIERS": 0,
            "COMPLETE_GATE_REQUIRES_12_OF_12": True,
            "PLAIN_SUBPROCESS_COUNTS_AS_SANDBOX": False,
            "BASELINE_COUNTS_UPDATED_ON_WAVE_EVIDENCE": False,
            "SANDBOX_EXECUTION_VALIDATED": False,
            "KERNEL_SANDBOX": False,
        },
        "pre_closeout_baseline": {
            "ATOMIC_TOTAL": 419,
            "DIGITAL_IMPLEMENTATION_COMPLETE": 52,
            "DIGITAL_IMPLEMENTATION_OPEN": 110,
            "DIGITAL_VALIDATION_OPEN": 0,
            "EVIDENCE_MAPPING_OPEN": 0,
        },
        "post_closeout_baseline": {
            "ATOMIC_TOTAL": totals["ATOMIC_TOTAL"],
            "DIGITAL_IMPLEMENTATION_COMPLETE": totals["DIGITAL_IMPLEMENTATION_COMPLETE"],
            "DIGITAL_IMPLEMENTATION_OPEN": totals["DIGITAL_IMPLEMENTATION_OPEN"],
            "DIGITAL_VALIDATION_OPEN": totals["DIGITAL_VALIDATION_OPEN"],
            "EVIDENCE_MAPPING_OPEN": totals.get("EVIDENCE_MAPPING_OPEN", 0),
        },
        "targets_digital_implementation_complete": closed_ids,
        "targets_digital_validation_open": validation_open_ids,
        "OS_PLATFORM_020": {
            "implementation_present": True,
            "validation_state": "DIGITAL_VALIDATION_OPEN",
            "blocker_class": "BLOCKED_ENVIRONMENT",
            "blocker": "SANDBOX_ENFORCEMENT_ENVIRONMENT",
            "plain_subprocess_counts_as_sandbox": False,
            "kernel_sandbox": False,
            "next_action": SANDBOX_020["next_action"],
            "NOT_MARKED_COMPLETE": True,
        },
        "UNTARGETED_ROWS_CHANGED": untargeted_changed,
        "UNEXPECTED_CHANGED_IDS": unexpected,
        "UNRELATED_IMPLEMENTATION_QUEUE_ROWS_CHANGED": unrelated_impl_changed,
        "claim_boundaries": CLAIM_BOUNDARIES,
        "closeout_validation": closeout_validation,
        "queue_integrity": {
            "len_NEXT_IMPL": len(impl_items),
            "DIGITAL_IMPLEMENTATION_OPEN": totals["DIGITAL_IMPLEMENTATION_OPEN"],
            "len_NEXT_VALIDATION": len(val_items),
            "DIGITAL_VALIDATION_OPEN": totals["DIGITAL_VALIDATION_OPEN"],
            "NEXT_VALIDATION_only": [i["requirement_id"] for i in val_items],
        },
        "non_digital_pending_preserved": pending_before == pending_reg.get("total_pending_rows"),
        "non_digital_pending_rows": pending_reg.get("total_pending_rows"),
    }
    (CLOSEOUT_ART / "CLOSEOUT_RESULT.json").write_text(json.dumps(closeout_result, indent=2) + "\n", encoding="utf-8")

    print(json.dumps({"totals": {k: totals[k] for k in EXPECTED_AFTER}, "closeout_validation": closeout_validation}, indent=2))

    if not closeout_validation["ENGINEERING_WAVE_004_TARGETED_PARTIAL_CLOSEOUT_VALIDATION_PASS"]:
        return 1
    rc = validate_b41()
    if rc != 0:
        return rc
    print("ENGINEERING_WAVE_004_TARGETED_PARTIAL_CLOSEOUT_VALIDATION_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
