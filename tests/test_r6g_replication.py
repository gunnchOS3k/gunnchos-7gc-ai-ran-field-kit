"""R6G-REPLICATION-ADOPTION-001 tests — honest ladder/token/claim remediation."""
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
    assert "R4" not in earned


def test_replication_honesty_caps(tmp_path: Path):
    suite = run_replication_suite(tmp_path)
    assert suite["IMPROVED_STATE_OF_ART"] is False
    assert suite["tokens"]["BREAKTHROUGH_PROVEN"] is False
    assert suite["tokens"]["STANDARDIZED_6G"] is False
    assert suite["tokens"]["R6G_INDEPENDENT_VERIFIER_PASS"] is False
    assert suite["tokens"]["R6G_DIGITAL_REPLICATION_PASS"] is False
    assert suite["tokens"]["PROMISING_DIGITAL_ANY"] is False
    assert suite["negative_result_count"] >= 5

    c003 = suite["candidates"]["R6G-003"]
    c005 = suite["candidates"]["R6G-005"]
    c009 = suite["candidates"]["R6G-009"]

    # No R6 on any candidate (same-PR cannot earn it)
    for c in (c003, c005, c009):
        assert c["IMPROVED_STATE_OF_ART"] is False
        assert c["claim_state"] not in CLAIM_STATES_FORBIDDEN
        assert c["claim_state"] != "PROMISING_DIGITAL"
        assert "R6" not in c["ladder_earned"]
        assert c["ladder_flags"]["R6"] is False

    # 003 capped at R0–R5 when multi-seed/ablation/neg hold
    assert c003["claim_state"] == "DIGITAL_IMPROVEMENT_CANDIDATE"
    assert set(c003["ladder_earned"]) <= {"R0", "R1", "R2", "R3", "R4", "R5"}
    assert "R3" in c003["ladder_earned"]
    assert c003["metrics_vary_across_seeds"] is True

    # 005/009: real seed-varying evidence published; ladder capped R0–R2; claim incomplete
    assert c005["claim_state"] == "REPLICATION_INCOMPLETE"
    assert c009["claim_state"] == "REPLICATION_INCOMPLETE"
    assert c005["ladder_earned"] == ["R0", "R1", "R2"]
    assert c009["ladder_earned"] == ["R0", "R1", "R2"]
    assert c005["metrics_vary_across_seeds"] is True
    assert c009["metrics_vary_across_seeds"] is True
    assert len({r["aware_vs_naive_adversarial_fail_delta"] for r in c005["seed_rows"]}) >= 2
    assert len({r["predictive_regret_25ms"] for r in c009["seed_rows"]}) >= 2

    # Portfolio tokens demoted
    assert suite["tokens"]["R6G_MULTI_SEED_REPRODUCED"] is False
    assert suite["tokens"]["R6G_ABLATIONS_DOCUMENTED"] is False
    assert suite["tokens"]["R6G_ABLATIONS_PARTIAL"] is True  # 003 only
    assert suite["tokens"]["R6G_FALSIFICATION_DOCUMENTED"] is True

    # Robustness seeds executed
    assert len(c003["robustness_runs"]) >= 1
    assert len(c005["robustness_runs"]) >= 1
    assert len(c009["robustness_runs"]) >= 1

    # Ablation gated on 003
    assert "ablation_ok" in c003["ablation"]
    assert c003["ladder_flags"]["R5"] == bool(c003["ablation"]["ablation_ok"])

    v = verify_from_raw(tmp_path)
    assert v["R6G_INDEPENDENT_VERIFIER_PASS"] is False
    assert v["earns_r6"] is False
    assert v["ok"] is True  # arithmetic only
    # neg double-count fix: only neg_s* files
    assert all(n.startswith("neg_s") for n in v["R6G-003"]["neg_files_counted"])

    suite2 = json.loads((tmp_path / "R6G_REPLICATION_SUITE.json").read_text())
    assert suite2["tokens"]["R6G_INDEPENDENT_VERIFIER_PASS"] is False
    assert suite2["tokens"]["R6G_DIGITAL_REPLICATION_PASS"] is False
    for cid in ("R6G-003", "R6G-005", "R6G-009"):
        assert "R6" not in suite2["candidates"][cid]["ladder_earned"]
        assert suite2["candidates"][cid]["claim_state"] != "PROMISING_DIGITAL"


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
    for row in dash["rows"]:
        assert row["IMPROVED_STATE_OF_ART"] is False
        assert row["physical_validation"] is False
        assert row["external_reproduction"] is False
        assert row["independent_verify"] is False
        assert row["claim_state"] != "BREAKTHROUGH_PROVEN"
        assert row["claim_state"] != "PROMISING_DIGITAL"


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
