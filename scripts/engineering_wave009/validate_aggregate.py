#!/usr/bin/env python3
"""Validate Wave009 accepted-main provenance remediation aggregate."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AGG = ROOT / "artifacts/engineering_wave009/WAVE009_AGGREGATE.json"
MIRROR = ROOT / "artifacts/engineering_wave009/device_os_mirror"
BASELINE = ROOT / "program/digital_ecosystem_baseline_v2"
QUEUE = BASELINE / "NEXT_DIGITAL_VALIDATION_WORK.json"
BASELINE_RESULT = BASELINE / "BASELINE_V2_RESULT.json"

FINAL_HEAD = "49455df192b071afd97d25a84d4490862dc07952"
MERGE_SHA = "28562a8456207540c205a1c8a6434a491b0a4771"
TESTED_TREE = "385441f7ff8c6e8f32f7310a11fc09ddd9d49583"
ACCEPTED_TREE = "385441f7ff8c6e8f32f7310a11fc09ddd9d49583"
RUN_ID = 32494141254
ART_ID = 9450933232
DIGEST = "sha256:cc97ed02a18b1ccef786d0ad9b6c6dd21be9738cd69605dcdf4e444fa4229a52"

FALSE_CLAIM_KEYS = (
    "FORMALLY_VERIFIED_SANDBOX",
    "PRODUCTION_SECURITY_CERTIFIED",
    "THIRD_PARTY_PEN_TESTED",
    "HARDWARE_TEE_ISOLATION_VALIDATED",
    "SELINUX_POLICY_CERTIFIED",
    "APPARMOR_POLICY_CERTIFIED",
    "HUMAN_E6",
    "PHYSICAL_VALIDATION",
)

MANDATORY_TRUE = (
    "HOST_PRIVATE_READ_BLOCKED",
    "OUTSIDE_WRITE_BLOCKED",
    "NETWORK_DENIED",
    "CHILD_SPAWN_DENIED",
    "CROSS_APP_READ_BLOCKED",
    "PRIVILEGED_CAPABILITY_DENIED",
    "PATH_TRAVERSAL_ESCAPE_BLOCKED",
    "SYMLINK_HOST_ESCAPE_BLOCKED",
    "SYMLINK_CROSS_APP_ESCAPE_BLOCKED",
    "PROC_ROOT_ESCAPE_BLOCKED",
    "MOUNT_ESCAPE_BLOCKED",
    "DANGEROUS_DEVICE_ACCESS_BLOCKED",
    "HOST_ROOT_ESCALATION_BLOCKED",
    "APP_ROOT_READ_ALLOWED",
    "APP_ROOT_WRITE_ALLOWED",
    "NORMAL_PYTHON_EXECUTION_INSIDE_SANDBOX",
    "PRIVATE_ROOT_RW_PASS",
    "SECCOMP_LOADED",
    "CONTROL_HOST_SECRET_READABLE",
    "CONTROL_OUTSIDE_WRITABLE_WHEN_PERMITTED",
    "CONTROL_NETWORK_REACHABLE",
    "CONTROL_CHILD_EXEC_WORKS",
    "CONTROL_CROSS_APP_READABLE",
)


def _fail(errors: list[str]) -> int:
    print({"ok": False, "errors": errors})
    return 1


def main() -> int:
    errors: list[str] = []
    agg = json.loads(AGG.read_text(encoding="utf-8"))
    wave = json.loads((MIRROR / "WAVE009_RESULT.json").read_text(encoding="utf-8"))
    suite = json.loads((MIRROR / "SANDBOX_ENFORCEMENT_RESULT.json").read_text(encoding="utf-8"))
    beh = json.loads((MIRROR / "BEHAVIORAL_NEGATIVE_CONTROL_RESULT.json").read_text(encoding="utf-8"))
    host = json.loads((MIRROR / "HOST_USERNS_CONFIGURATION_RESULT.json").read_text(encoding="utf-8"))
    claims = json.loads((MIRROR / "CLAIM_BOUNDARIES.json").read_text(encoding="utf-8"))
    baseline = json.loads(BASELINE_RESULT.read_text(encoding="utf-8"))
    queue = json.loads(QUEUE.read_text(encoding="utf-8"))
    totals = baseline.get("totals", {})

    # Aggregate provenance bindings to accepted device-os #131.
    if agg.get("device_os_pr") != 131:
        errors.append("device_os_pr_not_131")
    if agg.get("device_os_final_head_sha") != FINAL_HEAD:
        errors.append("final_head_mismatch")
    if agg.get("device_os_merge_sha") != MERGE_SHA:
        errors.append("merge_sha_mismatch")
    if agg.get("device_os_accepted_main") is not True:
        errors.append("accepted_main_not_true")
    if agg.get("device_os_accepted_main_verified") is not True:
        errors.append("accepted_main_not_verified")
    if agg.get("device_os_tree_equivalence") is not True:
        errors.append("tree_equivalence_not_true")
    if agg.get("device_os_tested_tree") != TESTED_TREE:
        errors.append("tested_tree_mismatch")
    if agg.get("device_os_accepted_tree") != ACCEPTED_TREE:
        errors.append("accepted_tree_mismatch")
    if TESTED_TREE != ACCEPTED_TREE:
        errors.append("tested_accepted_trees_not_equivalent")
    if agg.get("authoritative_ci_run") != RUN_ID:
        errors.append("ci_run_mismatch")
    if agg.get("authoritative_artifact_id") != ART_ID:
        errors.append("artifact_id_mismatch")
    if agg.get("authoritative_artifact_digest") != DIGEST:
        errors.append("artifact_digest_mismatch")
    if agg.get("DEVICE_OS_ACCEPTANCE_CONDITION_SATISFIED") is not True:
        errors.append("acceptance_condition_unsatisfied")

    if agg.get("status") != "PASS":
        errors.append("aggregate_status_not_pass")
    if agg.get("TARGET_REQUIREMENTS") != 1:
        errors.append("target_requirements_not_1")
    if agg.get("requirement_ids") != ["OS-PLATFORM-020"]:
        errors.append("unexpected_requirement_ids")
    if agg.get("OS_PLATFORM_020") != "IMPLEMENTED_AND_VALIDATED":
        errors.append("os020_not_validated")
    if wave.get("ENGINEERING_WAVE_009") != "PASS":
        errors.append("mirror_wave_not_pass")
    if wave.get("OS_PLATFORM_020") != "IMPLEMENTED_AND_VALIDATED":
        errors.append("mirror_os020_not_validated")

    # Sandbox / non-root / no-sudo / repair proof.
    if suite.get("SANDBOX_BACKEND") != "bubblewrap":
        errors.append("backend_not_bubblewrap")
    if suite.get("KERNEL_SANDBOX") is not True:
        errors.append("kernel_sandbox_false")
    if suite.get("SANDBOX_EXECUTION_VALIDATED") is not True:
        errors.append("sandbox_execution_not_validated")
    if suite.get("SANDBOX_EXECUTED_AS_ROOT") is not False:
        errors.append("executed_as_root")
    if suite.get("BWRAP_INVOKED_WITH_SUDO") is not False:
        errors.append("bwrap_with_sudo")
    if suite.get("PLAIN_SUBPROCESS_COUNTS_AS_SANDBOX") is not False:
        errors.append("plain_subprocess_claim")
    if suite.get("SECCOMP_LOADED") is not True:
        errors.append("seccomp_not_loaded")
    if suite.get("PRIVATE_ROOT_RW_PASS") is not True:
        errors.append("private_root_rw_fail")
    for key in MANDATORY_TRUE:
        if suite.get(key) is not True:
            errors.append(f"mandatory_probe_failed:{key}")

    before = str(host.get("APPARMOR_RESTRICT_USERNS_BEFORE", wave.get("APPARMOR_RESTRICT_USERNS_BEFORE")))
    after = str(host.get("APPARMOR_RESTRICT_USERNS_AFTER", wave.get("APPARMOR_RESTRICT_USERNS_AFTER")))
    if before != "1":
        errors.append("apparmor_userns_before_not_1")
    if after != "0":
        errors.append("apparmor_userns_after_not_0")
    if wave.get("PRE_REPAIR_UNPRIVILEGED_BWRAP_WORKS") is not False:
        errors.append("pre_repair_bwrap_unexpectedly_true")
    if wave.get("POST_REPAIR_UNPRIVILEGED_BWRAP_WORKS") is not True:
        errors.append("post_repair_bwrap_failed")
    if host.get("POST_REPAIR_UNPRIVILEGED_BWRAP_WORKS") is not True:
        errors.append("host_post_repair_bwrap_failed")

    if beh.get("BEHAVIORAL_NEGATIVE_CONTROL_COUNT", 0) < 12:
        errors.append("insufficient_sabotage_controls")
    if beh.get("BEHAVIORAL_NEGATIVE_CONTROLS_PASS") is not True:
        errors.append("sabotage_controls_failed")
    if wave.get("UNCONDITIONAL_TRUE_CLASSIFIERS") != 0:
        errors.append("unconditional_classifiers_nonzero")
    if wave.get("COMPLETE_GATE_REQUIRES_1_OF_1") is not True:
        errors.append("complete_gate_not_1_of_1")
    gate = wave.get("completion_gate") or {}
    if gate.get("validated_count") != 1 or gate.get("target_count") != 1:
        errors.append("completion_gate_counts_not_1_of_1")

    for key in FALSE_CLAIM_KEYS:
        if claims.get(key) is not False:
            errors.append(f"claim_boundary_not_false:{key}")
    if claims.get("PLAIN_SUBPROCESS_COUNTS_AS_SANDBOX") is not False:
        errors.append("claim_plain_subprocess_not_false")

    # Aggregate evidence itself must remain frozen (no baseline mutation in wave evidence).
    # After targeted closeout lands, live Baseline may already be 111/51/0 — accept either.
    closeout_meta = baseline.get("ENGINEERING_WAVE_009_TARGETED_CLOSEOUT") or {}
    closeout_applied = bool(
        closeout_meta.get("ENGINEERING_WAVE_009_TARGETED_CLOSEOUT_VALIDATION_PASS")
    ) or (baseline.get("phase") == "ENGINEERING_WAVE_009_TARGETED_CLOSEOUT")

    if totals.get("ATOMIC_TOTAL") != 419:
        errors.append("baseline_atomic_total")
    # Wave010+ may reduce OPEN below 51; require pool invariant and non-increase.
    if int(totals.get("DIGITAL_IMPLEMENTATION_OPEN") or 0) > 51:
        errors.append("baseline_impl_open")
    pool = (
        int(totals.get("DIGITAL_IMPLEMENTATION_COMPLETE") or 0)
        + int(totals.get("DIGITAL_IMPLEMENTATION_OPEN") or 0)
        + int(totals.get("DIGITAL_VALIDATION_OPEN") or 0)
    )
    if pool != 162:
        errors.append("baseline_pool")
    if totals.get("EVIDENCE_MAPPING_OPEN") != 0:
        errors.append("baseline_evidence_mapping_open")
    frozen = agg.get("baseline_frozen_verify") or {}
    if frozen.get("DIGITAL_CONTROLLABLE_POOL") != 162:
        errors.append("baseline_controllable_pool")

    if closeout_applied:
        if int(totals.get("DIGITAL_IMPLEMENTATION_COMPLETE") or 0) < 111:
            errors.append("baseline_impl_complete_post_closeout")
        if totals.get("DIGITAL_VALIDATION_OPEN") != 0:
            errors.append("baseline_validation_open_post_closeout")
        if queue.get("total_open") != 0:
            errors.append("validation_queue_not_empty_post_closeout")
        if queue.get("all_items"):
            errors.append("validation_queue_items_not_empty_post_closeout")
    else:
        if totals.get("DIGITAL_IMPLEMENTATION_COMPLETE") != 110:
            errors.append("baseline_impl_complete")
        if totals.get("DIGITAL_VALIDATION_OPEN") != 1:
            errors.append("baseline_validation_open")
        if queue.get("total_open") != 1:
            errors.append("validation_queue_count")
        qids = [i.get("requirement_id") for i in queue.get("all_items", [])]
        if qids != ["OS-PLATFORM-020"]:
            errors.append("validation_queue_not_only_os020")

    if agg.get("BASELINE_COUNTS_UPDATED") is not False:
        errors.append("baseline_counts_updated")
    if agg.get("DIGITAL_VALIDATION_QUEUE_UPDATED") is not False:
        errors.append("validation_queue_updated")
    if agg.get("BASELINE_FILES_CHANGED") != 0:
        errors.append("baseline_files_changed")
    if agg.get("OS_PLATFORM_020_BASELINE_STATE_UNCHANGED") != "DIGITAL_VALIDATION_OPEN":
        errors.append("baseline_state_changed")
    if agg.get("CLOSEOUT_NOT_PERFORMED") is not True:
        errors.append("closeout_performed")
    if agg.get("READY_FOR_OWNER_MERGE") is not True:
        errors.append("ready_for_owner_merge_false")
    if agg.get("CURSOR_MERGED_NOTHING") is not True:
        errors.append("cursor_merged_claim")
    # Ensure Baseline v2 path exists (mutation checked by git diff in CI).
    if not BASELINE.is_dir():
        errors.append("baseline_dir_missing")

    if errors:
        return _fail(errors)

    token = "WAVE009_ACCEPTED_MAIN_PROVENANCE_REMEDIATION_PASS"
    print(
        {
            "ok": True,
            "token": token,
            "WAVE009_ACCEPTED_MAIN_PROVENANCE_REMEDIATION_PASS": True,
            "OS_PLATFORM_020": "IMPLEMENTED_AND_VALIDATED",
            "device_os_final_head_sha": FINAL_HEAD,
            "device_os_merge_sha": MERGE_SHA,
            "authoritative_ci_run": RUN_ID,
            "authoritative_artifact_id": ART_ID,
            "authoritative_artifact_digest": DIGEST,
            "device_os_tree_equivalence": True,
            "BASELINE_COUNTS_UPDATED": False,
            "DIGITAL_VALIDATION_QUEUE_UPDATED": False,
        }
    )
    print(token)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
