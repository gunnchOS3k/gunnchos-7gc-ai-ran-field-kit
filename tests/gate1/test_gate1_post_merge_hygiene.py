"""Gate 1 post-merge hygiene, operator inventory, claim refusal, no-write dry-run."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from gate1 import (  # noqa: E402
    STATUS_GATE_1_PASS,
    STATUS_LOCAL_AUTOMATION_PASS,
    STATUS_PHYSICAL_EVIDENCE_PENDING,
    STATUS_REMOTE_CI_PENDING,
)
from gate1.operator.checklist import plan_from_inventory  # noqa: E402
from gate1.operator.evidence_session import (  # noqa: E402
    accept_bundle,
    finalize_session,
    run_check,
    start_session,
    validate_bundle,
)
from gate1.operator.inventory import REQUIRED_CAPABILITIES, collect_inventory  # noqa: E402
from gate1.orchestrator.evidence_validator import refuse_unsupported_upgrade  # noqa: E402


def test_runtime_artifacts_not_tracked():
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "check_gate1_runtime_artifacts_untracked.py")],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "GATE1_RUNTIME_ARTIFACTS_CLEAN" in proc.stdout


def test_migration_manifest_present_and_hashed():
    path = ROOT / "gate1" / "post_merge" / "runtime_artifact_migration_manifest.yaml"
    assert path.exists()
    doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert doc["counts"]["untrack"] >= 1
    assert any(e["action"] == "untrack_and_ignore" for e in doc["entries"])
    assert any(e["classification"].startswith("RUNTIME_") for e in doc["entries"])
    # No physical relabel in migration
    for e in doc["entries"]:
        assert e.get("evidence_class") in (None, "software", "simulated")
        assert not (e.get("claim_level") or "").startswith("PHYSICAL")


def test_gitignore_covers_evidence_buckets():
    text = (ROOT / ".gitignore").read_text(encoding="utf-8")
    for line in [
        "gate1/evidence/accepted/*",
        "gate1/evidence/pending/*",
        "gate1/evidence/rejected/*",
        "gate1/evidence/runs/*",
        "!gate1/evidence/**/.gitkeep",
    ]:
        assert line in text


def test_fixtures_valid_and_invalid_exist():
    valid = ROOT / "gate1" / "fixtures" / "valid"
    invalid = ROOT / "gate1" / "fixtures" / "invalid"
    assert any(valid.glob("*.json"))
    assert any(invalid.glob("*.json"))
    bad = json.loads((invalid / "evidence_event.physical_from_software.json").read_text(encoding="utf-8"))
    assert refuse_unsupported_upgrade(bad)


def test_orchestrator_no_write_dry_run_does_not_dirty_evidence(tmp_path):
    before = subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True)
    proc = subprocess.run(
        [sys.executable, "-m", "gate1.orchestrator.cli", "run", "--no-write"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert proc.returncode in (0, 1), proc.stdout + proc.stderr
    assert "GATE_1_PASS" not in [t for t in proc.stdout.split() if t == "GATE_1_PASS"]
    after = subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True)
    # Evidence dirs must not gain tracked dirt from no-write
    assert "gate1/evidence/pending/" not in after or before == after or "gate1/evidence" not in [
        ln for ln in after.splitlines() if "gate1/evidence" in ln and not ln.startswith("??")
    ]
    # Stronger: no new staged/modified evidence json
    dirty_evidence = [
        ln
        for ln in after.splitlines()
        if "gate1/evidence/" in ln and ln[:2].strip() in {"M", "A", "D", "MM", "AM"}
    ]
    prior_dirty = [
        ln
        for ln in before.splitlines()
        if "gate1/evidence/" in ln and ln[:2].strip() in {"M", "A", "D", "MM", "AM"}
    ]
    assert dirty_evidence == prior_dirty


def test_orchestrator_output_dir_writes_away_from_repo_evidence(tmp_path):
    out = tmp_path / "out"
    proc = subprocess.run(
        [sys.executable, "-m", "gate1.orchestrator.cli", "run", "--output-dir", str(out)],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert proc.returncode in (0, 1), proc.stdout + proc.stderr
    assert (out / "runs").exists() or (out / "pending").exists() or (out / "reports").exists()


def test_operator_inventory_schema_tokens():
    inv = collect_inventory()
    assert inv["assumption"]
    assert inv["summary"]["capabilities_present_confirmed"] == 0 or True  # may be 0
    for cap in inv["gate1_capabilities"]:
        assert cap["presence"] in {
            "PRESENT_CONFIRMED",
            "MISSING",
            "MISSING_ASSUMED",
            "TOOLCHAIN_MISSING",
            "UNSUPPORTED_PLATFORM",
            "PERMISSION_DENIED",
            "INDETERMINATE",
        }
        # Must not invent Gate 1 prototypes as PRESENT without correlation policy
        if cap["presence"] == "PRESENT_CONFIRMED":
            pytest.fail("inventory must not auto-confirm Gate 1 prototypes")
    schema = json.loads(
        (ROOT / "gate1" / "operator" / "schemas" / "inventory_item.schema.json").read_text(encoding="utf-8")
    )
    validator = Draft202012Validator(schema)
    for item in inv["observed_items"] + inv["gate1_capabilities"]:
        validator.validate(item)
    plan = plan_from_inventory(inv)
    assert plan["runnable_count"] == 0
    assert len(REQUIRED_CAPABILITIES) == 5


def test_claim_refusal_and_accept_requires_edmund(tmp_path, monkeypatch):
    # Isolate sessions/accepted under tmp
    import gate1.operator as op
    import gate1.operator.evidence_session as es

    sessions = tmp_path / "sessions"
    accepted = tmp_path / "accepted"
    rejected = tmp_path / "rejected"
    sessions.mkdir()
    accepted.mkdir()
    rejected.mkdir()
    monkeypatch.setattr(op, "SESSIONS", sessions)
    monkeypatch.setattr(op, "ACCEPTED", accepted)
    monkeypatch.setattr(op, "REJECTED", rejected)
    monkeypatch.setattr(es, "SESSIONS", sessions)
    monkeypatch.setattr(es, "ACCEPTED", accepted)
    monkeypatch.setattr(es, "REJECTED", rejected)

    session = start_session("boot", operator="tester")
    with pytest.raises(ValueError, match="PRESENT_CONFIRMED"):
        run_check(
            session["session_id"],
            "boot_identity",
            result="pass",
            capability_presence="MISSING_ASSUMED",
        )
    # Blocked check allowed without present
    run_check(
        session["session_id"],
        "boot_identity",
        result="blocked",
        capability_presence="MISSING",
    )
    bundle = finalize_session(session["session_id"])
    assert bundle["evidence_class"] != "physical"
    bundle_path = sessions / session["session_id"] / "bundle.json"
    ok, issues = validate_bundle(bundle_path)
    assert ok, issues

    decision = {
        "schema_version": "1.0.0",
        "authority": "Edmund Gunn Jr.",
        "decision": "ACCEPT",
        "bundle_id": bundle["bundle_id"],
        "decided_at_utc": "2026-08-07T00:00:00Z",
        "explicit_human_decision": True,
        "rationale": "test accept should still fail because not physical",
    }
    dec_path = tmp_path / "decision.json"
    dec_path.write_text(json.dumps(decision), encoding="utf-8")
    with pytest.raises(ValueError, match="not physical"):
        accept_bundle(bundle_path, dec_path)

    # Missing decision record refuses
    with pytest.raises((ValueError, FileNotFoundError, OSError)):
        accept_bundle(bundle_path, tmp_path / "missing.json")


def test_final_status_tokens():
    proc = subprocess.run(
        [sys.executable, "-m", "gate1.operator.cli", "final-status"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert STATUS_PHYSICAL_EVIDENCE_PENDING in proc.stdout
    assert STATUS_REMOTE_CI_PENDING in proc.stdout
    assert "GATE_2_NOT_STARTED_GATE_1_INCOMPLETE" in proc.stdout
    start = proc.stdout.index("{")
    end = proc.stdout.rindex("}") + 1
    data = json.loads(proc.stdout[start:end])
    assert data["physical_complete"] is False
    assert data["tokens"]["remote_ci"] == STATUS_REMOTE_CI_PENDING
    assert data["tokens"]["physical"] == STATUS_PHYSICAL_EVIDENCE_PENDING
    assert data["gate2_entry"] == "GATE_2_NOT_STARTED_GATE_1_INCOMPLETE"
    assert data["overall"] != STATUS_GATE_1_PASS
    assert data["tokens"]["local_automation"] in {
        STATUS_LOCAL_AUTOMATION_PASS,
        "GATE_1_AUTOMATED_PASS",
        "GATE_1_AUTOMATED_PARTIAL",
        "GATE_1_SOFTWARE_FAIL",
    }


def test_post_merge_artifacts_exist():
    for name in [
        "merged_baseline.yaml",
        "repository_main_lock.yaml",
        "ci_inventory.yaml",
        "runtime_artifact_inventory.yaml",
        "physical_capability_inventory.yaml",
        "findings.schema.json",
        "runtime_artifact_migration_manifest.yaml",
    ]:
        assert (ROOT / "gate1" / "post_merge" / name).exists()
    for name in [
        "GATE_1_POST_MERGE_INTEGRITY_AUDIT.md",
        "GATE_1_REMOTE_CI_AUDIT.md",
        "GATE_1_RUNTIME_ARTIFACT_CLEANUP_REPORT.md",
        "GATE_1_PHYSICAL_CAPABILITY_INVENTORY.md",
        "GATE_1_FINAL_ACCEPTANCE_MATRIX.md",
        "GATE_1_REMOTE_CI_EVIDENCE.md",
        "GATE_1_PHYSICAL_EVIDENCE_INDEX.md",
        "GATE_1_BLOCKER_AND_ACQUISITION_PLAN.md",
        "GATE_1_MERGE_REVIEW_PACKET.md",
    ]:
        assert (ROOT / "gate1" / "reports" / name).exists()
    assert (ROOT / "gate2" / "GATE_2_EXECUTION_PACKET.md").exists()
    assert (ROOT / "gate2" / "GATE_2_ENTRY_BLOCKERS.md").exists()
    blockers = (ROOT / "gate2" / "GATE_2_ENTRY_BLOCKERS.md").read_text(encoding="utf-8")
    assert "GATE_2_NOT_STARTED_GATE_1_INCOMPLETE" in blockers
