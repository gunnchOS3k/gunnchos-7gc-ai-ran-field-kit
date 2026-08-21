"""Validate Wave 009 targeted closeout artifact and register freeze."""
from __future__ import annotations

import json
from pathlib import Path


TARGET_ID = "OS-PLATFORM-020"


def test_targeted_row_diff_freeze():
    root = Path(__file__).resolve().parents[2]
    diff_path = root / "artifacts/engineering_wave009_closeout/TARGETED_ROW_DIFF.json"
    data = json.loads(diff_path.read_text(encoding="utf-8"))
    assert data["untargeted_rows_changed"] == 0
    assert data["UNTARGETED_ROWS_CHANGED"] == 0
    assert data["unexpected_changed_ids"] == []
    assert data["target_ids"] == [TARGET_ID]
    assert data["changed_ids"] == [TARGET_ID]
    assert data["closeout_validation"]["ENGINEERING_WAVE_009_TARGETED_CLOSEOUT_VALIDATION_PASS"] is True
    assert data["claim_boundaries"]["FORMALLY_VERIFIED_SANDBOX"] is False
    assert data["claim_boundaries"]["KERNEL_SANDBOX"] is True
    assert data["claim_boundaries"]["SANDBOX_EXECUTION_VALIDATED"] is True
    assert data["claim_boundaries"]["PLAIN_SUBPROCESS_COUNTS_AS_SANDBOX"] is False
    assert data["closeout_assessment"]["targets_remaining_validation_open"] == []
    assert data["closeout_assessment"]["targets_digital_implementation_complete"] == [TARGET_ID]
    assert data["closeout_assessment"]["validation_queue_empty"] is True
    x = data["closeout_validation"]["cross_checks"]
    assert x["complete_delta"] == 1
    assert x["impl_open_unchanged"] is True
    assert x["validation_open_delta"] == 1
    assert x["validation_queue_empty"] is True
    assert x["impl_queue_identity"] is True
    ind = data["closeout_validation"]["independent_fields"]
    assert ind["IMPLEMENTED_AND_VALIDATED_1"] is True
    assert ind["PARTIAL_false"] is True
    assert ind["KERNEL_SANDBOX_true"] is True
    assert ind["SANDBOX_EXECUTION_VALIDATED_true"] is True
    assert ind["PLAIN_SUBPROCESS_false"] is True
    assert ind["UNCONDITIONAL_TRUE_0"] is True
    assert ind["provenance_trees_identical"] is True
    assert ind["GENUINE_SANDBOX_NOT_AGGREGATE_ALONE"] is True


def test_provenance_binding():
    root = Path(__file__).resolve().parents[2]
    prov = json.loads(
        (root / "artifacts/engineering_wave009_closeout/PROVENANCE_BINDING_RESULT.json").read_text(
            encoding="utf-8"
        )
    )
    assert prov["ENGINEERING_WAVE_009_PROVENANCE_BINDING"] == "PASS"
    assert prov["device_os_pr"] == 131
    assert prov["device_os_final_head"] == "49455df192b071afd97d25a84d4490862dc07952"
    assert prov["device_os_merge_sha"] == "28562a8456207540c205a1c8a6434a491b0a4771"
    assert prov["device_os_tested_tree"] == prov["device_os_accepted_tree"] == "385441f7ff8c6e8f32f7310a11fc09ddd9d49583"
    assert prov["device_os_tree_equivalence"] is True
    assert prov["field_kit_111_merge_sha"] == "89a390be796f418e1b0e21be93bd6b560caef832"
    assert prov["field_kit_112_head"] == "641fb90c8105a1335711736cd59b21c0b8e8bc5e"
    assert prov["field_kit_112_merge_sha"] == "75e2fd101825b46fe6abcf6150c49b2c8abee9c2"
    assert prov["binding"]["trees_identical"] is True
    assert prov["generation_sha_notes"]["BLOCKED_STALE_EVIDENCE"] is False
    assert prov["authoritative_ci"]["run_id"] == 32494141254
    assert prov["authoritative_ci"]["artifact_id"] == 9450933232
    assert (
        prov["authoritative_ci"]["digest"]
        == "sha256:cc97ed02a18b1ccef786d0ad9b6c6dd21be9738cd69605dcdf4e444fa4229a52"
    )
    assert prov["authoritative_ci"]["expired"] is False


def test_validation_queue_emptied():
    root = Path(__file__).resolve().parents[2]
    vdiff = json.loads(
        (root / "artifacts/engineering_wave009_closeout/VALIDATION_QUEUE_DIFF.json").read_text(
            encoding="utf-8"
        )
    )
    val = json.loads(
        (root / "program/digital_ecosystem_baseline_v2/NEXT_DIGITAL_VALIDATION_WORK.json").read_text(
            encoding="utf-8"
        )
    )
    assert vdiff["validation_queue_emptied"] is True
    assert vdiff["after"]["total_open"] == 0
    assert vdiff["after"]["all_items"] == []
    assert vdiff["removed_ids"] == [TARGET_ID]
    assert val["total_open"] == 0
    assert val["all_items"] == []
    assert val["top_priority_items"] == []


