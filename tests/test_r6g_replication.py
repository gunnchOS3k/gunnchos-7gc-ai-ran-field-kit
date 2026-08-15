"""R6G-REPLICATION-ADOPTION-001 tests — multi-seed, falsification, verifier, claim honesty."""
from __future__ import annotations

import json
from pathlib import Path

from research.r6g.replication.ladder import CLAIM_STATES_FORBIDDEN, contiguous_earned
from research.r6g.replication.reproduce import run_replication_suite
from research.r6g.replication.verify_independent import verify_from_raw
from research.r6g.metrics.useful_connectivity import (
    PREREGISTERED_WEIGHT_SCHEME,
    sensitivity_analysis,
    useful_connectivity_score,
)

ROOT = Path(__file__).resolve().parents[1]


def test_ladder_no_auto_inherit_across_gap():
    flags = {"R0": True, "R1": True, "R2": True, "R3": False, "R4": True, "R5": True}
    earned = contiguous_earned(flags)
    assert earned == ["R0", "R1", "R2"]
    assert "R4" not in earned  # gap at R3 blocks climb


def test_replication_suite_and_independent_verifier(tmp_path: Path):
    suite = run_replication_suite(tmp_path)
    assert suite["IMPROVED_STATE_OF_ART"] is False
    assert suite["tokens"]["BREAKTHROUGH_PROVEN"] is False
    assert suite["tokens"]["STANDARDIZED_6G"] is False
    assert suite["negative_result_count"] >= 5
    for cid in ("R6G-003", "R6G-005", "R6G-009"):
        c = suite["candidates"][cid]
        assert c["IMPROVED_STATE_OF_ART"] is False
        assert c["claim_state"] not in CLAIM_STATES_FORBIDDEN
        assert "R4" in c["ladder_earned"] or c["ladder_flags"]["R4"] is True
        assert (tmp_path / "raw" / cid).exists()

    v = verify_from_raw(tmp_path)
    assert v["ok"] is True
    assert v["IMPROVED_STATE_OF_ART"] is False
    assert v["BREAKTHROUGH_PROVEN"] is False
    suite2 = json.loads((tmp_path / "R6G_REPLICATION_SUITE.json").read_text())
    assert suite2["tokens"]["R6G_INDEPENDENT_VERIFIER_PASS"] is True
    assert suite2["tokens"]["R6G_DIGITAL_REPLICATION_PASS"] is True
    for cid in ("R6G-003", "R6G-005", "R6G-009"):
        assert "R6" in suite2["candidates"][cid]["ladder_earned"]
        assert suite2["candidates"][cid]["claim_state"] in (
            "PROMISING_DIGITAL",
            "DIGITAL_IMPROVEMENT_CANDIDATE",
        )


def test_negative_results_register_published(tmp_path: Path):
    run_replication_suite(tmp_path)
    neg = json.loads((tmp_path / "R6G_NEGATIVE_RESULTS.json").read_text())
    assert neg["count"] == len(neg["results"])
    assert neg["IMPROVED_STATE_OF_ART"] is False
    packets = {r["packet"] for r in neg["results"]}
    assert "R6G-003" in packets and "R6G-005" in packets and "R6G-009" in packets


def test_dashboard_cannot_look_like_breakthrough(tmp_path: Path):
    run_replication_suite(tmp_path)
    dash = json.loads((tmp_path / "R6G_PORTFOLIO_DASHBOARD.json").read_text())
    assert dash["IMPROVED_STATE_OF_ART"] is False
    assert "simulation" in dash["disclaimer"].lower() or "Interesting" in dash["disclaimer"]
    for row in dash["rows"]:
        assert row["IMPROVED_STATE_OF_ART"] is False
        assert row["physical_validation"] is False
        assert row["external_reproduction"] is False
        assert row["claim_state"] != "BREAKTHROUGH_PROVEN"


def test_ucs_preregistered_and_sensitive():
    assert PREREGISTERED_WEIGHT_SCHEME["NOT_ITU_METRIC"] is True
    s = useful_connectivity_score(R=0.55, D=0.8, A=0.9, Q=0.85, P=1.0, C=1.0)
    assert s["classification"] == "GUNNCHOS_PROPOSED_METRIC"
    sens = sensitivity_analysis({"R": 0.55, "D": 0.8, "A": 0.9, "Q": 0.85, "P": 1.0, "C": 1.0})
    assert len(sens["rows"]) == 12


def test_adoption_packages_exist_for_eleven_packets():
    base = ROOT / "research/r6g/adoption/packages"
    for i in range(1, 12):
        pid = f"R6G-{i:03d}"
        man = json.loads((base / pid / "manifest.json").read_text())
        assert man["IMPROVED_STATE_OF_ART"] is False
        assert (base / pid / "README.md").exists()


def test_external_reproduction_pending():
    st = json.loads((ROOT / "research/r6g/external_reproduction/STATUS.json").read_text())
    assert st["status"] == "EXTERNAL_REPRODUCTION_PENDING"
    assert st["doi"] is None
    assert st["peer_review"] is False


def test_waike_case_studies_not_validation():
    text = (ROOT / "research/r6g/waike/case_studies/R6G-003.md").read_text()
    assert "NOT count as scientific validation" in text or "Does NOT count" in text
