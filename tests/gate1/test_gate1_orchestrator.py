"""Gate 1 orchestrator tests — schemas, status, evidence, tamper, idempotency, upgrades."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from gate1 import STATUS_AUTOMATED_PASS, STATUS_GATE_1_PASS, STATUS_PHYSICAL_PENDING  # noqa: E402
from gate1.orchestrator import ACCEPTED, CONTRACTS, PENDING, REJECTED  # noqa: E402
from gate1.orchestrator.evidence_collector import (  # noqa: E402
    classify_evidence,
    content_digest,
    ingest_path,
    verify_artifact_hash,
    write_pending,
)
from gate1.orchestrator.evidence_validator import (  # noqa: E402
    refuse_unsupported_upgrade,
    validate_against_schema,
    validate_all_contracts,
)
from gate1.orchestrator.result_aggregator import compute_status  # noqa: E402

FIXTURES = Path(__file__).parent / "fixtures"


def _clean_buckets():
    for bucket in (PENDING, ACCEPTED, REJECTED):
        bucket.mkdir(parents=True, exist_ok=True)
        for p in bucket.glob("*.json"):
            p.unlink()


@pytest.fixture(autouse=True)
def _isolate_evidence(tmp_path, monkeypatch):
    # Keep real contracts; isolate evidence dirs via monkeypatch of module paths
    pend = tmp_path / "pending"
    acc = tmp_path / "accepted"
    rej = tmp_path / "rejected"
    for d in (pend, acc, rej):
        d.mkdir()
    import gate1.orchestrator as orch
    import gate1.orchestrator.evidence_collector as ec
    import gate1.orchestrator.evidence_validator as ev
    import gate1.orchestrator.result_aggregator as ra

    monkeypatch.setattr(orch, "PENDING", pend)
    monkeypatch.setattr(orch, "ACCEPTED", acc)
    monkeypatch.setattr(orch, "REJECTED", rej)
    monkeypatch.setattr(ec, "PENDING", pend)
    monkeypatch.setattr(ec, "ACCEPTED", acc)
    monkeypatch.setattr(ev, "ACCEPTED", acc)
    monkeypatch.setattr(ev, "REJECTED", rej)
    monkeypatch.setattr(ra, "PENDING", pend)
    monkeypatch.setattr(ra, "ACCEPTED", acc)
    yield {"pending": pend, "accepted": acc, "rejected": rej}


def test_all_contract_schemas_valid():
    issues = validate_all_contracts()
    assert issues == [], "\n".join(str(i) for i in issues)
    for name in [
        "device_identity.schema.json",
        "authenticated_input.schema.json",
        "dock_session.schema.json",
        "local_ai_runtime.schema.json",
        "game_core_loop.schema.json",
        "evidence_event.schema.json",
    ]:
        assert (CONTRACTS / name).exists()


def test_valid_fixtures_pass_schema():
    mapping = {
        "device_identity.valid.json": "device_identity.schema.json",
        "authenticated_input.valid.json": "authenticated_input.schema.json",
        "evidence_event.valid.json": "evidence_event.schema.json",
    }
    for fname, schema in mapping.items():
        doc = json.loads((FIXTURES / "valid" / fname).read_text(encoding="utf-8"))
        assert validate_against_schema(doc, schema) == []


def test_invalid_fixtures_fail_schema():
    doc = json.loads((FIXTURES / "invalid" / "device_identity.missing_fields.json").read_text(encoding="utf-8"))
    issues = validate_against_schema(doc, "device_identity.schema.json")
    assert issues


def test_status_software_pass_physical_pending():
    status = compute_status({"ok": True, "software_failures": [], "contract_issues": []})
    assert status["overall"] == STATUS_AUTOMATED_PASS
    assert status["secondary"] == STATUS_PHYSICAL_PENDING
    assert status["physical_complete"] is False
    assert status["overall"] != STATUS_GATE_1_PASS


def test_status_software_fail_nonzero_semantics():
    status = compute_status({"ok": False, "software_failures": ["boot"], "contract_issues": []})
    assert status["software_ok"] is False
    assert "FAIL" in status["overall"]


def test_evidence_classification_separation():
    assert classify_evidence({"evidence_class": "software", "claim_level": "SOFTWARE_SLICE"}) == "software"
    assert classify_evidence({"evidence_class": "simulated", "claim_level": "SIMULATED"}) == "simulated"
    assert classify_evidence({"evidence_class": "physical", "claim_level": "PHYSICAL_BOOT"}) == "physical"


def test_refuse_unsupported_claim_upgrade():
    bad = {
        "evidence_class": "software",
        "claim_level": "PHYSICAL_BOOT",
    }
    with pytest.raises(ValueError, match="refuse claim upgrade"):
        classify_evidence(bad)
    issues = refuse_unsupported_upgrade(bad)
    assert any(i.code == "CLAIM_UPGRADE_REFUSED" for i in issues)


def test_negative_fixture_physical_upgrade_from_software():
    doc = json.loads((FIXTURES / "invalid" / "physical_claim_software_class.json").read_text(encoding="utf-8"))
    issues = refuse_unsupported_upgrade(doc)
    assert issues


def test_tamper_hash_detection(tmp_path):
    path = write_pending(
        "hash_probe.json",
        {
            "schema_version": "1.0.0",
            "evidence_id": "hash-probe",
            "workstream": "boot",
            "evidence_class": "software",
            "claim_level": "SOFTWARE_SLICE",
            "tool_versions": {"gate1_orchestrator": "0.1.0"},
            "collected_at_utc": "2026-08-06T00:00:00Z",
            "notes": "ok",
        },
    )
    assert verify_artifact_hash(path)
    doc = json.loads(path.read_text(encoding="utf-8"))
    doc["notes"] = "tampered"
    path.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    assert not verify_artifact_hash(path)


def test_ingest_idempotency(tmp_path):
    src = tmp_path / "src.json"
    payload = {
        "schema_version": "1.0.0",
        "evidence_id": "idem-1",
        "workstream": "dock",
        "evidence_class": "software",
        "claim_level": "SOFTWARE_SLICE",
        "artifact_sha256": "0" * 64,
        "tool_versions": {"t": "1"},
        "collected_at_utc": "2026-08-06T00:00:00Z",
    }
    # Fix digest to match content_digest rules after write_pending enrichment path via ingest
    src.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    a, mode_a = ingest_path(src)
    b, mode_b = ingest_path(src)
    assert mode_a == "ingested"
    assert mode_b == "idempotent_hit"
    assert a == b


def test_gate1_pass_refused_without_physical():
    status = compute_status({"ok": True, "software_failures": [], "contract_issues": []})
    assert status["overall"] != STATUS_GATE_1_PASS
    assert status["prohibited_without_physical"] == STATUS_GATE_1_PASS


def test_cli_status_and_run_exit_codes():
    st = subprocess.run(
        [sys.executable, "-m", "gate1.orchestrator.cli", "status"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert st.returncode == 0, st.stdout + st.stderr
    assert "overall:" in st.stdout
    assert STATUS_GATE_1_PASS in st.stdout  # mentioned as prohibited
    run = subprocess.run(
        [sys.executable, "-m", "gate1.orchestrator.cli", "run"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    # software may pass or fail depending on sibling repos; never claim GATE_1_PASS
    assert STATUS_GATE_1_PASS not in run.stdout.splitlines()[-1] if run.stdout else True
    assert "GATE_1_PASS" not in [tok for tok in run.stdout.split() if tok == "GATE_1_PASS"] or "physical" in run.stdout.lower()
    # Explicit: last status line tokens should not be sole GATE_1_PASS
    assert "GATE_1_AUTOMATED_PASS" in run.stdout or "GATE_1_SOFTWARE_FAIL" in run.stdout


def test_manifests_present():
    for name in [
        "gate1_components.yaml",
        "gate1_required_services.yaml",
        "gate1_test_matrix.yaml",
        "gate1_physical_evidence_requirements.yaml",
    ]:
        path = ROOT / "gate1" / "manifests" / name
        assert path.exists()
        yaml.safe_load(path.read_text(encoding="utf-8"))


def test_physical_action_packet_has_exact_steps():
    # Ensure packet generated after a run
    subprocess.run(
        [sys.executable, "-m", "gate1.orchestrator.cli", "run"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    packet = (ROOT / "gate1" / "reports" / "GATE_1_PHYSICAL_ACTION_PACKET.md").read_text(encoding="utf-8")
    for needle in [
        "Equipment inventory command",
        "### A. Boot",
        "### B. Ring authenticated input",
        "### C. Dock continuity",
        "### D. Local AI runtime",
        "### E. Game core loops",
        "beatlink-party",
        "archive-of-life-artifact-world",
        "pedestrian-pursuit",
        "anime-aggressors",
        "MISSING",
        "python -m gate1.orchestrator.cli status --equipment-inventory",
    ]:
        assert needle in packet
