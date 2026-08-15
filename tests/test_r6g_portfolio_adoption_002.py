"""R6G-PORTFOLIO-ADOPTION-002 — deepen 001/002/004/008/010/011; preserve #79 claims."""
from __future__ import annotations

import json
from pathlib import Path

from research.r6g import evaluate_r6g
from research.r6g.experiments.r6g002_spectrum_fabric import run_r6g002
from research.r6g.experiments.r6g004_multimodal_isac_personal import run_r6g004
from research.r6g.experiments.r6g006_cellfree_mimo_contract import run_r6g006
from research.r6g.experiments.r6g007_adaptive_ris_contract import run_r6g007
from research.r6g.experiments.r6g008_semantic_ntn import run_r6g008
from research.r6g.experiments.r6g010_security_pqc_privacy import run_r6g010
from research.r6g.experiments.r6g011_imt2030_harness import run_r6g011
from research.r6g.metrics.useful_connectivity import useful_connectivity_score

ROOT = Path(__file__).resolve().parents[1]


def test_portfolio_adoption_002_preserves_79_claims(tmp_path: Path):
    report = evaluate_r6g(tmp_path)
    assert report["ok"] is True
    assert report["wave"] == "R6G-PORTFOLIO-ADOPTION-002"
    assert report["IMPROVED_STATE_OF_ART"] is False
    c = report["replication"]["candidates"]
    assert c["R6G-003"]["claim_state"] == "DIGITAL_IMPROVEMENT_CANDIDATE"
    assert c["R6G-005"]["claim_state"] == "REPLICATION_INCOMPLETE"
    assert c["R6G-009"]["claim_state"] == "REPLICATION_INCOMPLETE"
    assert report["tokens"]["STANDARDIZED_6G"] is False
    assert report["tokens"]["COMPLIANT"] is False
    assert report["tokens"]["PHYSICAL_RING"] is False
    # Honesty demotions (#80 remediation)
    assert report["tokens"]["HYBRID_SPECTRUM_FABRIC_DIGITAL"] is False
    assert report["tokens"]["MULTIMODAL_ISAC_PERSONAL_DIGITAL"] is False
    assert report["tokens"]["SEMANTIC_CONTINUITY_NTN_EDU_DIGITAL"] is False
    assert report["tokens"]["SECURITY_PQC_PRIVACY_HOOKS_DIGITAL"] is False
    assert report["tokens"]["IMT2030_HARNESS_DIGITAL"] is False
    matrix = report["portfolio_matrix"]
    assert len(matrix["rows"]) == 11
    by = {r["packet"]: r for r in matrix["rows"]}
    assert by["R6G-001"]["status"] == "COMPLETE_DIGITAL_REGISTRY"
    assert by["R6G-003"]["claim_state"] == "DIGITAL_IMPROVEMENT_CANDIDATE"
    assert by["R6G-005"]["claim_state"] == "REPLICATION_INCOMPLETE"
    assert by["R6G-009"]["claim_state"] == "REPLICATION_INCOMPLETE"
    assert by["R6G-002"]["claim_state"] == "MODELED_ILLUSTRATIVE"
    assert by["R6G-004"]["claim_state"] == "MODELED_SYNTHETIC_STUB"
    assert by["R6G-008"]["claim_state"] == "MODELED_LOOKUP_TABLE"
    assert by["R6G-010"]["claim_state"] == "MODELED_SCORING_HOOKS"
    assert by["R6G-011"]["claim_state"] == "HARNESS_MAP_ONLY"
    for pid in ("R6G-002", "R6G-004", "R6G-008", "R6G-010", "R6G-011"):
        assert by[pid]["ladder_earned"] == ["R0", "R1"]
    assert by["R6G-006"]["status"] == "MODELED_CONTRACT_ONLY"
    assert by["R6G-007"]["status"] == "MODELED_CONTRACT_ONLY"
    neg = json.loads((tmp_path / "replication" / "R6G_NEGATIVE_RESULTS.json").read_text())
    assert neg["count"] == len(neg["results"])
    assert all(not r.get("ILLUSTRATIVE") for r in neg["results"])
    assert neg.get("illustrative_count", 0) >= 1
    assert (tmp_path / "OPEN.md").exists()
    assert (tmp_path / "R6G_PORTFOLIO_MATRIX.json").exists()


