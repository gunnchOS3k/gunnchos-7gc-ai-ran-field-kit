#!/usr/bin/env python3
"""Integrity tests for master status, preregistration, assignments, and claim boundaries."""
from __future__ import annotations

import csv
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
PY = sys.executable


def run(argv: list[str], cwd: Path = ROOT) -> subprocess.CompletedProcess:
    return subprocess.run(argv, cwd=str(cwd), capture_output=True, text=True)


def test_master_status_validator_passes_current():
    proc = run([PY, "scripts/validate_master_status.py"])
    assert proc.returncode == 0, proc.stdout + proc.stderr


def test_gate_pass_without_evidence_fails():
    status = json.loads((ROOT / "research-application-control" / "MASTER_STATUS.json").read_text())
    status["gates"]["GATE_1_PASS"]["status"] = "PASS"
    status["gates"]["GATE_1_PASS"]["evidence"] = ["does/not/exist.md"]
    status["gates"]["GATE_1_PASS"]["unmet"] = []
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "MASTER_STATUS.json"
        p.write_text(json.dumps(status))
        # copy schema path expectation: validator uses fixed schema under repo; only status overridden
        proc = run([PY, "scripts/validate_master_status.py", "--status", str(p), "--repo-root", str(ROOT)])
        assert proc.returncode != 0
        assert "evidence missing" in proc.stdout or "evidence missing" in proc.stderr


def test_gate3_pass_with_zero_sessions_fails():
    status = json.loads((ROOT / "research-application-control" / "MASTER_STATUS.json").read_text())
    status["gates"]["GATE_3_PASS"]["status"] = "PASS"
    status["gates"]["GATE_3_PASS"]["eligible_sessions"] = 0
    status["gates"]["GATE_3_PASS"]["required_sessions"] = 54
    status["gates"]["GATE_3_PASS"]["evidence"] = ["datasets/controlled/GATE3_FINAL_REPORT.md"]
    status["gates"]["GATE_3_PASS"]["unmet"] = []
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "MASTER_STATUS.json"
        p.write_text(json.dumps(status))
        proc = run([PY, "scripts/validate_master_status.py", "--status", str(p), "--repo-root", str(ROOT)])
        assert proc.returncode != 0


def test_preregistration_lock_ok():
    proc = run([PY, "scripts/validate_preregistration.py"])
    assert proc.returncode == 0, proc.stdout + proc.stderr


def test_preregistration_tamper_fails():
    lock_path = ROOT / "evaluation" / "PRIMARY_OUTCOME_LOCK.json"
    original = lock_path.read_text()
    try:
        data = json.loads(original)
        data["primary_outcome"] = "tampered_metric"
        lock_path.write_text(json.dumps(data, indent=2) + "\n")
        proc = run([PY, "scripts/validate_preregistration.py"])
        assert proc.returncode != 0
    finally:
        lock_path.write_text(original)


def test_assignment_matrix_coverage():
    proc = run([PY, "scripts/validate_pilot_assignments.py"])
    assert proc.returncode == 0, proc.stdout + proc.stderr
    payload = json.loads(proc.stdout)
    assert payload["n"] == 54
    assert payload["design_approved"] is False  # pending dates


def test_duplicate_assignment_detected(tmp_path: Path):
    src = ROOT / "pilot" / "54_CELL_ASSIGNMENT_MATRIX.csv"
    rows = list(csv.DictReader(src.open()))
    rows.append(rows[0])
    out = tmp_path / "dup.csv"
    with out.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)
    proc = run([PY, "scripts/validate_pilot_assignments.py", "--matrix", str(out)])
    assert proc.returncode != 0


def test_missing_cell_detected(tmp_path: Path):
    src = ROOT / "pilot" / "54_CELL_ASSIGNMENT_MATRIX.csv"
    rows = list(csv.DictReader(src.open()))[:-1]
    out = tmp_path / "missing.csv"
    with out.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)
    proc = run([PY, "scripts/validate_pilot_assignments.py", "--matrix", str(out)])
    assert proc.returncode != 0


def test_application_packet_present():
    proc = run([PY, "scripts/validate_application_packet.py"])
    assert proc.returncode == 0, proc.stdout + proc.stderr


def test_repo_lock_rejects_stale(tmp_path: Path):
    lock = json.loads((ROOT / "integration" / "repo-lock.json").read_text())
    # Pick a required component and corrupt expected commit
    comps = lock.get("components") or {}
    assert comps
    name = next(iter(comps))
    comps[name]["commit"] = "0" * 40
    comps[name]["required"] = True
    lock_path = tmp_path / "repo-lock.json"
    lock_path.write_text(json.dumps(lock))
    proc = run(
        [
            PY,
            "scripts/verify_repo_lock.py",
            "--lock",
            str(lock_path),
            "--repos-root",
            str(ROOT.parent),
        ]
    )
    assert proc.returncode != 0


def test_raw_private_gitignored():
    gi = (ROOT / ".gitignore").read_text()
    assert "raw-private" in gi or "datasets/controlled/raw" in gi


def test_portfolio_landing_exists():
    assert (ROOT / "portfolio" / "LANDING_PAGE.md").is_file()


def test_no_active_doi_claimed():
    text = (ROOT / "release" / "CITATION.cff").read_text()
    assert "DOI_PENDING" in text or "doi:" not in text.lower() or "pending" in text.lower()
