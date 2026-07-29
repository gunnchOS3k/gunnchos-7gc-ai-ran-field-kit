"""Gate 6 fail-closed harness tests."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import run_gate6_dry_run as g6  # noqa: E402


def test_missing_report_fails(tmp_path, monkeypatch):
    fake = tmp_path / "empty-repo"
    fake.mkdir()
    monkeypatch.setattr(g6, "REPOS_ROOT", tmp_path)
    (tmp_path / "gunnchos-gpu-nr-baseband-platform").mkdir()
    result = g6._validate_sibling_report(fake, "gunnchos-gpu-nr-baseband-platform")
    assert result["ok"] is False
    assert result["error"] == "missing_required_report"


def test_malformed_report_fails(tmp_path):
    repo = tmp_path / "r"
    (repo / "physical_evidence").mkdir(parents=True)
    bad = repo / "physical_evidence" / "GATE6_DRY_RUN_REPORT.json"
    bad.write_text("{not-json")
    result = g6._validate_sibling_report(repo, "x")
    assert result["ok"] is False
    assert "malformed_report" in result["error"]


def test_missing_mode_field_fails(tmp_path):
    repo = tmp_path / "r"
    (repo / "physical_evidence").mkdir(parents=True)
    path = repo / "physical_evidence" / "GATE6_DRY_RUN_REPORT.json"
    path.write_text(json.dumps({"ok": True, "evidence_label": "SYNTHETIC_EXPERIMENT"}))
    result = g6._validate_sibling_report(repo, "x")
    assert result["ok"] is False
    assert result["error"] == "missing_required_report_field"


def test_wrong_physical_label_fails(tmp_path):
    repo = tmp_path / "r"
    (repo / "physical_evidence").mkdir(parents=True)
    path = repo / "physical_evidence" / "GATE6_DRY_RUN_REPORT.json"
    path.write_text(
        json.dumps(
            {
                "ok": True,
                "mode": "dry_run",
                "evidence_label": "PHYSICAL_PASS",
            }
        )
    )
    result = g6._validate_sibling_report(repo, "x")
    assert result["ok"] is False
    assert result["error"] == "wrong_evidence_label"


def test_physical_pass_flag_fails(tmp_path):
    repo = tmp_path / "r"
    (repo / "physical_evidence").mkdir(parents=True)
    path = repo / "physical_evidence" / "GATE6_DRY_RUN_REPORT.json"
    path.write_text(
        json.dumps(
            {
                "ok": True,
                "mode": "dry_run",
                "evidence_label": "SYNTHETIC_EXPERIMENT",
                "physical_pass": True,
            }
        )
    )
    result = g6._validate_sibling_report(repo, "x")
    assert result["ok"] is False


def test_valid_sibling_report_passes(tmp_path):
    repo = tmp_path / "r"
    (repo / "physical_evidence").mkdir(parents=True)
    path = repo / "physical_evidence" / "GATE6_DRY_RUN_REPORT.json"
    path.write_text(
        json.dumps(
            {
                "ok": True,
                "mode": "dry_run",
                "evidence_label": "SYNTHETIC_EXPERIMENT",
                "statuses": {"GATE6_HARNESS": "GATE6_PARTIAL_HARNESS_PASS", "PHYSICAL_EVIDENCE": "PHYSICAL_EVIDENCE_PENDING"},
            }
        )
    )
    result = g6._validate_sibling_report(repo, "x")
    assert result["ok"] is True
