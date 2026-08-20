#!/usr/bin/env python3
"""Engineering Wave 005 targeted closeout — 12 NET-ORCH decision-engine rows only."""

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
CLOSEOUT_ART = ROOT / "artifacts" / "engineering_wave005_closeout"
WAVE005_MIRROR = ROOT / "artifacts" / "engineering_wave005" / "device_os_mirror"
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from baseline_v2_evidence_census import build_end_goal_matrix, compute_totals  # noqa: E402
from validate_baseline_v2_b4_register_integrity import main as validate_b41  # noqa: E402

TARGET_IDS = [
    "NET-ORCH-001",
    "NET-ORCH-014",
    "NET-ORCH-015",
    "NET-ORCH-016",
    "NET-ORCH-017",
    "NET-ORCH-018",
    "NET-ORCH-019",
    "NET-ORCH-020",
    "NET-ORCH-021",
    "NET-ORCH-022",
    "NET-ORCH-023",
    "NET-ORCH-024",
]

PRESERVE_UNTOUCHED = "OS-PLATFORM-020"

ACCEPTED_MAIN = {
    "gunnchos-device-os": "9d61569eb1affad2dfd7d9e9cbd231d60220c56f",
    "gunnchos-7gc-ai-ran-field-kit": "39087c294a57a6c42aa8d815a92fbeba1991c688",
}

MERGE_PRS = {
    "gunnchos-device-os": {
        "pr": 128,
        "merge_commit": ACCEPTED_MAIN["gunnchos-device-os"],
        "merged_at": "2026-08-20T19:59:54Z",
        "title": "Wave005 integrity repair: strict evaluator gate, priority authority, hard user policy",
    },
    "gunnchos-7gc-ai-ran-field-kit": {
        "pr": 102,
        "merge_commit": ACCEPTED_MAIN["gunnchos-7gc-ai-ran-field-kit"],
        "merged_at": "2026-08-20T20:00:10Z",
        "title": "Wave005 integrity correction aggregate: strict decision-engine evidence",
    },
}