def test_spectrum_fabric_continuum_and_ucs():
    r = run_r6g002()
    assert r["ok"] is True
    assert r["claim_state"] == "MODELED_ILLUSTRATIVE"
    assert r["status"] == "MODELED_ILLUSTRATIVE"
    assert r["ladder_earned"] == ["R0", "R1"]
    assert r["HYBRID_SPECTRUM_FABRIC_DIGITAL"] is False
    assert "bearer_continuum" in r
    assert len(r["bearer_continuum"]) >= 7
    assert "policy_comparisons" in r
    assert "ucs_predeclared" in r["policy_comparisons"]
    ucs = r["useful_connectivity_comparison"]
    assert ucs["research_metric_class"] == "GUNNCHOS_PROPOSED_RESEARCH_METRIC"
    assert ucs["no_146_gt_145_claim"] is True
    s = useful_connectivity_score(R=0.5, D=0.5, A=0.5, Q=0.5, P=1.0, C=1.0)
    assert s["research_metric_class"] == "GUNNCHOS_PROPOSED_RESEARCH_METRIC"


def test_r6g004_synthetic_privacy_no_physical_ring():
    r = run_r6g004()
    assert r["PHYSICAL_RING"] is False
    assert r["claim_state"] == "MODELED_SYNTHETIC_STUB"
    assert r["MULTIMODAL_ISAC_PERSONAL_DIGITAL_IMPROVEMENT"] is False
    assert r["dataset"]["type"] == "SYNTHETIC_LABELED"
    assert r["dataset"]["real_humans"] is False
    assert all(n.get("ILLUSTRATIVE") for n in r["documented_negative_or_no_gain"])
    assert r["IMPROVED_STATE_OF_ART"] is False


def test_r6g008_no_learning_outcomes():
    r = run_r6g008()
    assert r["claim_state"] == "MODELED_LOOKUP_TABLE"
    assert r["SEMANTIC_CONTINUITY_NTN_EDU_DIGITAL"] is False
    assert r["real_education_outcome_claimed"] is False
    assert r["guaranteed_learning_outcomes"] is False
    assert r["waike_transfer"]["counts_as_scientific_validation"] is False


def test_r6g006_007_contracts_safe():
    r6 = run_r6g006()
    r7 = run_r6g007()
    assert r6["status"] == "MODELED_CONTRACT_ONLY"
    assert r7["status"] == "MODELED_CONTRACT_ONLY"
    assert r7["RIS_PURCHASE"] is False
    assert r6["HARDWARE_PENDING"] is True


def test_r6g010_011_never_compliant():
    r10 = run_r6g010()
    r11 = run_r6g011()
    assert r10["claim_state"] == "MODELED_SCORING_HOOKS"
    assert r11["claim_state"] == "HARNESS_MAP_ONLY"
    assert r10["SECURITY_PQC_PRIVACY_HOOKS_DIGITAL"] is False
    assert r11["IMT2030_HARNESS_DIGITAL"] is False
    assert r10["COMPLIANT"] is False
    assert r10["STANDARDIZED_6G"] is False
    assert r11["claim_boundary"]["COMPLIANT"] is False
    assert r11["claim_boundary"]["STANDARDIZED_6G"] is False
    assert r11["all_official_values_pending"] is True
    assert r10["falsification"]["overclaim_trap_scores_worse_when_privacy_collapses"] is True


def test_waike_case_studies_exist_for_new_packets():
    for pid in ("R6G-004", "R6G-008", "R6G-010", "R6G-011"):
        text = (ROOT / f"research/r6g/waike/case_studies/{pid}.md").read_text()
        assert "Does NOT count" in text or "NOT count as scientific validation" in text


def test_atlas_index_official_value_pending():
    atlas = json.loads((ROOT / "research/6g_breakthroughs/ATLAS_INDEX.json").read_text())
    assert atlas["IMPROVED_STATE_OF_ART"] is False
    assert atlas["NEW_6G_RESEARCH_REPO_CREATION"] == "FORBIDDEN_BY_DEFAULT"
    assert atlas["breakthrough_count"] >= 20
    assert atlas["official_value_pending_count"] >= 1