def test_claim_boundary_result():
    root = Path(__file__).resolve().parents[2]
    claims = json.loads(
        (root / "artifacts/engineering_wave009_closeout/CLAIM_BOUNDARY_RESULT.json").read_text(
            encoding="utf-8"
        )
    )
    cb = claims["claim_boundaries"]
    assert claims["ENGINEERING_WAVE_009_CLAIM_BOUNDARIES"] == "PASS"
    assert cb["FORMALLY_VERIFIED_SANDBOX"] is False
    assert cb["HARDWARE_TEE_ISOLATION_VALIDATED"] is False
    assert cb["PRODUCTION_SECURITY_CERTIFIED"] is False
    assert cb["THIRD_PARTY_PEN_TESTED"] is False
    assert cb["SELINUX_POLICY_CERTIFIED"] is False
    assert cb["APPARMOR_POLICY_CERTIFIED"] is False
    assert cb["HUMAN_E6"] is False
    assert cb["PHYSICAL_VALIDATION"] is False
    assert cb["KERNEL_SANDBOX"] is True
    assert cb["SANDBOX_EXECUTION_VALIDATED"] is True
    assert cb["PLAIN_SUBPROCESS_COUNTS_AS_SANDBOX"] is False


def test_closeout_result_and_queues():
    root = Path(__file__).resolve().parents[2]
    result = json.loads(
        (root / "artifacts/engineering_wave009_closeout/CLOSEOUT_RESULT.json").read_text(encoding="utf-8")
    )
    reg = json.loads(
        (root / "program/digital_ecosystem_baseline_v2/MASTER_COMPLETION_REGISTER.json").read_text(
            encoding="utf-8"
        )
    )
    impl = json.loads(
        (root / "program/digital_ecosystem_baseline_v2/NEXT_DIGITAL_IMPLEMENTATION_WORK.json").read_text(
            encoding="utf-8"
        )
    )
    val = json.loads(
        (root / "program/digital_ecosystem_baseline_v2/NEXT_DIGITAL_VALIDATION_WORK.json").read_text(
            encoding="utf-8"
        )
    )
    baseline = json.loads(
        (root / "program/digital_ecosystem_baseline_v2/BASELINE_V2_RESULT.json").read_text(encoding="utf-8")
    )
    totals = reg["totals"]
    assert result["ENGINEERING_WAVE_009_TARGETED_CLOSEOUT_VALIDATION_PASS"] is True
    assert result["ENGINEERING_WAVE_009_CLOSEOUT"] == "PASS"
    assert result["CURSOR_MERGED_NOTHING"] is True
    assert result["OS_PLATFORM_020"]["work_state"] == "DIGITAL_IMPLEMENTATION_COMPLETE"
    assert result["OS_PLATFORM_020"]["kernel_sandbox"] is True
    assert result["OS_PLATFORM_020"]["sandbox_execution_validated"] is True
    assert result["OS_PLATFORM_020"]["plain_subprocess_counts_as_sandbox"] is False
    assert result["OS_PLATFORM_020"]["formally_verified_sandbox"] is False
    assert totals["DIGITAL_IMPLEMENTATION_COMPLETE"] == 111
    assert totals["DIGITAL_IMPLEMENTATION_OPEN"] == 51
    assert totals["DIGITAL_VALIDATION_OPEN"] == 0
    assert totals["EVIDENCE_MAPPING_OPEN"] == 0
    assert result["post_closeout_baseline"]["DIGITAL_CONTROLLABLE_POOL"] == 162
    assert len(impl["all_items"]) == 51
    assert impl["total_open"] == 51
    assert len(val["all_items"]) == 0
    assert val["total_open"] == 0
    row020 = next(r for r in reg["requirements"] if r["requirement_id"] == TARGET_ID)
    assert row020["work_state"] == "DIGITAL_IMPLEMENTATION_COMPLETE"
    assert row020["implementation_state"] == "IMPLEMENTED"
    assert row020["verification_state"] == "INDEPENDENTLY_VERIFIED_DIGITAL"
    assert row020.get("kernel_sandbox") is True
    assert row020.get("plain_subprocess_counts_as_sandbox") is False
    assert "ENGINEERING_WAVE_008_TARGETED_CLOSEOUT" in baseline
    assert "ENGINEERING_WAVE_009_TARGETED_CLOSEOUT" in baseline
    assert "wave008_targeted_closeout" in reg
    assert "wave009_targeted_closeout" in reg
    assert result["UNTARGETED_ROWS_CHANGED"] == 0
    assert result["queue_integrity"]["impl_queue_identity_preserved"] is True