WAVE005_VAL = (
    "gunnchos-device-os:artifacts/engineering_wave005/WAVE005_RESULT.json;"
    "gunnchos-device-os:artifacts/engineering_wave005/REQUIREMENT_RESULTS.json;"
    "gunnchos-device-os:artifacts/engineering_wave005/REQUIREMENT_EVALUATOR_MATRIX.json;"
    "gunnchos-device-os:artifacts/engineering_wave005/INTEGRITY_REPAIR_RESULT.json;"
    "gunnchos-7gc-ai-ran-field-kit:artifacts/engineering_wave005/WAVE005_AGGREGATE.json;"
    "gunnchos-7gc-ai-ran-field-kit:artifacts/engineering_wave005/device_os_mirror/WAVE005_RESULT.json;"
    "gunnchos-device-os:tests/test_wave005_network_decision.py"
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

# Per-row implementation anchors (device-os network_decision package).
COMPLETE_OUTCOMES: dict[str, dict[str, Any]] = {
    "NET-ORCH-001": {
        "implementation_evidence": (
            "gunnchos-device-os:gunnchos_device_os/network_decision/models.py;"
            "gunnchos-device-os:gunnchos_device_os/network_decision/engine.py"
        ),
        "pass4": [
            "gunnchos-device-os:gunnchos_device_os/network_decision/models.py role=IMPLEMENTATION_CODE",
            "gunnchos-device-os:gunnchos_device_os/network_decision/engine.py role=IMPLEMENTATION_CODE",
        ],
        "resolution_reason": (
            "Wave 005 accepted-main (#128): AnywhereServiceObjective typed runtime with service classes "
            "and floors; DIGITAL_SYNTHETIC_EVIDENCE. IMPLEMENTED_AND_VALIDATED."
        ),
    },
    "NET-ORCH-014": {
        "implementation_evidence": (
            "gunnchos-device-os:gunnchos_device_os/network_decision/metrics.py;"
            "gunnchos-device-os:gunnchos_device_os/network_decision/evaluators.py"
        ),
        "pass4": [
            "gunnchos-device-os:gunnchos_device_os/network_decision/metrics.py role=IMPLEMENTATION_CODE",
            "gunnchos-device-os:gunnchos_device_os/network_decision/evaluators.py role=IMPLEMENTATION_CODE",
        ],
        "resolution_reason": (
            "Wave 005 accepted-main (#128): availability + freshness/failure/recovery handling. "
            "IMPLEMENTED_AND_VALIDATED."
        ),
    },
    "NET-ORCH-015": {
        "implementation_evidence": (
            "gunnchos-device-os:gunnchos_device_os/network_decision/metrics.py;"
            "gunnchos-device-os:gunnchos_device_os/network_decision/evaluators.py"
        ),
        "pass4": [
            "gunnchos-device-os:gunnchos_device_os/network_decision/metrics.py role=IMPLEMENTATION_CODE",
            "gunnchos-device-os:gunnchos_device_os/network_decision/evaluators.py role=IMPLEMENTATION_CODE",
        ],
        "resolution_reason": (
            "Wave 005 accepted-main (#128): signal quality normalization with provenance; "
            "unknown!=perfect. IMPLEMENTED_AND_VALIDATED."
        ),
    },
    "NET-ORCH-016": {
        "implementation_evidence": (
            "gunnchos-device-os:gunnchos_device_os/network_decision/metrics.py;"
            "gunnchos-device-os:gunnchos_device_os/network_decision/evaluators.py"
        ),
        "pass4": [
            "gunnchos-device-os:gunnchos_device_os/network_decision/metrics.py role=IMPLEMENTATION_CODE",
            "gunnchos-device-os:gunnchos_device_os/network_decision/evaluators.py role=IMPLEMENTATION_CODE",
        ],
        "resolution_reason": (
            "Wave 005 accepted-main (#128): latency ms with service-aware thresholds; negatives rejected. "
            "IMPLEMENTED_AND_VALIDATED."
        ),
    },
    "NET-ORCH-017": {
        "implementation_evidence": (
            "gunnchos-device-os:gunnchos_device_os/network_decision/metrics.py;"
            "gunnchos-device-os:gunnchos_device_os/network_decision/evaluators.py"
        ),
        "pass4": [
            "gunnchos-device-os:gunnchos_device_os/network_decision/metrics.py role=IMPLEMENTATION_CODE",
            "gunnchos-device-os:gunnchos_device_os/network_decision/evaluators.py role=IMPLEMENTATION_CODE",
        ],
        "resolution_reason": (
            "Wave 005 accepted-main (#128): jitter separate from latency; interactive more sensitive. "
            "IMPLEMENTED_AND_VALIDATED."
        ),
    },
    "NET-ORCH-018": {
        "implementation_evidence": (
            "gunnchos-device-os:gunnchos_device_os/network_decision/metrics.py;"
            "gunnchos-device-os:gunnchos_device_os/network_decision/evaluators.py"
        ),
        "pass4": [
            "gunnchos-device-os:gunnchos_device_os/network_decision/metrics.py role=IMPLEMENTATION_CODE",
            "gunnchos-device-os:gunnchos_device_os/network_decision/evaluators.py role=IMPLEMENTATION_CODE",
        ],
        "resolution_reason": (
            "Wave 005 accepted-main (#128): packet loss ratio 0..1; higher loss never improves score. "
            "IMPLEMENTED_AND_VALIDATED."
        ),
    },
    "NET-ORCH-019": {
        "implementation_evidence": (
            "gunnchos-device-os:gunnchos_device_os/network_decision/metrics.py;"
            "gunnchos-device-os:gunnchos_device_os/network_decision/evaluators.py"
        ),
        "pass4": [
            "gunnchos-device-os:gunnchos_device_os/network_decision/metrics.py role=IMPLEMENTATION_CODE",
            "gunnchos-device-os:gunnchos_device_os/network_decision/evaluators.py role=IMPLEMENTATION_CODE",
        ],
        "resolution_reason": (
            "Wave 005 accepted-main (#128): cost policy abstractions; cannot bypass hard security. "
            "IMPLEMENTED_AND_VALIDATED."
        ),
    },
    "NET-ORCH-020": {
        "implementation_evidence": (
            "gunnchos-device-os:gunnchos_device_os/network_decision/metrics.py;"
            "gunnchos-device-os:gunnchos_device_os/network_decision/evaluators.py"
        ),
        "pass4": [
            "gunnchos-device-os:gunnchos_device_os/network_decision/metrics.py role=IMPLEMENTATION_CODE",
            "gunnchos-device-os:gunnchos_device_os/network_decision/evaluators.py role=IMPLEMENTATION_CODE",
        ],
        "resolution_reason": (
            "Wave 005 accepted-main (#128): modeled energy with battery-saving influence; "
            "not measured battery draw. IMPLEMENTED_AND_VALIDATED."
        ),
    },
    "NET-ORCH-021": {
        "implementation_evidence": (
            "gunnchos-device-os:gunnchos_device_os/network_decision/metrics.py;"
            "gunnchos-device-os:gunnchos_device_os/network_decision/evaluators.py"
        ),
        "pass4": [
            "gunnchos-device-os:gunnchos_device_os/network_decision/metrics.py role=IMPLEMENTATION_CODE",
            "gunnchos-device-os:gunnchos_device_os/network_decision/evaluators.py role=IMPLEMENTATION_CODE",
        ],
        "resolution_reason": (
            "Wave 005 accepted-main (#128): security hard policy; fast/free hostile rejected. "
            "IMPLEMENTED_AND_VALIDATED."
        ),
    },
    "NET-ORCH-022": {
        "implementation_evidence": (
            "gunnchos-device-os:gunnchos_device_os/network_decision/metrics.py;"
            "gunnchos-device-os:gunnchos_device_os/network_decision/evaluators.py"
        ),
        "pass4": [
            "gunnchos-device-os:gunnchos_device_os/network_decision/metrics.py role=IMPLEMENTATION_CODE",
            "gunnchos-device-os:gunnchos_device_os/network_decision/evaluators.py role=IMPLEMENTATION_CODE",
        ],
        "resolution_reason": (
            "Wave 005 accepted-main (#128): data limits with hard exhaustion reject; "
            "background prefers unmetered. IMPLEMENTED_AND_VALIDATED."
        ),
    },
    "NET-ORCH-023": {
        "implementation_evidence": (
            "gunnchos-device-os:gunnchos_device_os/network_decision/priority_authority.py;"
            "gunnchos-device-os:gunnchos_device_os/network_decision/evaluators.py"
        ),
        "pass4": [
            "gunnchos-device-os:gunnchos_device_os/network_decision/priority_authority.py role=IMPLEMENTATION_CODE",
            "gunnchos-device-os:gunnchos_device_os/network_decision/evaluators.py role=IMPLEMENTATION_CODE",
        ],
        "resolution_reason": (
            "Wave 005 accepted-main (#128): application priority with PriorityAuthority; soft influence; "
            "self-asserted CRITICAL blocked; PRODUCTION_APP_PRIORITY_SIGNING=false. IMPLEMENTED_AND_VALIDATED."
        ),
    },
    "NET-ORCH-024": {
        "implementation_evidence": (
            "gunnchos-device-os:gunnchos_device_os/network_decision/preferences.py;"
            "gunnchos-device-os:gunnchos_device_os/network_decision/evaluators.py"
        ),
        "pass4": [
            "gunnchos-device-os:gunnchos_device_os/network_decision/preferences.py role=IMPLEMENTATION_CODE",
            "gunnchos-device-os:gunnchos_device_os/network_decision/evaluators.py role=IMPLEMENTATION_CODE",
        ],
        "resolution_reason": (
            "Wave 005 accepted-main (#128): user preference SOFT|HARD policy persisted; hard avoid enforced; "
            "security remains mandatory; TPM_KEYSTORE=false. IMPLEMENTED_AND_VALIDATED."
        ),
    },
}

CLAIM_BOUNDARIES = {
    "CARRIER_ACCEPTED": False,
    "FIELD_MEASURED_PERFORMANCE": False,
    "HUMAN_E6": False,
    "LIVE_CARRIER_HANDOVER_VALIDATED": False,
    "PHYSICAL_VALIDATION": False,
    "PRODUCTION_APP_PRIORITY_SIGNING": False,
    "PRODUCTION_NETWORK_OPTIMALITY": False,
    "REAL_NTN_MODEM_VALIDATED": False,
    "STANDARDIZED_6G": False,
    "TPM_KEYSTORE": False,
}

EXPECTED_BEFORE = {
    "ATOMIC_TOTAL": 419,
    "DIGITAL_IMPLEMENTATION_COMPLETE": 63,
    "DIGITAL_IMPLEMENTATION_OPEN": 98,
    "DIGITAL_VALIDATION_OPEN": 1,
    "EVIDENCE_MAPPING_OPEN": 0,
}

EXPECTED_AFTER = {
    "ATOMIC_TOTAL": 419,
    "DIGITAL_IMPLEMENTATION_COMPLETE": 75,
    "DIGITAL_IMPLEMENTATION_OPEN": 86,
    "DIGITAL_VALIDATION_OPEN": 1,
    "EVIDENCE_MAPPING_OPEN": 0,
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
    row["validation_evidence"] = WAVE005_VAL
    row["token_or_result"] = "PASS"
    row["evidence_confidence"] = "MEDIUM"
    row["resolution_reason"] = spec["resolution_reason"]
    row["next_action"] = "Owner may advance human/device/field proof or product RC when ready."
    row["pending_dimensions"] = row.get("pending_dimensions") or []
    row["next_level_blocker"] = row.get("next_level_blocker")
    row["specific_missing_implementation"] = None
    row["why_paths_insufficient"] = None
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
    if row["requirement_id"] == PRESERVE_UNTOUCHED:
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
        "# Master completion register (Wave 005 targeted closeout)",
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
        if row["requirement_id"] in TARGET_IDS or row["requirement_id"] == PRESERVE_UNTOUCHED:
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


def _load_wave005_truth() -> dict[str, Any]:
    wave = json.loads((WAVE005_MIRROR / "WAVE005_RESULT.json").read_text(encoding="utf-8"))
    integrity = json.loads((WAVE005_MIRROR / "INTEGRITY_REPAIR_RESULT.json").read_text(encoding="utf-8"))
    neg = json.loads((WAVE005_MIRROR / "COMPLETION_GATE_NEGATIVE_CONTROL_RESULT.json").read_text(encoding="utf-8"))
    authority = json.loads((WAVE005_MIRROR / "APPLICATION_PRIORITY_AUTHORITY_RESULT.json").read_text(encoding="utf-8"))
    boundary = json.loads((WAVE005_MIRROR / "APPLICATION_PRIORITY_BOUNDARY_RESULT.json").read_text(encoding="utf-8"))
    pref = json.loads((WAVE005_MIRROR / "USER_PREFERENCE_POLICY_RESULT.json").read_text(encoding="utf-8"))
    telemetry = json.loads((WAVE005_MIRROR / "INVALID_TELEMETRY_RESULT.json").read_text(encoding="utf-8"))
    provenance = json.loads((WAVE005_MIRROR / "SOURCE_PROVENANCE_RESULT.json").read_text(encoding="utf-8"))
    claims = json.loads((WAVE005_MIRROR / "CLAIM_BOUNDARIES.json").read_text(encoding="utf-8"))
    req = json.loads((WAVE005_MIRROR / "REQUIREMENT_RESULTS.json").read_text(encoding="utf-8"))

    classification = wave.get("requirement_classification") or req.get("requirements") or {}
    validated = sum(1 for v in classification.values() if v.get("classification") == "IMPLEMENTED_AND_VALIDATED")
    if wave.get("target_requirements") != 12:
        raise SystemExit(f"target_requirements={wave.get('target_requirements')} expected 12")
    if validated != 12:
        raise SystemExit(f"expected 12 IMPLEMENTED_AND_VALIDATED; got {validated}")
    if set(classification.keys()) != set(TARGET_IDS):
        raise SystemExit(f"classification IDs mismatch: {sorted(classification.keys())}")
    for rid in TARGET_IDS:
        if classification[rid].get("classification") != "IMPLEMENTED_AND_VALIDATED":
            raise SystemExit(f"{rid} not IMPLEMENTED_AND_VALIDATED")
        if classification[rid].get("ok") is not True:
            raise SystemExit(f"{rid} ok!=true")
    if wave.get("WAVE005_POSTMERGE_INTEGRITY_REPAIR") != "PASS":
        raise SystemExit("WAVE005_POSTMERGE_INTEGRITY_REPAIR must be PASS")
    if integrity.get("WAVE005_POSTMERGE_INTEGRITY_REPAIR") != "PASS":
        raise SystemExit("INTEGRITY_REPAIR_RESULT must be PASS")
    if wave.get("UNCONDITIONAL_TRUE_CLASSIFIERS", -1) != 0:
        raise SystemExit("UNCONDITIONAL_TRUE_CLASSIFIERS must be 0")
    if wave.get("UNCONDITIONAL_TRUE_CLASSIFIERS_COMPUTED") is not True:
        raise SystemExit("UNCONDITIONAL_TRUE_CLASSIFIERS_COMPUTED must be true")
    gate = wave.get("completion_gate") or {}
    if gate.get("WAVE005_COMPLETE_GATE_REQUIRES_12_OF_12") is not True:
        raise SystemExit("12-of-12 gate flag missing")
    if gate.get("validated_count") != 12 or gate.get("complete") is not True:
        raise SystemExit(f"completion_gate incomplete: {gate}")
    if neg.get("BROKEN_EVALUATOR_GATE_RESULT") != "REJECTED" or neg.get("ok") is not True:
        raise SystemExit("negative control must reject broken evaluator")
    if authority.get("ok") is not True or boundary.get("ok") is not True:
        raise SystemExit("priority authority/boundary must pass")
    if pref.get("ok") is not True:
        raise SystemExit("user preference soft/hard policy must pass")
    if telemetry.get("NEVER_BEST_CASE_MISSING_INVALID") is not True:
        raise SystemExit("adversarial telemetry NEVER_BEST_CASE must hold")
    if telemetry.get("NEVER_BEST_CASE_MISSING_INVALID_COMPUTED") is not True:
        raise SystemExit("NEVER_BEST_CASE must be computed")
    if not provenance.get("evaluator_source_hashes") or not provenance.get("production_source_tree_hash"):
        raise SystemExit("portable provenance hashes missing")
    if wave.get("OS_PLATFORM_020_UNTOUCHED") is not True:
        raise SystemExit("OS_PLATFORM_020_UNTOUCHED must be true on wave evidence")
    if wave.get("BASELINE_COUNTS_UPDATED") is not False:
        raise SystemExit("Wave005 evidence BASELINE_COUNTS_UPDATED must be false (pre-closeout)")
    for k, expected in CLAIM_BOUNDARIES.items():
        if k == "TPM_KEYSTORE":
            continue  # not always in wave claim file
        if claims.get(k) is not expected:
            raise SystemExit(f"claim {k}={claims.get(k)} expected {expected}")
    return {
        "classification": classification,
        "validated": validated,
        "UNCONDITIONAL_TRUE_CLASSIFIERS": 0,
        "WAVE005_COMPLETE_GATE_REQUIRES_12_OF_12": True,
        "BASELINE_COUNTS_UPDATED_ON_EVIDENCE": False,
        "OS_PLATFORM_020_UNTOUCHED": True,
        "NEVER_BEST_CASE_MISSING_INVALID": True,
        "negative_control_rejected": True,
        "priority_authority_ok": True,
        "priority_boundary_ok": True,
        "preference_policy_ok": True,
        "portable_provenance": True,
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
    os020_before: dict[str, Any],
    os020_after: dict[str, Any],
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
    pool = (
        totals["DIGITAL_IMPLEMENTATION_COMPLETE"]
        + totals["DIGITAL_IMPLEMENTATION_OPEN"]
        + totals["DIGITAL_VALIDATION_OPEN"]
    )
    if pool != 162:
        errors.append(f"DIGITAL_CONTROLLABLE_POOL={pool} expected 162")
    if {i["requirement_id"] for i in val_items} != {PRESERVE_UNTOUCHED}:
        errors.append(
            f"validation queue IDs={sorted(i['requirement_id'] for i in val_items)} expected only {PRESERVE_UNTOUCHED}"
        )
    if any(i["requirement_id"] in set(TARGET_IDS) for i in impl_items):
        errors.append("Wave005 IDs still present in implementation queue")
    for rid in TARGET_IDS:
        if after_rows[rid]["work_state"] != "DIGITAL_IMPLEMENTATION_COMPLETE":
            errors.append(f"{rid} expected DIGITAL_IMPLEMENTATION_COMPLETE")
    if after_rows[PRESERVE_UNTOUCHED]["work_state"] != "DIGITAL_VALIDATION_OPEN":
        errors.append("OS-PLATFORM-020 must remain DIGITAL_VALIDATION_OPEN")
    if os020_before != os020_after:
        errors.append("OS_PLATFORM_020_CHANGED=true (must be false)")
    if pending_before != pending_after:
        errors.append(f"non-digital pending changed {pending_before}->{pending_after}")
    claim = diff.get("claim_boundaries", {})
    for key, expected in CLAIM_BOUNDARIES.items():
        if claim.get(key) is not expected:
            errors.append(f"claim boundary {key}={claim.get(key)} expected {expected}")
    # Cross-check independent fields (no literal "all good")
    if totals["DIGITAL_IMPLEMENTATION_COMPLETE"] - EXPECTED_BEFORE["DIGITAL_IMPLEMENTATION_COMPLETE"] != 12:
        errors.append("COMPLETE delta must equal 12 closed rows")
    if EXPECTED_BEFORE["DIGITAL_IMPLEMENTATION_OPEN"] - totals["DIGITAL_IMPLEMENTATION_OPEN"] != 12:
        errors.append("IMPL_OPEN delta must equal 12 removed queue rows")
    if totals["DIGITAL_VALIDATION_OPEN"] != EXPECTED_BEFORE["DIGITAL_VALIDATION_OPEN"]:
        errors.append("VALIDATION_OPEN must stay unchanged at 1")
    ok = len(errors) == 0
    return {
        "ENGINEERING_WAVE_005_TARGETED_CLOSEOUT_VALIDATION_PASS": ok,
        "errors": errors,
        "accepted_main_shas": ACCEPTED_MAIN,
        "claim_boundaries": claim,
        "EXPECTED_AFTER": EXPECTED_AFTER,
        "DIGITAL_CONTROLLABLE_POOL": pool,
        "OS_PLATFORM_020_CHANGED": os020_before != os020_after,
        "cross_checks": {
            "complete_delta": totals["DIGITAL_IMPLEMENTATION_COMPLETE"]
            - EXPECTED_BEFORE["DIGITAL_IMPLEMENTATION_COMPLETE"],
            "impl_open_delta": EXPECTED_BEFORE["DIGITAL_IMPLEMENTATION_OPEN"]
            - totals["DIGITAL_IMPLEMENTATION_OPEN"],
            "validation_open_unchanged": totals["DIGITAL_VALIDATION_OPEN"]
            == EXPECTED_BEFORE["DIGITAL_VALIDATION_OPEN"],
            "len_next_impl_matches_open": len(impl_items) == totals["DIGITAL_IMPLEMENTATION_OPEN"],
            "len_next_val_matches_open": len(val_items) == totals["DIGITAL_VALIDATION_OPEN"],
            "next_val_only_020": [i["requirement_id"] for i in val_items] == [PRESERVE_UNTOUCHED],
        },
    }


def main() -> int:
    ts = _utc_now()
    truth = _load_wave005_truth()

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
    for key, expected in EXPECTED_BEFORE.items():
        if before_totals.get(key) != expected:
            raise SystemExit(f"pre-closeout {key}={before_totals.get(key)} expected {expected}")

    val_ids_before = [i["requirement_id"] for i in val_reg["all_items"]]
    if val_ids_before != [PRESERVE_UNTOUCHED]:
        raise SystemExit(f"pre-closeout NEXT_VALIDATION={val_ids_before} expected only {PRESERVE_UNTOUCHED}")

    unrelated_impl_before = [
        i["requirement_id"] for i in impl_reg["all_items"] if i["requirement_id"] not in TARGET_IDS
    ]

    os020_before = _semantic_snapshot(before_by_id[PRESERVE_UNTOUCHED])

    after_rows: list[dict[str, Any]] = []
    changed_ids: list[str] = []
    before_states: dict[str, Any] = {}
    after_states: dict[str, Any] = {}
    closed_ids: list[str] = []

    for row in register["requirements"]:
        rid = row["requirement_id"]
        new_row = copy.deepcopy(row)
        if rid not in TARGET_IDS:
            after_rows.append(new_row)
            continue
        before_states[rid] = _semantic_snapshot(row)
        cls = (truth["classification"].get(rid) or {}).get("classification")
        if cls != "IMPLEMENTED_AND_VALIDATED":
            raise SystemExit(f"{rid} classification={cls} — refusing complete without evidence")
        _apply_complete(new_row, rid)
        closed_ids.append(rid)
        after_states[rid] = _semantic_snapshot(new_row)
        if before_states[rid] != after_states[rid]:
            changed_ids.append(rid)
        after_rows.append(new_row)

    after_by_id = {r["requirement_id"]: r for r in after_rows}
    os020_after = _semantic_snapshot(after_by_id[PRESERVE_UNTOUCHED])
    os020_changed = os020_before != os020_after

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
    fam14 = next((f for f in end_goal["families"] if f["id"] == 14), None)

    impl_open_rows = [r for r in after_rows if r["work_state"] == "DIGITAL_IMPLEMENTATION_OPEN"]
    val_open_rows = [r for r in after_rows if r["work_state"] == "DIGITAL_VALIDATION_OPEN"]
    impl_items = [_impl_work_item(r) for r in impl_open_rows]
    val_items = [_val_work_item(r) for r in val_open_rows]

    unrelated_impl_after = [i["requirement_id"] for i in impl_items if i["requirement_id"] not in TARGET_IDS]
    unrelated_impl_changed = 0 if unrelated_impl_before == unrelated_impl_after else 1

    pool = (
        totals["DIGITAL_IMPLEMENTATION_COMPLETE"]
        + totals["DIGITAL_IMPLEMENTATION_OPEN"]
        + totals["DIGITAL_VALIDATION_OPEN"]
    )

    closeout_status = "COMPLETE" if len(closed_ids) == 12 else "PARTIAL"

    diff_doc = {
        "schema": "gunnchos.engineering_wave005.targeted_row_diff.v1",
        "generated_at_utc": ts,
        "wave": "ENGINEERING_WAVE_005",
        "target_ids": TARGET_IDS,
        "changed_ids": changed_ids,
        "unexpected_changed_ids": unexpected,
        "untargeted_rows_changed": untargeted_changed,
        "UNRELATED_IMPLEMENTATION_QUEUE_ROWS_CHANGED": unrelated_impl_changed,
        "OS_PLATFORM_020_CHANGED": os020_changed,
        "before_state": before_states,
        "after_state": after_states,
        "os_platform_020_preserved": {
            "before": os020_before,
            "after": os020_after,
            "changed": os020_changed,
            "work_state": after_by_id[PRESERVE_UNTOUCHED]["work_state"],
            "blocker": after_by_id[PRESERVE_UNTOUCHED].get("blocker"),
            "blocker_class": after_by_id[PRESERVE_UNTOUCHED].get("blocker_class"),
        },
        "accepted_main_evidence": {
            "merge_prs": MERGE_PRS,
            "accepted_main_shas": ACCEPTED_MAIN,
            "required_ci_state": "SUCCESS_ON_MERGED_PRS",
            "aggregate_artifacts": [
                "artifacts/engineering_wave005/WAVE005_AGGREGATE.json",
                "artifacts/engineering_wave005/device_os_mirror/WAVE005_RESULT.json",
                "artifacts/engineering_wave005/device_os_mirror/INTEGRITY_REPAIR_RESULT.json",
                "gunnchos-device-os:artifacts/engineering_wave005/WAVE005_RESULT.json",
            ],
            "wave005_truth": {
                "TARGET_REQUIREMENTS": 12,
                "IMPLEMENTED_AND_VALIDATED": 12,
                "UNCONDITIONAL_TRUE_CLASSIFIERS": 0,
                "WAVE005_COMPLETE_GATE_REQUIRES_12_OF_12": True,
                "WAVE005_POSTMERGE_INTEGRITY_REPAIR": "PASS",
                "NEVER_BEST_CASE_MISSING_INVALID": True,
                "OS_PLATFORM_020_UNTOUCHED": True,
                "BASELINE_COUNTS_UPDATED_ON_WAVE_EVIDENCE": False,
            },
        },
        "claim_boundaries": CLAIM_BOUNDARIES,
        "closeout_assessment": {
            "targets_digital_implementation_complete": closed_ids,
            "targets_remaining_validation_open": [],
            "OS_PLATFORM_020_NOT_COMPLETE": True,
            "OS_PLATFORM_020_CHANGED": os020_changed,
            "independent_digital_reproduction": "PASS" if len(closed_ids) == 12 else "PARTIAL",
            "release_complete": False,
            "WAVE005_COMPLETE_GATE_REQUIRES_12_OF_12": True,
            "ENGINEERING_WAVE_005_CLOSEOUT": closeout_status,
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
            "DIGITAL_CONTROLLABLE_POOL_after": pool,
            "rows_closed": len(closed_ids),
            "rows_moved_to_validation_open": 0,
        },
        "family_14_net_orch": {
            "family_release_level": fam14.get("family_release_level") if fam14 else None,
            "validation_open": fam14.get("validation_open") if fam14 else None,
            "digital_impl_open": fam14.get("digital_impl_open") if fam14 else None,
            "work_state_counts": fam14.get("work_state_counts") if fam14 else None,
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
        os020_before,
        os020_after,
    )
    diff_doc["closeout_validation"] = closeout_validation

    register["generated_at_utc"] = ts
    register["totals"] = totals
    register["requirements"] = after_rows
    # Preserve Wave001–004 history; append Wave005 only.
    register["wave005_targeted_closeout"] = {
        "phase": "ENGINEERING_WAVE_005_TARGETED_CLOSEOUT",
        "targets_changed": len(changed_ids),
        "targets_closed": len(closed_ids),
        "targets_validation_open": 0,
        "accepted_main_shas": ACCEPTED_MAIN,
        "OS_PLATFORM_020": "DIGITAL_VALIDATION_OPEN",
        "OS_PLATFORM_020_CHANGED": os020_changed,
        "ENGINEERING_WAVE_005_CLOSEOUT": closeout_status,
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
        "Wave 005 targeted closeout draft PR pending owner merge",
        f"DIGITAL_IMPLEMENTATION_OPEN={totals['DIGITAL_IMPLEMENTATION_OPEN']} rows need digital engineering",
        f"DIGITAL_VALIDATION_OPEN={totals['DIGITAL_VALIDATION_OPEN']} (OS-PLATFORM-020 sandbox enforcement environment)",
        "OS-PLATFORM-020: re-run mandatory sandbox suite on working isolation backend; PLAIN_SUBPROCESS_COUNTS_AS_SANDBOX=false",
    ]
    remaining["wave005_closeout"] = {
        "targets_closed": closed_ids,
        "targets_validation_open": [],
        "claim_boundaries": CLAIM_BOUNDARIES,
        "OS_PLATFORM_020": {
            "implementation_present": True,
            "validation_state": "DIGITAL_VALIDATION_OPEN",
            "blocker_class": "BLOCKED_ENVIRONMENT",
            "blocker": "SANDBOX_ENFORCEMENT_ENVIRONMENT",
            "plain_subprocess_counts_as_sandbox": False,
            "kernel_sandbox": False,
            "changed": os020_changed,
        },
    }
    (OUT / "REMAINING_GAPS.json").write_text(json.dumps(remaining, indent=2) + "\n", encoding="utf-8")
    (OUT / "REMAINING_GAPS.md").write_text(
        "# Remaining gaps (Wave 005 targeted closeout)\n\n"
        + "\n".join(f"- {b}" for b in remaining["top_blockers"])
        + "\n",
        encoding="utf-8",
    )

    (OUT / "END_GOAL_COVERAGE_MATRIX.json").write_text(json.dumps(end_goal, indent=2) + "\n", encoding="utf-8")
    fam_lines = ["# End goal coverage (family 14 net-orch snapshot)\n"]
    if fam14:
        fam_lines.extend(
            [
                f"- family_release_level: {fam14['family_release_level']}\n",
                f"- validation_open: {fam14['validation_open']}\n",
                f"- digital_impl_open: {fam14['digital_impl_open']}\n",
                f"- DIGITAL_IMPLEMENTATION_COMPLETE in family: "
                f"{fam14['work_state_counts'].get('DIGITAL_IMPLEMENTATION_COMPLETE', 0)}\n",
            ]
        )
    (OUT / "END_GOAL_COVERAGE_MATRIX.md").write_text("".join(fam_lines), encoding="utf-8")

    result["generated_at_utc"] = ts
    result["phase"] = "ENGINEERING_WAVE_005_TARGETED_CLOSEOUT"
    result["totals"] = totals
    result["work_state_counts"] = dict(work_state_counts)
    # Concise Wave005 record; do not overwrite Wave001–004 keys.
    result["ENGINEERING_WAVE_005_TARGETED_CLOSEOUT"] = closeout_validation
    result["wave005_claim_boundaries"] = CLAIM_BOUNDARIES
    result["BASELINE_V2_STATE"] = "DRAFT_PR"
    result["STOP_FOR_OWNER_MERGE"] = True
    result["BASELINE_V2_READY_FOR_OWNER_MERGE"] = closeout_validation[
        "ENGINEERING_WAVE_005_TARGETED_CLOSEOUT_VALIDATION_PASS"
    ]
    result["READY_FOR_OWNER_MERGE"] = False  # flipped true only after remote CI green
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
        "schema": "gunnchos.engineering_wave005.targeted_closeout_result.v1",
        "generated_at_utc": ts,
        "phase": "ENGINEERING_WAVE_005_TARGETED_CLOSEOUT",
        "ENGINEERING_WAVE_005_CLOSEOUT": closeout_status,
        "ENGINEERING_WAVE_005_TARGETED_CLOSEOUT_VALIDATION_PASS": closeout_validation[
            "ENGINEERING_WAVE_005_TARGETED_CLOSEOUT_VALIDATION_PASS"
        ],
        "CURSOR_MERGED_NOTHING": True,
        "READY_FOR_OWNER_MERGE": False,
        "STOP_FOR_OWNER_MERGE": True,
        "prerequisites": {
            "gunnchos-device-os_pr_128": MERGE_PRS["gunnchos-device-os"],
            "gunnchos-7gc-ai-ran-field-kit_pr_102": MERGE_PRS["gunnchos-7gc-ai-ran-field-kit"],
            "accepted_main_shas": ACCEPTED_MAIN,
            "required_ci_state": "SUCCESS",
        },
        "wave005_accepted_main_truth": {
            "TARGET_REQUIREMENTS": 12,
            "IMPLEMENTED_AND_VALIDATED": 12,
            "UNCONDITIONAL_TRUE_CLASSIFIERS": 0,
            "UNCONDITIONAL_TRUE_CLASSIFIERS_COMPUTED": True,
            "WAVE005_COMPLETE_GATE_REQUIRES_12_OF_12": True,
            "WAVE005_POSTMERGE_INTEGRITY_REPAIR": "PASS",
            "BROKEN_EVALUATOR_GATE_RESULT": "REJECTED",
            "NEVER_BEST_CASE_MISSING_INVALID": True,
            "OS_PLATFORM_020_UNTOUCHED": True,
            "BASELINE_COUNTS_UPDATED_ON_WAVE_EVIDENCE": False,
            "portable_provenance": True,
            "priority_authority_ok": True,
            "preference_soft_hard_ok": True,
        },
        "pre_closeout_baseline": EXPECTED_BEFORE,
        "post_closeout_baseline": {
            "ATOMIC_TOTAL": totals["ATOMIC_TOTAL"],
            "DIGITAL_IMPLEMENTATION_COMPLETE": totals["DIGITAL_IMPLEMENTATION_COMPLETE"],
            "DIGITAL_IMPLEMENTATION_OPEN": totals["DIGITAL_IMPLEMENTATION_OPEN"],
            "DIGITAL_VALIDATION_OPEN": totals["DIGITAL_VALIDATION_OPEN"],
            "EVIDENCE_MAPPING_OPEN": totals.get("EVIDENCE_MAPPING_OPEN", 0),
            "DIGITAL_CONTROLLABLE_POOL": pool,
        },
        "targets_digital_implementation_complete": closed_ids,
        "targets_digital_validation_open": [],
        "OS_PLATFORM_020": {
            "implementation_present": True,
            "validation_state": "DIGITAL_VALIDATION_OPEN",
            "blocker_class": "BLOCKED_ENVIRONMENT",
            "blocker": "SANDBOX_ENFORCEMENT_ENVIRONMENT",
            "plain_subprocess_counts_as_sandbox": False,
            "kernel_sandbox": False,
            "OS_PLATFORM_020_CHANGED": os020_changed,
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

    print(
        json.dumps(
            {
                "totals": {k: totals[k] for k in EXPECTED_AFTER},
                "DIGITAL_CONTROLLABLE_POOL": pool,
                "OS_PLATFORM_020_CHANGED": os020_changed,
                "closeout_validation": closeout_validation,
            },
            indent=2,
        )
    )

    if not closeout_validation["ENGINEERING_WAVE_005_TARGETED_CLOSEOUT_VALIDATION_PASS"]:
        return 1
    rc = validate_b41()
    if rc != 0:
        return rc
    print("ENGINEERING_WAVE_005_TARGETED_CLOSEOUT_VALIDATION_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
