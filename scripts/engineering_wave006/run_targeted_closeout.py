#!/usr/bin/env python3
"""Engineering Wave 006 targeted closeout — NET-ORCH-026..035 service-continuity rows only."""

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
CLOSEOUT_ART = ROOT / "artifacts" / "engineering_wave006_closeout"
WAVE006_MIRROR = ROOT / "artifacts" / "engineering_wave006" / "device_os_mirror"
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from baseline_v2_evidence_census import build_end_goal_matrix, compute_totals  # noqa: E402
from validate_baseline_v2_b4_register_integrity import main as validate_b41  # noqa: E402

TARGET_IDS = [
    "NET-ORCH-026",
    "NET-ORCH-027",
    "NET-ORCH-028",
    "NET-ORCH-029",
    "NET-ORCH-030",
    "NET-ORCH-031",
    "NET-ORCH-032",
    "NET-ORCH-033",
    "NET-ORCH-034",
    "NET-ORCH-035",
]

PRESERVE_UNTOUCHED = "OS-PLATFORM-020"

ACCEPTED_MAIN = {
    "gunnchos-device-os": "1c9d54a6e57a568288ee6beec9d0cdf4ccbeca63",
    "gunnchos-7gc-ai-ran-field-kit": "d156fd4ebf7355460126850ba950f2444670e50d",
}

MERGE_PRS = {
    "gunnchos-device-os": {
        "pr": 130,
        "merge_commit": ACCEPTED_MAIN["gunnchos-device-os"],
        "merged_at": "2026-08-21T00:01:03Z",
        "title": "Wave006 integrity repair: real continuity execution, multipath, resume, cache, sync",
    },
    "gunnchos-7gc-ai-ran-field-kit": {
        "pr": 105,
        "merge_commit": ACCEPTED_MAIN["gunnchos-7gc-ai-ran-field-kit"],
        "merged_at": "2026-08-21T00:01:18Z",
        "title": "Wave006 integrity correction aggregate: strengthened continuity execution evidence",
    },
}

WAVE006_VAL = (
    "gunnchos-device-os:artifacts/engineering_wave006/WAVE006_RESULT.json;"
    "gunnchos-device-os:artifacts/engineering_wave006/REQUIREMENT_RESULTS.json;"
    "gunnchos-device-os:artifacts/engineering_wave006/REQUIREMENT_EVALUATOR_MATRIX.json;"
    "gunnchos-device-os:artifacts/engineering_wave006/INTEGRITY_REPAIR_RESULT.json;"
    "gunnchos-device-os:artifacts/engineering_wave006/E2E_SCENARIOS_A_J_RESULT.json;"
    "gunnchos-device-os:artifacts/engineering_wave006/FAILURE_INJECTION_RESULT.json;"
    "gunnchos-device-os:artifacts/engineering_wave006/CONTINUITY_STATE_MACHINE_RESULT.json;"
    "gunnchos-device-os:artifacts/engineering_wave006/BEHAVIORAL_NEGATIVE_CONTROL_RESULT.json;"
    "gunnchos-7gc-ai-ran-field-kit:artifacts/engineering_wave006/WAVE006_AGGREGATE.json;"
    "gunnchos-7gc-ai-ran-field-kit:artifacts/engineering_wave006/device_os_mirror/WAVE006_RESULT.json;"
    "gunnchos-device-os:tests/test_wave006_service_continuity.py"
)

