"""Gate 2 taxonomy vs Gate 5/6 release-evidence separation."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from evaluate_gate2_status import evaluate_gate2_system, evaluate_release_evidence  # noqa: E402


def test_release_evidence_pending_by_default():
    rel = evaluate_release_evidence()
    assert rel["release_evidence_status"] == "RELEASE_EVIDENCE_PENDING"
    assert "clean_checkout_reproduction" in rel["unmet"]
    assert "doi_or_archived_dataset" in rel["unmet"]


def test_gate2_system_pass_does_not_require_release_evidence(tmp_path):
    src = ROOT / "results/calibration/pixel6a/integrated/pixel-cal-1784756973874"
    # Use existing committed artifacts directory
    result = evaluate_gate2_system(src)
    assert result["gate2_status"] == "GATE2_SYSTEM_PASS"
    rel = evaluate_release_evidence()
    assert rel["release_evidence_status"] != "RELEASE_EVIDENCE_COMPLETE"
    # System pass must not imply release complete
    assert result["system_pass"] is True
    assert rel["release_evidence_status"] == "RELEASE_EVIDENCE_PENDING"


def test_missing_artifacts_fail(tmp_path):
    result = evaluate_gate2_system(tmp_path)
    assert result["gate2_status"] == "FAIL"
