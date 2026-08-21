"""Wave009 accepted-main provenance remediation checks — no Baseline mutation."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

FINAL_HEAD = "49455df192b071afd97d25a84d4490862dc07952"
MERGE_SHA = "28562a8456207540c205a1c8a6434a491b0a4771"
RUN_ID = 32494141254
ART_ID = 9450933232
DIGEST = "sha256:cc97ed02a18b1ccef786d0ad9b6c6dd21be9738cd69605dcdf4e444fa4229a52"


def test_aggregate_provenance_binds_accepted_device_os() -> None:
    agg = json.loads((ROOT / "artifacts/engineering_wave009/WAVE009_AGGREGATE.json").read_text())
    assert agg["status"] == "PASS"
    assert agg["device_os_pr"] == 131
    assert agg["device_os_final_head_sha"] == FINAL_HEAD
    assert agg["device_os_merge_sha"] == MERGE_SHA
    assert agg["device_os_accepted_main"] is True
    assert agg["device_os_accepted_main_verified"] is True
    assert agg["device_os_tree_equivalence"] is True
    assert agg["authoritative_ci_run"] == RUN_ID
    assert agg["authoritative_artifact_id"] == ART_ID
    assert agg["authoritative_artifact_digest"] == DIGEST
    assert agg["DEVICE_OS_ACCEPTANCE_CONDITION_SATISFIED"] is True
    assert agg["TARGET_REQUIREMENTS"] == 1
    assert agg["requirement_ids"] == ["OS-PLATFORM-020"]
    assert agg["BASELINE_FILES_CHANGED"] == 0
    assert agg["BASELINE_COUNTS_UPDATED"] is False
    assert agg["DIGITAL_VALIDATION_QUEUE_UPDATED"] is False
    assert agg["OS_PLATFORM_020_BASELINE_STATE_UNCHANGED"] == "DIGITAL_VALIDATION_OPEN"
    assert agg["CLOSEOUT_NOT_PERFORMED"] is True
    assert agg["READY_FOR_OWNER_MERGE"] is True
    assert agg["CURSOR_MERGED_NOTHING"] is True


def test_mirror_kernel_sandbox_and_claim_boundaries() -> None:
    suite = json.loads(
        (ROOT / "artifacts/engineering_wave009/device_os_mirror/SANDBOX_ENFORCEMENT_RESULT.json").read_text()
    )
    claims = json.loads(
        (ROOT / "artifacts/engineering_wave009/device_os_mirror/CLAIM_BOUNDARIES.json").read_text()
    )
    wave = json.loads(
        (ROOT / "artifacts/engineering_wave009/device_os_mirror/WAVE009_RESULT.json").read_text()
    )
    assert suite["SANDBOX_BACKEND"] == "bubblewrap"
    assert suite["KERNEL_SANDBOX"] is True
    assert suite["SANDBOX_EXECUTED_AS_ROOT"] is False
    assert suite["BWRAP_INVOKED_WITH_SUDO"] is False
    assert suite["PLAIN_SUBPROCESS_COUNTS_AS_SANDBOX"] is False
    assert suite["SECCOMP_LOADED"] is True
    assert suite["PRIVATE_ROOT_RW_PASS"] is True
    assert wave["APPARMOR_RESTRICT_USERNS_BEFORE"] in (1, "1")
    assert wave["APPARMOR_RESTRICT_USERNS_AFTER"] in (0, "0")
    assert wave["PRE_REPAIR_UNPRIVILEGED_BWRAP_WORKS"] is False
    assert wave["POST_REPAIR_UNPRIVILEGED_BWRAP_WORKS"] is True
    for key in (
        "FORMALLY_VERIFIED_SANDBOX",
        "PRODUCTION_SECURITY_CERTIFIED",
        "THIRD_PARTY_PEN_TESTED",
        "HARDWARE_TEE_ISOLATION_VALIDATED",
        "SELINUX_POLICY_CERTIFIED",
        "APPARMOR_POLICY_CERTIFIED",
        "HUMAN_E6",
        "PHYSICAL_VALIDATION",
        "PLAIN_SUBPROCESS_COUNTS_AS_SANDBOX",
    ):
        assert claims[key] is False


def test_baseline_frozen_counts() -> None:
    baseline = json.loads(
        (ROOT / "program/digital_ecosystem_baseline_v2/BASELINE_V2_RESULT.json").read_text()
    )
    queue = json.loads(
        (ROOT / "program/digital_ecosystem_baseline_v2/NEXT_DIGITAL_VALIDATION_WORK.json").read_text()
    )
    totals = baseline["totals"]
    assert totals["ATOMIC_TOTAL"] == 419
    assert totals["DIGITAL_IMPLEMENTATION_COMPLETE"] == 110
    assert totals["DIGITAL_IMPLEMENTATION_OPEN"] == 51
    assert totals["DIGITAL_VALIDATION_OPEN"] == 1
    assert totals["EVIDENCE_MAPPING_OPEN"] == 0
    assert queue["total_open"] == 1
    assert [i["requirement_id"] for i in queue["all_items"]] == ["OS-PLATFORM-020"]


def test_validate_script_emits_provenance_remediation_pass() -> None:
    proc = subprocess.run(
        ["python3", "scripts/engineering_wave009/validate_aggregate.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "WAVE009_ACCEPTED_MAIN_PROVENANCE_REMEDIATION_PASS" in proc.stdout
