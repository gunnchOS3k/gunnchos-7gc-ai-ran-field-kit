"""Narrow tests for R5-S1 accepted-main reconciliation overlay."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "program" / "code_health_authenticity_baseline_v1"
STATUS = BASE / "remediation_status"
VALIDATOR = ROOT / "scripts" / "validate_code_health_r5_s1_reconciliation.py"


def test_overlay_files_exist():
    for name in (
        "CURRENT_CODE_HEALTH_STATUS.json",
        "CURRENT_CODE_HEALTH_STATUS.md",
        "R5_S1_ACCEPTED_MAIN_RECONCILIATION.json",
        "R5_S1_ACCEPTED_MAIN_RECONCILIATION.md",
        "REMEDIATION_HISTORY.json",
    ):
        assert (STATUS / name).is_file(), name
    assert (BASE / "FUTURE_WAVE_CODE_INTEGRITY_POLICY.md").is_file()


def test_severity_arithmetic():
    recon = json.loads((STATUS / "R5_S1_ACCEPTED_MAIN_RECONCILIATION.json").read_text())
    sev = recon["severity_arithmetic"]
    assert sev == {
        "historical_s0": 0,
        "historical_s1": 2,
        "current_open_s0": 0,
        "current_open_s1": 0,
        "closed_s1_since_baseline": 2,
    }
    assert recon["token"] == "CODE_HEALTH_R5_S1_ACCEPTED_MAIN_RECONCILIATION_PASS"
    assert recon["claim_boundaries"]["FULL_MUTATION_TESTING_COMPLETE"] is False


def test_historical_findings_still_show_s1():
    findings = json.loads((BASE / "FINDINGS.json").read_text())
    s1 = [f for f in findings["findings"] if f.get("severity") == "S1"]
    assert len(s1) == 2
    assert {f["repository"] for f in s1} == {"gunnchos-research-portal", "waike-research-ops"}


def test_s2_mvi_preserved():
    findings = json.loads((BASE / "FINDINGS.json").read_text())
    s2 = [f for f in findings["findings"] if f.get("severity") == "S2"]
    mvi = {
        f["repository"]
        for f in s2
        if f.get("mutation_outcome") == "MUTATION_VALIDATION_INCOMPLETE"
        or "MUTATION_VALIDATION_INCOMPLETE" in f.get("title", "")
    }
    assert {
        "7gc-digital-twin",
        "readygary-6g-beam-selection",
        "gunnchos-emergent-service-intent-protocols",
    }.issubset(mvi)


def test_digital_baseline_frozen():
    # R5 overlay itself must still record the pre-Wave010 freeze it left.
    recon = json.loads(
        (ROOT / "program/code_health_authenticity_baseline_v1/remediation_status/R5_S1_ACCEPTED_MAIN_RECONCILIATION.json").read_text()
    )
    r5 = recon["digital_baseline"]
    assert r5["ATOMIC_TOTAL"] == 419
    assert r5["DIGITAL_IMPLEMENTATION_COMPLETE"] == 111
    assert r5["DIGITAL_IMPLEMENTATION_OPEN"] == 51
    assert r5["DIGITAL_VALIDATION_OPEN"] == 0
    assert r5["DIGITAL_CONTROLLABLE_POOL"] == 162
    # Live baseline may advance via later accepted closeouts (Wave010 GAME-PP).
    br = json.loads((ROOT / "program/digital_ecosystem_baseline_v2/BASELINE_V2_RESULT.json").read_text())
    t = br["totals"]
    assert t["ATOMIC_TOTAL"] == 419
    assert t["DIGITAL_IMPLEMENTATION_COMPLETE"] >= 111
    assert t["DIGITAL_IMPLEMENTATION_OPEN"] <= 51
    assert t["DIGITAL_VALIDATION_OPEN"] == 0
    assert t["EVIDENCE_MAPPING_OPEN"] == 0
    assert (
        t["DIGITAL_IMPLEMENTATION_COMPLETE"]
        + t["DIGITAL_IMPLEMENTATION_OPEN"]
        + t["DIGITAL_VALIDATION_OPEN"]
        == 162
    )


def test_validator_pass_offline():
    env = dict(os.environ)
    env["SKIP_LIVE_GITHUB"] = "1"
    r = subprocess.run(
        [sys.executable, str(VALIDATOR)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        env=env,
        timeout=120,
    )
    assert r.returncode == 0, r.stderr + r.stdout
    assert "CODE_HEALTH_R5_S1_ACCEPTED_MAIN_RECONCILIATION_PASS" in r.stdout