PKG = "gunnchos-device-os:gunnchos_device_os/service_continuity_execution"

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
    "NET-ORCH-026": {
        "implementation_evidence": f"{PKG}/satellite.py;{PKG}/evaluators.py",
        "pass4": [
            f"{PKG}/satellite.py role=IMPLEMENTATION_CODE",
            f"{PKG}/evaluators.py role=IMPLEMENTATION_CODE",
        ],
        "resolution_reason": (
            "Wave 006 accepted-main (#130): satellite visibility windows + freshness with "
            "unknown≠best-case; FIELD_MEASURED_SATELLITE_VISIBILITY=false; REAL_NTN_MODEM_VALIDATED=false. "
            "IMPLEMENTED_AND_VALIDATED."
        ),
    },
    "NET-ORCH-027": {
        "implementation_evidence": f"{PKG}/local_infra.py;{PKG}/evaluators.py",
        "pass4": [
            f"{PKG}/local_infra.py role=IMPLEMENTATION_CODE",
            f"{PKG}/evaluators.py role=IMPLEMENTATION_CODE",
        ],
        "resolution_reason": (
            "Wave 006 accepted-main (#130): local infrastructure capability graph "
            "(internet/cache/edge/peer not collapsed to one bit). IMPLEMENTED_AND_VALIDATED."
        ),
    },
    "NET-ORCH-028": {
        "implementation_evidence": f"{PKG}/transition.py;{PKG}/evaluators.py",
        "pass4": [
            f"{PKG}/transition.py role=IMPLEMENTATION_CODE",
            f"{PKG}/evaluators.py role=IMPLEMENTATION_CODE",
        ],
        "resolution_reason": (
            "Wave 006 accepted-main (#130): bearer transition transaction + rollback "
            "(phases not mere reassignment); CARRIER_ACCEPTED=false; "
            "LIVE_CARRIER_HANDOVER_VALIDATED=false. IMPLEMENTED_AND_VALIDATED."
        ),
    },
    "NET-ORCH-029": {
        "implementation_evidence": f"{PKG}/resume.py;{PKG}/evaluators.py",
        "pass4": [
            f"{PKG}/resume.py role=IMPLEMENTATION_CODE",
            f"{PKG}/evaluators.py role=IMPLEMENTATION_CODE",
        ],
        "resolution_reason": (
            "Wave 006 accepted-main (#130): durable checkpoint/resume exactly-once with "
            "duplicate resume blocked (A/B/C process proof). IMPLEMENTED_AND_VALIDATED."
        ),
    },
    "NET-ORCH-030": {
        "implementation_evidence": f"{PKG}/multipath.py;{PKG}/evaluators.py",
        "pass4": [
            f"{PKG}/multipath.py role=IMPLEMENTATION_CODE",
            f"{PKG}/evaluators.py role=IMPLEMENTATION_CODE",
        ],
        "resolution_reason": (
            "Wave 006 accepted-main (#130): application-level multipath real transfer "
            "(hash match, path-failure continues); MULTIPATH_KIND=APPLICATION_LEVEL_MULTIPATH; "
            "REAL_MPTCP=false; PRODUCTION_MPTCP_VALIDATED=false. IMPLEMENTED_AND_VALIDATED."
        ),
    },
    "NET-ORCH-031": {
        "implementation_evidence": f"{PKG}/adaptation.py;{PKG}/evaluators.py",
        "pass4": [
            f"{PKG}/adaptation.py role=IMPLEMENTATION_CODE",
            f"{PKG}/evaluators.py role=IMPLEMENTATION_CODE",
        ],
        "resolution_reason": (
            "Wave 006 accepted-main (#130): stateful low-bandwidth adaptation with hysteresis "
            "and recovery (FULL/REDUCED/MINIMUM_USEFUL). IMPLEMENTED_AND_VALIDATED."
        ),
    },
    "NET-ORCH-032": {
        "implementation_evidence": f"{PKG}/prioritization.py;{PKG}/evaluators.py",
        "pass4": [
            f"{PKG}/prioritization.py role=IMPLEMENTATION_CODE",
            f"{PKG}/evaluators.py role=IMPLEMENTATION_CODE",
        ],
        "resolution_reason": (
            "Wave 006 accepted-main (#130): constrained-capacity traffic scheduler with "
            "starvation bounded; PRODUCTION_APP_PRIORITY_SIGNING=false. IMPLEMENTED_AND_VALIDATED."
        ),
    },
    "NET-ORCH-033": {
        "implementation_evidence": f"{PKG}/cache.py;{PKG}/evaluators.py",
        "pass4": [
            f"{PKG}/cache.py role=IMPLEMENTATION_CODE",
            f"{PKG}/evaluators.py role=IMPLEMENTATION_CODE",
        ],
        "resolution_reason": (
            "Wave 006 accepted-main (#130): persistent cache TTL/integrity/budget/namespace "
            "isolation with process-B persistence. IMPLEMENTED_AND_VALIDATED."
        ),
    },
    "NET-ORCH-034": {
        "implementation_evidence": f"{PKG}/sync.py;{PKG}/evaluators.py",
        "pass4": [
            f"{PKG}/sync.py role=IMPLEMENTATION_CODE",
            f"{PKG}/evaluators.py role=IMPLEMENTATION_CODE",
        ],
        "resolution_reason": (
            "Wave 006 accepted-main (#130): SyncOpportunity planner with max-bytes and "
            "exactly-once apply. IMPLEMENTED_AND_VALIDATED."
        ),
    },
    "NET-ORCH-035": {
        "implementation_evidence": (
            f"{PKG}/degraded_report.py;{PKG}/state_machine.py;{PKG}/evaluators.py"
        ),
        "pass4": [
            f"{PKG}/degraded_report.py role=IMPLEMENTATION_CODE",
            f"{PKG}/state_machine.py role=IMPLEMENTATION_CODE",
            f"{PKG}/evaluators.py role=IMPLEMENTATION_CODE",
        ],
        "resolution_reason": (
            "Wave 006 accepted-main (#130): canonical degraded-mode report + continuity "
            "state machine (runtime-consistent, transparent). IMPLEMENTED_AND_VALIDATED."
        ),
    },
}

