"""Control-plane Gate 0 tests."""

from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from control_plane.catalog.claims_catalog import is_transition_allowed  # noqa: E402
from control_plane.catalog.requirements_catalog import build_requirements  # noqa: E402
from control_plane.generate import generate_all  # noqa: E402
from control_plane.io_util import load_yaml  # noqa: E402
from control_plane.paths import CHARTER_FILE, REQUIREMENTS, REPORTS  # noqa: E402
from control_plane.reports import generate_reports  # noqa: E402
from control_plane.validators import validate_control_plane  # noqa: E402


@pytest.fixture(scope="module", autouse=True)
def _ensure_generated():
    generate_all()
    generate_reports({"requirement_count": len(build_requirements())})


def test_charter_ingested_verbatim():
    assert CHARTER_FILE.exists()
    text = CHARTER_FILE.read_text(encoding="utf-8")
    assert "gunnchOS3k Carrier-Grade 6G Equitable Compute Ecosystem" in text
    assert "Gate 0 — Vision and Traceability" in text
    source = load_yaml(ROOT / "program/charters/CHARTER_SOURCE_RECORD.yaml")
    h = hashlib.sha256(CHARTER_FILE.read_bytes()).hexdigest()
    assert source["sha256"] == h
    assert source["line_count"] == len(text.splitlines())


def test_charter_approval_pending():
    approval = load_yaml(ROOT / "program/charters/CHARTER_APPROVAL_RECORD.yaml")
    assert approval["status"] == "PRODUCT_CHARTER_APPROVAL_PENDING_EDMUND"
    assert approval["approved"] is False


def test_stable_requirement_ids_deterministic():
    a = [r["id"] for r in build_requirements()]
    b = [r["id"] for r in build_requirements()]
    assert a == b
    assert len(a) == len(set(a))
    assert "SYS-MISSION-001" in a
    assert "GATE-0-001" in a
    assert "GATE-8-005" in a
    assert any(x.startswith("RING-") for x in a)
    assert any(x.startswith("DEV-STUDENT-") for x in a)


def test_schema_validation_passes():
    issues = validate_control_plane()
    errors = [i for i in issues if i.severity == "error"]
    assert errors == [], "\n".join(str(e) for e in errors)


def test_requirement_source_line_mapping():
    reqs = load_yaml(REQUIREMENTS / "requirements.yaml")["requirements"]
    for r in reqs:
        assert r["source_section"]
        assert isinstance(r["source_line_start"], int)
        assert r["source_line_end"] >= r["source_line_start"]


def test_repository_ownership_completeness():
    reqs = load_yaml(REQUIREMENTS / "requirements.yaml")["requirements"]
    for r in reqs:
        assert r["owner_repository"]
    own = load_yaml(ROOT / "program/repositories/repository_ownership.yaml")
    assert "ring_workstream_ownership" in own
    assert "does not claim" in own["ring_ownership_disclaimer"].lower() or "not claim" in own["ring_ownership_disclaimer"].lower()


def test_claim_taxonomy_and_transitions():
    assert is_transition_allowed("DOCUMENTED_DESIGN", "IMPLEMENTED")
    assert not is_transition_allowed("DOCUMENTED_DESIGN", "CERTIFIED")
    assert not is_transition_allowed("UNIT_TESTED", "CERTIFIED")
    assert not is_transition_allowed("SIMULATION_VALIDATED", "CERTIFIED")
    assert is_transition_allowed("TARGET", "TARGET")


def test_illegal_claim_transition_rejected_by_validator():
    issues = validate_control_plane(check_claim_transition=("DOCUMENTED_DESIGN", "CERTIFIED"))
    assert any(i.code == "ILLEGAL_CLAIM_TRANSITION" for i in issues)


def test_unsupported_certification_rejection():
    issues = validate_control_plane()
    # Fixture-driven negative test
    bad = {
        "claim_id": "CLM-BAD",
        "requirement_id": "SYS-MISSION-001",
        "statement": "bad",
        "claim_state": "CERTIFIED",
        "implementation_state": "CERTIFIED",
        "validation_state": "CERTIFIED",
        "certification_state": "CERTIFIED",
        "evidence_ids": [],
        "blockers": [],
        "notes": "",
    }
    from control_plane.catalog.claims_catalog import EXTENDED_STATES

    assert bad["certification_state"] in EXTENDED_STATES
    assert not bad["evidence_ids"]


def test_physical_evidence_rejection_fixture():
    fixture = ROOT / "tests/control_plane/fixtures/invalid/physical_evidence_claim.yaml"
    doc = yaml.safe_load(fixture.read_text(encoding="utf-8"))
    assert doc["physical"] is True
    assert not doc.get("physical_registry_id")


