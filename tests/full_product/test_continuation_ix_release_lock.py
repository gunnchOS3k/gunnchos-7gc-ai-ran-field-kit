"""Cont IX digital release lock + release firewall tests."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
CONT_IX = ROOT / "program" / "full_product" / "continuation_ix"
CONT_VIII = ROOT / "program" / "full_product" / "continuation_viii"
FIREWALL = ROOT / "scripts" / "validate_release_firewall.py"
PROVE = ROOT / "scripts" / "prove_full_product_continuation_ix.py"

REQUIRED_BLOCKER_FIELDS = {
    "id",
    "product",
    "readiness_gate",
    "bucket",
    "exact_gap",
    "exact_next_action",
    "owner_repo",
    "owner_file",
    "status",
}


def _accepted_sha(entry) -> str:
    if isinstance(entry, dict):
        return str(entry.get("sha") or "")
    return str(entry or "")


def test_cont_ix_prove_script_exists():
    assert PROVE.exists()
    text = PROVE.read_text(encoding="utf-8")
    assert "CONTINUATION_IX_DIGITAL_RELEASE_LOCK" in text
    assert "7c6b955be933e050f81358f25077866f37a493bd" in text
    assert "06366da047a6938646acb01e016d19318fabab70" in text
    assert "a710f35559252f36f0e6af7e025a5958df0906e3" in text
    assert "IX-D-001" in text
    assert "CONDITIONAL_VENDOR_COLLATERAL" in text


def test_cont_ix_artifacts_exist_and_honest():
    for name in (
        "ACCEPTED_MAIN_LOCK.json",
        "READINESS_REPROOF.json",
        "BLOCKER_BURNDOWN.json",
        "PRODUCT_RELEASE_MATRIX.json",
        "PRE_EVT_HANDOFF_MATRIX.json",
        "VENDOR_COLLATERAL_REQUESTS.json",
        "CONTINUATION_IX_REPORT_A_T.md",
        "continuation_ix_sibling_draft_registry.yaml",
    ):
        assert (CONT_IX / name).exists(), name

    lock = json.loads((CONT_IX / "ACCEPTED_MAIN_LOCK.json").read_text(encoding="utf-8"))
    assert lock["continuation"] == "IX"
    assert lock["digital_release_lock_complete"] is True
    assert lock["ready_for_npi_dfm_and_evt_quotation"] is True
    assert lock.get("final_umbrella") is False
    assert lock["physical_execution_freeze"] is True
    assert lock["recommendation"] == "READY_FOR_NPI_DFM_AND_EVT_QUOTATION"
    assert lock["digital_open"] == 0
    assert _accepted_sha(lock["accepted_mains"]["gunnchos-7gc-ai-ran-field-kit"]).startswith(
        "5a03fa2"
    )
    assert _accepted_sha(lock["accepted_mains"]["gunnchos-device-os"]).startswith("1d4883d")
    assert _accepted_sha(
        lock["accepted_mains"]["gunnchos-hardware-industrial-design"]
    ).startswith("cd1d906")
    ci = (lock.get("evidence") or {}).get("device_os_digital_lock_ci") or {}
    assert ci.get("ok") is True
    assert ci.get("run_id") == 31336820565
    assert "PRODUCTION_READY" in lock["forbidden_tokens_not_claimed"]
    assert "EVT_VALIDATED" in lock["forbidden_tokens_not_claimed"]
    follow = lock.get("device_os_tree_sync_followup") or {}
    assert follow.get("pr") == 69
    assert follow.get("status") == "DRAFT_TIP_NOT_ACCEPTED_MAIN"

    burndown = json.loads((CONT_IX / "BLOCKER_BURNDOWN.json").read_text(encoding="utf-8"))
    assert set(burndown["buckets"]) == {"DIGITAL", "PHYSICAL", "EXTERNAL"}
    assert burndown["counts"]["DIGITAL"] >= 4
    assert burndown["counts"]["DIGITAL_OPEN"] == 0
    assert burndown["digital_release_lock_complete"] is True
    assert burndown["recommendation"] == "READY_FOR_NPI_DFM_AND_EVT_QUOTATION"
    digital_ids = {b["id"] for b in burndown["blockers"] if b["bucket"] == "DIGITAL"}
    assert {"IX-D-001", "IX-D-002", "IX-D-003", "IX-D-004"} <= digital_ids
    external_ids = {b["id"] for b in burndown["blockers"] if b["bucket"] == "EXTERNAL"}
    assert {"IX-E-001", "IX-E-002", "IX-E-003", "IX-E-004", "IX-E-005"} <= external_ids
    physical_ids = {b["id"] for b in burndown["blockers"] if b["bucket"] == "PHYSICAL"}
    assert {"IX-P-001", "IX-P-002"} <= physical_ids
    for b in burndown["blockers"]:
        assert REQUIRED_BLOCKER_FIELDS <= set(b), b.get("id")

    matrix = json.loads((CONT_IX / "PRODUCT_RELEASE_MATRIX.json").read_text(encoding="utf-8"))
    assert matrix["digital_release_lock_complete"] is True
    assert matrix["ready_for_npi_dfm_and_evt_quotation"] is True
    assert "CONDITIONAL_VENDOR_COLLATERAL" in matrix["allowed_conditional_tokens_with_evidence"]
    assert "PRODUCTION_READY" in matrix["forbidden_tokens"]
    assert "EVT_VALIDATED" in matrix["forbidden_tokens"]
    assert "GATE_8_PASS" in matrix["forbidden_tokens"]
    assert matrix["products"]["student_device"]["manufacturer_ready"] is False

    drafts = yaml.safe_load(
        (CONT_IX / "continuation_ix_sibling_draft_registry.yaml").read_text(encoding="utf-8")
    )
    assert drafts["policy"] == "DRAFT_TIPS_NOT_ACCEPTED_MAIN_NOT_FINAL_UMBRELLA"
    assert drafts["digital_release_lock_complete"] is True
    assert drafts["final_umbrella"] is False
    assert drafts["drafts"]["device_os_ci_lock_evidence"]["pr"] == 69
    assert drafts["drafts"]["device_os_ci_lock_evidence"]["status"] == "DRAFT_TIP_NOT_ACCEPTED_MAIN"

    # Cont VIII schema backlog remains the prior digital-executable zero baseline
    viii_backlog = json.loads((CONT_VIII / "DIGITAL_BACKLOG.json").read_text(encoding="utf-8"))
    assert viii_backlog["DIGITALLY_EXECUTABLE_SCHEMA_ONLY"] == 0


def test_release_firewall_passes_cont_ix_tree():
    proc = subprocess.run(
        [sys.executable, str(FIREWALL)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "RELEASE_FIREWALL_PASS" in proc.stdout
    assert "active_continuation=IX" in proc.stdout


def test_release_firewall_rejects_digital_lock_complete_while_blockers(tmp_path: Path):
    lock_path = CONT_IX / "ACCEPTED_MAIN_LOCK.json"
    burndown_path = CONT_IX / "BLOCKER_BURNDOWN.json"
    lock_original = lock_path.read_text(encoding="utf-8")
    burndown_original = burndown_path.read_text(encoding="utf-8")
    try:
        doc = json.loads(lock_original)
        doc["digital_release_lock_complete"] = True
        lock_path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
        burn = json.loads(burndown_original)
        burn.setdefault("counts", {})["DIGITAL_OPEN"] = 1
        burndown_path.write_text(json.dumps(burn, indent=2) + "\n", encoding="utf-8")
        proc = subprocess.run(
            [sys.executable, str(FIREWALL)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        assert proc.returncode != 0
        assert "RELEASE_FIREWALL_FAIL" in proc.stdout
        assert "digital_release_lock_complete" in proc.stdout
    finally:
        lock_path.write_text(lock_original, encoding="utf-8")
        burndown_path.write_text(burndown_original, encoding="utf-8")


def test_release_firewall_rejects_production_ready_token(tmp_path: Path):
    matrix_path = CONT_IX / "PRODUCT_RELEASE_MATRIX.json"
    original = matrix_path.read_text(encoding="utf-8")
    try:
        doc = json.loads(original)
        # Assertive claim without negation context
        doc["notes"] = "PRODUCTION_READY=true for all devices"
        matrix_path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
        proc = subprocess.run(
            [sys.executable, str(FIREWALL)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        assert proc.returncode != 0
        assert "RELEASE_FIREWALL_FAIL" in proc.stdout
        assert "PRODUCTION_READY" in proc.stdout
    finally:
        matrix_path.write_text(original, encoding="utf-8")


def test_conditional_vendor_collateral_allowed_with_evidence():
    vendor = json.loads(
        (CONT_IX / "VENDOR_COLLATERAL_REQUESTS.json").read_text(encoding="utf-8")
    )
    assert vendor["purchase_authorized"] is False
    assert len(vendor["requests"]) >= 5
    assert all(
        r.get("allows_token_when_received") == "CONDITIONAL_VENDOR_COLLATERAL"
        for r in vendor["requests"]
    )
    matrix = json.loads((CONT_IX / "PRODUCT_RELEASE_MATRIX.json").read_text(encoding="utf-8"))
    student = matrix["products"]["student_device"]
    assert student["manufacturer_ready"] is False
    assert student["manufacturer_ready_token"] == "CONDITIONAL_VENDOR_COLLATERAL"
