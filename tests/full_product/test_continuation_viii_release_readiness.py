"""Cont VIII release-readiness firewall + evidence pack tests."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
CONT_VIII = ROOT / "program" / "full_product" / "continuation_viii"
FIREWALL = ROOT / "scripts" / "validate_release_firewall.py"
PROVE = ROOT / "scripts" / "prove_full_product_continuation_viii.py"


def test_cont_viii_prove_script_exists():
    assert PROVE.exists()
    text = PROVE.read_text(encoding="utf-8")
    assert "CONTINUATION_VIII_RELEASE_READINESS_CLOSURE" in text
    assert "78cd33f1fde0a0c42eb6469bbdbe4664225d3dd0" in text
    assert "CG-QUALITY-001" in text
    assert "RING-RELIAB-016" in text


def test_cont_viii_readiness_schemas_exist():
    assert (CONT_VIII / "readiness_gates.schema.json").exists()
    assert (CONT_VIII / "readiness_scorecard.schema.json").exists()
    assert (CONT_VIII / "READINESS_GATES.md").exists()
    gates_schema = json.loads((CONT_VIII / "readiness_gates.schema.json").read_text(encoding="utf-8"))
    assert set(gates_schema["properties"]["gates"]["required"]) == {
        "R1",
        "R2",
        "R3",
        "R4",
        "R5",
        "R6",
    }
    score_schema = json.loads(
        (CONT_VIII / "readiness_scorecard.schema.json").read_text(encoding="utf-8")
    )
    required = score_schema["properties"]["scorecard"]["required"]
    for key in (
        "product",
        "manufacturer_ready",
        "assembly_ready",
        "adopter_ready",
        "reproducible_ready",
        "recreation_ready",
        "student_ready",
        "office_work_ready",
        "physical_validation_pending",
        "external_validation_pending",
    ):
        assert key in required


def test_cont_viii_artifacts_exist_and_honest():
    for name in (
        "ACCEPTED_MAIN_BASELINE.json",
        "REQUIREMENT_PROOF.json",
        "REQUIREMENT_COUNTS.json",
        "REQUIREMENT_PROMOTION_LEDGER.json",
        "DIGITAL_BACKLOG.json",
        "PHYSICAL_IRREDUCIBILITY_AUDIT.json",
        "EXTERNAL_IRREDUCIBILITY_AUDIT.json",
        "READINESS_SCORECARD.json",
        "READINESS_GATES.json",
        "REMAINING_BLOCKERS.yaml",
        "continuation_viii_sibling_draft_registry.yaml",
    ):
        assert (CONT_VIII / name).exists(), name

    counts = json.loads((CONT_VIII / "REQUIREMENT_COUNTS.json").read_text(encoding="utf-8"))
    assert counts["total"] == 476
    assert counts["continuation"] == "VIII"
    assert counts["status_counts"].get("SCHEMA_ONLY", -1) != 221
    # Cont VIII target: SCHEMA_ONLY closed after device-os #65+#66
    assert counts["status_counts"].get("SCHEMA_ONLY", 0) == 0

    backlog = json.loads((CONT_VIII / "DIGITAL_BACKLOG.json").read_text(encoding="utf-8"))
    assert backlog["DIGITALLY_EXECUTABLE_SCHEMA_ONLY"] == 0
    assert backlog["ids"]["DIGITALLY_EXECUTABLE_SCHEMA_ONLY"] == []

    baseline = json.loads((CONT_VIII / "ACCEPTED_MAIN_BASELINE.json").read_text(encoding="utf-8"))
    assert baseline["continuation"] == "VIII"
    assert baseline["final_umbrella"] is False
    assert baseline["accepted_mains"]["gunnchos-device-os"].startswith("78cd33f1")
    assert baseline["accepted_mains"]["gunnchos-7gc-ai-ran-field-kit"].startswith("a4846ca9")

    scorecard = json.loads((CONT_VIII / "READINESS_SCORECARD.json").read_text(encoding="utf-8"))
    assert scorecard["digital_pre_evt_release_ready"] is False
    sc = scorecard["scorecard"]
    for flag in (
        "manufacturer_ready",
        "assembly_ready",
        "adopter_ready",
        "recreation_ready",
        "student_ready",
        "office_work_ready",
    ):
        assert sc[flag] is False, flag
    assert sc["physical_validation_pending"] is True
    assert sc["external_validation_pending"] is True

    blockers = yaml.safe_load((CONT_VIII / "REMAINING_BLOCKERS.yaml").read_text(encoding="utf-8"))
    assert set(blockers["buckets"]) == {"DIGITAL", "PHYSICAL", "EXTERNAL"}
    assert blockers["buckets"]["DIGITAL"]["count"] == 0


def test_release_firewall_passes_cont_viii_tree():
    proc = subprocess.run(
        [sys.executable, str(FIREWALL)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "RELEASE_FIREWALL_PASS" in proc.stdout


def test_release_firewall_rejects_manufacturer_ready_without_artifacts(tmp_path: Path):
    # Snapshot scorecard, corrupt manufacturer_ready=true, expect fail
    score_path = CONT_VIII / "READINESS_SCORECARD.json"
    original = score_path.read_text(encoding="utf-8")
    try:
        doc = json.loads(original)
        doc["scorecard"]["manufacturer_ready"] = True
        doc["subcriteria"]["manufacturer_ready"]["satisfied"] = False
        doc["subcriteria"]["manufacturer_ready"]["missing"] = [
            "FORBIDDEN_UNTIL_FAB_PACKAGE_COMPLETE"
        ]
        score_path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
        proc = subprocess.run(
            [sys.executable, str(FIREWALL)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        assert proc.returncode != 0
        assert "RELEASE_FIREWALL_FAIL" in proc.stdout
        assert "manufacturer_ready" in proc.stdout
    finally:
        score_path.write_text(original, encoding="utf-8")


def test_promoted_quality_ids_are_digitally_validated():
    proof = json.loads((CONT_VIII / "REQUIREMENT_PROOF.json").read_text(encoding="utf-8"))
    by_id = {n["id"]: n for n in proof["nodes"]}
    for rid in ("CG-QUALITY-001", "CG-QUALITY-007", "CG-QUALITY-008", "RING-RELIAB-016"):
        assert by_id[rid]["current_status"] == "DIGITALLY_VALIDATED", rid
        assert by_id[rid]["accepted_main_sha"].startswith("78cd33f1")