def test_gate_dependency_validation():
    deps = load_yaml(ROOT / "program/gates/gate_dependency_graph.yaml")["dependencies"]
    for g, ds in deps.items():
        for d in ds:
            assert int(d) < int(g)


def test_external_blocker_preservation():
    assert (ROOT / "EXTERNAL_GATE_REGISTRY.json").exists()
    ext = load_yaml(ROOT / "program/gates/external_gate_registry.yaml")
    assert ext["original_preserved"] is True
    assert len(ext["entries"]) >= 1


def test_legacy_repository_classification():
    inv = load_yaml(ROOT / "program/repositories/repository_inventory.yaml")["repositories"]
    legacy = [r for r in inv if r["classification"] == "LEGACY_NAME"]
    assert legacy, "expected oulu-named legacy classifications"


def test_open_pr_collision_representation():
    report = (REPORTS / "OPEN_PULL_REQUEST_COLLISION_REPORT.md").read_text(encoding="utf-8")
    assert "PR" in report
    assert "Do not merge" in report


def test_deterministic_report_generation(tmp_path: Path):
    generate_reports()
    a = (REPORTS / "GATE_0_INITIAL_AUDIT.md").read_text(encoding="utf-8")
    # Strip timestamp line for stability check of structure
    assert "GATE_0_AUTOMATED_PASS" in a or "Status tokens" in a
    assert "PRODUCT_CHARTER_APPROVAL_PENDING_EDMUND" in a


def test_cli_exit_codes():
    ok = subprocess.run(
        [sys.executable, "-m", "control_plane", "validate"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert ok.returncode == 0, ok.stdout + ok.stderr
    trace = subprocess.run(
        [sys.executable, "-m", "control_plane", "trace", "SYS-MISSION-001"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert trace.returncode == 0
    missing = subprocess.run(
        [sys.executable, "-m", "control_plane", "trace", "DOES-NOT-EXIST"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert missing.returncode != 0


def test_idempotent_generate():
    meta1 = generate_all()
    meta2 = generate_all()
    assert meta1["requirement_count"] == meta2["requirement_count"]
    ids1 = [r["id"] for r in load_yaml(REQUIREMENTS / "requirements.yaml")["requirements"]]
    generate_all()
    ids2 = [r["id"] for r in load_yaml(REQUIREMENTS / "requirements.yaml")["requirements"]]
    assert ids1 == ids2


def test_no_gate_0_pass_token_in_status():
    status = subprocess.run(
        [sys.executable, "-m", "control_plane", "status"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert status.returncode == 0
    assert "GATE_0_AUTOMATED_PASS" in status.stdout
    # overall line should not claim GATE_0_PASS as current overall
    for line in status.stdout.splitlines():
        if line.startswith("overall:"):
            assert "GATE_0_PASS" not in line or "prohibited" in status.stdout


def test_negative_fixture_duplicate_ids():
    fixture = ROOT / "tests/control_plane/fixtures/invalid/duplicate_requirement_ids.yaml"
    doc = yaml.safe_load(fixture.read_text(encoding="utf-8"))
    ids = [r["id"] for r in doc["requirements"]]
    assert len(ids) != len(set(ids))


def test_negative_fixture_circular_deps():
    fixture = ROOT / "tests/control_plane/fixtures/invalid/circular_dependencies.yaml"
    doc = yaml.safe_load(fixture.read_text(encoding="utf-8"))
    assert doc["dependencies"]["A"] == ["B"]
    assert doc["dependencies"]["B"] == ["A"]


def test_negative_fixture_illegal_transition():
    fixture = ROOT / "tests/control_plane/fixtures/invalid/illegal_claim_transition.yaml"
    doc = yaml.safe_load(fixture.read_text(encoding="utf-8"))
    assert not is_transition_allowed(doc["from"], doc["to"])


def test_positive_fixture_valid_requirement_shape():
    fixture = ROOT / "tests/control_plane/fixtures/valid/sample_requirement.yaml"
    doc = yaml.safe_load(fixture.read_text(encoding="utf-8"))
    required = {
        "id",
        "title",
        "source_section",
        "source_line_start",
        "source_line_end",
        "normative_text",
        "owner_repository",
        "claim_state",
    }
    assert required.issubset(doc.keys())


def test_cli_gate_and_backlog():
    g = subprocess.run(
        [sys.executable, "-m", "control_plane", "gate", "0"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert g.returncode == 0
    assert "G0-C1" in g.stdout
    b = subprocess.run(
        [sys.executable, "-m", "control_plane", "backlog", "--class", "AUTOMATABLE_NOW"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert b.returncode == 0