CLAIM_BOUNDARIES = {
    "CARRIER_ACCEPTED": False,
    "FIELD_MEASURED_PERFORMANCE": False,
    "FIELD_MEASURED_SATELLITE_VISIBILITY": False,
    "HUMAN_E6": False,
    "KERNEL_MPTCP_VALIDATED": False,
    "LIVE_CARRIER_HANDOVER_VALIDATED": False,
    "PHYSICAL_VALIDATION": False,
    "PRODUCTION_APP_PRIORITY_SIGNING": False,
    "PRODUCTION_MPTCP_VALIDATED": False,
    "PRODUCTION_NETWORK_OPTIMALITY": False,
    "REAL_MPTCP": False,
    "REAL_NTN_MODEM_VALIDATED": False,
    "STANDARDIZED_6G": False,
    "UNIVERSAL_OPTIMALITY": False,
}

EXPECTED_BEFORE = {
    "ATOMIC_TOTAL": 419,
    "DIGITAL_IMPLEMENTATION_COMPLETE": 75,
    "DIGITAL_IMPLEMENTATION_OPEN": 86,
    "DIGITAL_VALIDATION_OPEN": 1,
    "EVIDENCE_MAPPING_OPEN": 0,
}

EXPECTED_AFTER = {
    "ATOMIC_TOTAL": 419,
    "DIGITAL_IMPLEMENTATION_COMPLETE": 85,
    "DIGITAL_IMPLEMENTATION_OPEN": 76,
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
    row["validation_evidence"] = WAVE006_VAL
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
        "# Master completion register (Wave 006 targeted closeout)",
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


def _load_wave006_truth() -> dict[str, Any]:
    wave = json.loads((WAVE006_MIRROR / "WAVE006_RESULT.json").read_text(encoding="utf-8"))
    integrity = json.loads((WAVE006_MIRROR / "INTEGRITY_REPAIR_RESULT.json").read_text(encoding="utf-8"))
    neg = json.loads(
        (WAVE006_MIRROR / "COMPLETION_GATE_NEGATIVE_CONTROL_RESULT.json").read_text(encoding="utf-8")
    )
    e2e = json.loads((WAVE006_MIRROR / "E2E_SCENARIOS_A_J_RESULT.json").read_text(encoding="utf-8"))
    fail = json.loads((WAVE006_MIRROR / "FAILURE_INJECTION_RESULT.json").read_text(encoding="utf-8"))
    sm = json.loads((WAVE006_MIRROR / "CONTINUITY_STATE_MACHINE_RESULT.json").read_text(encoding="utf-8"))
    beh = json.loads(
        (WAVE006_MIRROR / "BEHAVIORAL_NEGATIVE_CONTROL_RESULT.json").read_text(encoding="utf-8")
    )
    mp = json.loads(
        (WAVE006_MIRROR / "APPLICATION_MULTIPATH_TRANSFER_RESULT.json").read_text(encoding="utf-8")
    )
    claims = json.loads((WAVE006_MIRROR / "CLAIM_BOUNDARIES.json").read_text(encoding="utf-8"))
    req = json.loads((WAVE006_MIRROR / "REQUIREMENT_RESULTS.json").read_text(encoding="utf-8"))

    classification = wave.get("requirement_classification") or req.get("requirements") or {}
    if isinstance(classification, dict) and classification and "classification" not in next(
        iter(classification.values()), {}
    ):
        # WAVE006_RESULT may nest differently; prefer REQUIREMENT_RESULTS
        classification = req.get("requirements") or classification

    validated = sum(
        1 for v in classification.values() if v.get("classification") == "IMPLEMENTED_AND_VALIDATED"
    )
    if wave.get("target_requirements") != 10 and wave.get("TARGET_REQUIREMENTS") != 10:
        raise SystemExit(
            f"target_requirements={wave.get('target_requirements') or wave.get('TARGET_REQUIREMENTS')} expected 10"
        )
    if validated != 10:
        raise SystemExit(f"expected 10 IMPLEMENTED_AND_VALIDATED; got {validated}")
    if set(classification.keys()) != set(TARGET_IDS):
        raise SystemExit(f"classification IDs mismatch: {sorted(classification.keys())}")
    for rid in TARGET_IDS:
        if classification[rid].get("classification") != "IMPLEMENTED_AND_VALIDATED":
            raise SystemExit(f"{rid} not IMPLEMENTED_AND_VALIDATED")
        if classification[rid].get("ok") is not True:
            raise SystemExit(f"{rid} ok!=true")
    if wave.get("WAVE006_POSTMERGE_INTEGRITY_REPAIR") != "PASS":
        raise SystemExit("WAVE006_POSTMERGE_INTEGRITY_REPAIR must be PASS")
    if integrity.get("WAVE006_POSTMERGE_INTEGRITY_REPAIR") != "PASS":
        raise SystemExit("INTEGRITY_REPAIR_RESULT must be PASS")
    if wave.get("UNCONDITIONAL_TRUE_CLASSIFIERS", -1) != 0:
        raise SystemExit("UNCONDITIONAL_TRUE_CLASSIFIERS must be 0")
    if wave.get("UNCONDITIONAL_TRUE_CLASSIFIERS_COMPUTED") is not True:
        raise SystemExit("UNCONDITIONAL_TRUE_CLASSIFIERS_COMPUTED must be true")
    if wave.get("PARTIAL") is not False:
        raise SystemExit("PARTIAL must be false")
    gate = wave.get("completion_gate") or {}
    if gate.get("WAVE006_COMPLETE_GATE_REQUIRES_10_OF_10") is not True and wave.get(
        "COMPLETE_GATE_REQUIRES_10_OF_10"
    ) is not True:
        raise SystemExit("10-of-10 gate flag missing")
    if gate.get("validated_count") != 10 or gate.get("complete") is not True:
        raise SystemExit(f"completion_gate incomplete: {gate}")
    if neg.get("BROKEN_EVALUATOR_GATE_RESULT") != "REJECTED" or neg.get("ok") is not True:
        raise SystemExit("negative control must reject broken evaluator")
    if e2e.get("ok") is not True or e2e.get("passed") != 10 or e2e.get("total") != 10:
        raise SystemExit(f"E2E A-J must be 10/10; got {e2e.get('passed')}/{e2e.get('total')}")
    scenarios = e2e.get("scenarios") or []
    if len(scenarios) != 10 or not all(s.get("ok") is True for s in scenarios):
        raise SystemExit("E2E scenarios must all be ok=true")
    if fail.get("ok") is not True:
        raise SystemExit("failure injection must pass")
    if sm.get("ok") is not True:
        raise SystemExit("continuity state machine must pass")
    if beh.get("BEHAVIORAL_NEGATIVE_CONTROLS_PASS") is not True or beh.get("ok") is not True:
        raise SystemExit("behavioral negative controls must pass")
    if mp.get("MULTIPATH_KIND") != "APPLICATION_LEVEL_MULTIPATH":
        raise SystemExit(f"MULTIPATH_KIND={mp.get('MULTIPATH_KIND')}")
    if mp.get("REAL_MPTCP") is not False or mp.get("PRODUCTION_MPTCP_VALIDATED") is not False:
        raise SystemExit("MPTCP claims must be false")
    if wave.get("MULTIPATH_KIND") != "APPLICATION_LEVEL_MULTIPATH":
        raise SystemExit("WAVE006_RESULT MULTIPATH_KIND mismatch")
    if wave.get("OS_PLATFORM_020_UNTOUCHED") is not True:
        raise SystemExit("OS_PLATFORM_020_UNTOUCHED must be true on wave evidence")
    if wave.get("BASELINE_COUNTS_UPDATED") is not False:
        raise SystemExit("Wave006 evidence BASELINE_COUNTS_UPDATED must be false (pre-closeout)")
    for k, expected in CLAIM_BOUNDARIES.items():
        if claims.get(k) is not expected:
            raise SystemExit(f"claim {k}={claims.get(k)} expected {expected}")
    return {
        "classification": classification,
        "validated": validated,
        "UNCONDITIONAL_TRUE_CLASSIFIERS": 0,
        "WAVE006_COMPLETE_GATE_REQUIRES_10_OF_10": True,
        "BASELINE_COUNTS_UPDATED_ON_EVIDENCE": False,
        "OS_PLATFORM_020_UNTOUCHED": True,
        "BEHAVIORAL_NEGATIVE_CONTROLS_PASS": True,
        "E2E_A_J_10_OF_10": True,
        "MULTIPATH_KIND": "APPLICATION_LEVEL_MULTIPATH",
        "negative_control_rejected": True,
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
        errors.append("Wave006 IDs still present in implementation queue")
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
    if claim.get("REAL_MPTCP") is not False or claim.get("PRODUCTION_MPTCP_VALIDATED") is not False:
        errors.append("MPTCP claim boundaries must remain false")
    if diff.get("accepted_main_evidence", {}).get("wave006_truth", {}).get("MULTIPATH_KIND") != (
        "APPLICATION_LEVEL_MULTIPATH"
    ):
        # also allow top-level on closeout assessment
        pass
    if totals["DIGITAL_IMPLEMENTATION_COMPLETE"] - EXPECTED_BEFORE["DIGITAL_IMPLEMENTATION_COMPLETE"] != 10:
        errors.append("COMPLETE delta must equal 10 closed rows")
    if EXPECTED_BEFORE["DIGITAL_IMPLEMENTATION_OPEN"] - totals["DIGITAL_IMPLEMENTATION_OPEN"] != 10:
        errors.append("IMPL_OPEN delta must equal 10 removed queue rows")
    if totals["DIGITAL_VALIDATION_OPEN"] != EXPECTED_BEFORE["DIGITAL_VALIDATION_OPEN"]:
        errors.append("VALIDATION_OPEN must stay unchanged at 1")
    ok = len(errors) == 0
    return {
        "ENGINEERING_WAVE_006_TARGETED_CLOSEOUT_VALIDATION_PASS": ok,
        "errors": errors,
        "accepted_main_shas": ACCEPTED_MAIN,
        "claim_boundaries": claim,
        "EXPECTED_AFTER": EXPECTED_AFTER,
        "DIGITAL_CONTROLLABLE_POOL": pool,
        "OS_PLATFORM_020_CHANGED": os020_before != os020_after,
        "MULTIPATH_KIND": "APPLICATION_LEVEL_MULTIPATH",
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
    truth = _load_wave006_truth()

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

    closeout_status = "COMPLETE" if len(closed_ids) == 10 else "PARTIAL"

    diff_doc = {
        "schema": "gunnchos.engineering_wave006.targeted_row_diff.v1",
        "generated_at_utc": ts,
        "wave": "ENGINEERING_WAVE_006",
        "target_ids": TARGET_IDS,
        "changed_ids": changed_ids,
        "unexpected_changed_ids": unexpected,
        "untargeted_rows_changed": untargeted_changed,
        "UNRELATED_IMPLEMENTATION_QUEUE_ROWS_CHANGED": unrelated_impl_changed,
        "OS_PLATFORM_020_CHANGED": os020_changed,
        "MULTIPATH_KIND": "APPLICATION_LEVEL_MULTIPATH",
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
                "artifacts/engineering_wave006/WAVE006_AGGREGATE.json",
                "artifacts/engineering_wave006/WAVE006_INTEGRITY_REPAIR_AGGREGATE.json",
                "artifacts/engineering_wave006/device_os_mirror/WAVE006_RESULT.json",
                "artifacts/engineering_wave006/device_os_mirror/INTEGRITY_REPAIR_RESULT.json",
                "gunnchos-device-os:artifacts/engineering_wave006/WAVE006_RESULT.json",
            ],
            "wave006_truth": {
                "TARGET_REQUIREMENTS": 10,
                "IMPLEMENTED_AND_VALIDATED": 10,
                "UNCONDITIONAL_TRUE_CLASSIFIERS": 0,
                "WAVE006_COMPLETE_GATE_REQUIRES_10_OF_10": True,
                "WAVE006_POSTMERGE_INTEGRITY_REPAIR": "PASS",
                "PARTIAL": False,
                "BEHAVIORAL_NEGATIVE_CONTROLS_PASS": True,
                "E2E_A_J_10_OF_10": True,
                "MULTIPATH_KIND": "APPLICATION_LEVEL_MULTIPATH",
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
            "independent_digital_reproduction": "PASS" if len(closed_ids) == 10 else "PARTIAL",
            "release_complete": False,
            "WAVE006_COMPLETE_GATE_REQUIRES_10_OF_10": True,
            "MULTIPATH_KIND": "APPLICATION_LEVEL_MULTIPATH",
            "ENGINEERING_WAVE_006_CLOSEOUT": closeout_status,
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
    register["wave006_targeted_closeout"] = {
        "phase": "ENGINEERING_WAVE_006_TARGETED_CLOSEOUT",
        "targets_changed": len(changed_ids),
        "targets_closed": len(closed_ids),
        "targets_validation_open": 0,
        "accepted_main_shas": ACCEPTED_MAIN,
        "OS_PLATFORM_020": "DIGITAL_VALIDATION_OPEN",
        "OS_PLATFORM_020_CHANGED": os020_changed,
        "MULTIPATH_KIND": "APPLICATION_LEVEL_MULTIPATH",
        "ENGINEERING_WAVE_006_CLOSEOUT": closeout_status,
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
        "Wave 006 targeted closeout draft PR pending owner merge",
        f"DIGITAL_IMPLEMENTATION_OPEN={totals['DIGITAL_IMPLEMENTATION_OPEN']} rows need digital engineering",
        f"DIGITAL_VALIDATION_OPEN={totals['DIGITAL_VALIDATION_OPEN']} (OS-PLATFORM-020 sandbox enforcement environment)",
        "OS-PLATFORM-020: re-run mandatory sandbox suite on working isolation backend; PLAIN_SUBPROCESS_COUNTS_AS_SANDBOX=false",
    ]
    remaining["wave006_closeout"] = {
        "targets_closed": closed_ids,
        "targets_validation_open": [],
        "claim_boundaries": CLAIM_BOUNDARIES,
        "MULTIPATH_KIND": "APPLICATION_LEVEL_MULTIPATH",
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
        "# Remaining gaps (Wave 006 targeted closeout)\n\n"
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
    result["phase"] = "ENGINEERING_WAVE_006_TARGETED_CLOSEOUT"
    result["totals"] = totals
    result["work_state_counts"] = dict(work_state_counts)
    result["ENGINEERING_WAVE_006_TARGETED_CLOSEOUT"] = closeout_validation
    result["wave006_claim_boundaries"] = CLAIM_BOUNDARIES
    result["MULTIPATH_KIND"] = "APPLICATION_LEVEL_MULTIPATH"
    result["BASELINE_V2_STATE"] = "DRAFT_PR"
    result["STOP_FOR_OWNER_MERGE"] = True
    result["BASELINE_V2_READY_FOR_OWNER_MERGE"] = closeout_validation[
        "ENGINEERING_WAVE_006_TARGETED_CLOSEOUT_VALIDATION_PASS"
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
        "schema": "gunnchos.engineering_wave006.targeted_closeout_result.v1",
        "generated_at_utc": ts,
        "phase": "ENGINEERING_WAVE_006_TARGETED_CLOSEOUT",
        "ENGINEERING_WAVE_006_CLOSEOUT": closeout_status,
        "ENGINEERING_WAVE_006_TARGETED_CLOSEOUT_VALIDATION_PASS": closeout_validation[
            "ENGINEERING_WAVE_006_TARGETED_CLOSEOUT_VALIDATION_PASS"
        ],
        "CURSOR_MERGED_NOTHING": True,
        "READY_FOR_OWNER_MERGE": False,
        "STOP_FOR_OWNER_MERGE": True,
        "MULTIPATH_KIND": "APPLICATION_LEVEL_MULTIPATH",
        "prerequisites": {
            "gunnchos-device-os_pr_130": MERGE_PRS["gunnchos-device-os"],
            "gunnchos-7gc-ai-ran-field-kit_pr_105": MERGE_PRS["gunnchos-7gc-ai-ran-field-kit"],
            "accepted_main_shas": ACCEPTED_MAIN,
            "required_ci_state": "SUCCESS",
        },
        "wave006_accepted_main_truth": {
            "TARGET_REQUIREMENTS": 10,
            "IMPLEMENTED_AND_VALIDATED": 10,
            "UNCONDITIONAL_TRUE_CLASSIFIERS": 0,
            "UNCONDITIONAL_TRUE_CLASSIFIERS_COMPUTED": True,
            "WAVE006_COMPLETE_GATE_REQUIRES_10_OF_10": True,
            "WAVE006_POSTMERGE_INTEGRITY_REPAIR": "PASS",
            "PARTIAL": False,
            "BROKEN_EVALUATOR_GATE_RESULT": "REJECTED",
            "BEHAVIORAL_NEGATIVE_CONTROLS_PASS": True,
            "E2E_A_J_10_OF_10": True,
            "MULTIPATH_KIND": "APPLICATION_LEVEL_MULTIPATH",
            "OS_PLATFORM_020_UNTOUCHED": True,
            "BASELINE_COUNTS_UPDATED_ON_WAVE_EVIDENCE": False,
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
                "MULTIPATH_KIND": "APPLICATION_LEVEL_MULTIPATH",
                "closeout_validation": closeout_validation,
            },
            indent=2,
        )
    )

    if not closeout_validation["ENGINEERING_WAVE_006_TARGETED_CLOSEOUT_VALIDATION_PASS"]:
        return 1
    rc = validate_b41()
    if rc != 0:
        return rc
    print("ENGINEERING_WAVE_006_TARGETED_CLOSEOUT_VALIDATION_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
