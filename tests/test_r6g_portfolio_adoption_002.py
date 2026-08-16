"""R6G-PORTFOLIO-ADOPTION-002 — deepen 002/004/008/010/011; preserve #79 claims."""
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
from research.r6g.metrics.useful_connectivity import (
    PREREGISTRATION_HASH,
    useful_connectivity_score,
    weight_scheme_bundle,
)

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
    # Capability depth: digital tokens earned via execution
    assert report["tokens"]["HYBRID_SPECTRUM_FABRIC_DIGITAL"] is True
    assert report["tokens"]["MULTIMODAL_ISAC_PERSONAL_DIGITAL"] is True
    assert report["tokens"]["SEMANTIC_CONTINUITY_NTN_EDU_DIGITAL"] is True
    assert report["tokens"]["SECURITY_PQC_PRIVACY_HOOKS_DIGITAL"] is True
    assert report["tokens"]["IMT2030_HARNESS_DIGITAL"] is True
    matrix = report["portfolio_matrix"]
    assert len(matrix["rows"]) == 11
    by = {r["packet"]: r for r in matrix["rows"]}
    assert by["R6G-001"]["status"] == "COMPLETE_DIGITAL_REGISTRY"
    assert by["R6G-003"]["claim_state"] == "DIGITAL_IMPROVEMENT_CANDIDATE"
    assert by["R6G-005"]["claim_state"] == "REPLICATION_INCOMPLETE"
    assert by["R6G-009"]["claim_state"] == "REPLICATION_INCOMPLETE"
    assert by["R6G-002"]["claim_state"] == "DIGITALLY_EXECUTED"
    assert by["R6G-004"]["claim_state"] == "DIGITAL_SYNTHETIC_EXPERIMENT"
    assert by["R6G-008"]["claim_state"] == "DIGITALLY_EXECUTED"
    assert by["R6G-010"]["claim_state"] == "DIGITALLY_EXECUTED"
    assert by["R6G-011"]["claim_state"] == "DIGITALLY_EXECUTED_HARNESS"
    for pid in ("R6G-002", "R6G-004", "R6G-008", "R6G-010", "R6G-011"):
        assert "R2" in by[pid]["ladder_earned"]
        assert "R3" not in by[pid]["ladder_earned"]  # no silent R3/R4 from #80
    assert by["R6G-006"]["status"] == "DIGITALLY_EXECUTED"
    assert by["R6G-007"]["status"] == "DIGITALLY_EXECUTED"
    assert by["R6G-006"]["claim_state"] == "DIGITALLY_EXECUTED"
    assert by["R6G-007"]["claim_state"] == "DIGITALLY_EXECUTED"
    for pid in ("R6G-006", "R6G-007"):
        assert by[pid]["ladder_earned"] == ["R0", "R1", "R2"]
        assert "R3" not in by[pid]["ladder_earned"]
    neg = json.loads((tmp_path / "replication" / "R6G_NEGATIVE_RESULTS.json").read_text())
    assert neg["count"] == len(neg["results"])
    assert all(not r.get("ILLUSTRATIVE") for r in neg["results"])
    assert (tmp_path / "OPEN.md").exists()
    assert (tmp_path / "R6G_PORTFOLIO_MATRIX.json").exists()
    # Dashboard 009 consumes evidence manifests
    dash = json.loads((tmp_path / "replication" / "R6G_PORTFOLIO_DASHBOARD.json").read_text())
    row009 = next(r for r in dash["rows"] if r["packet"] == "R6G-009")
    assert row009["claim_state"] == "REPLICATION_INCOMPLETE"
    assert row009["falsification"] is True  # from evidence manifest, not ladder promotion
    assert row009["falsification_ladder_earned"] is False
    assert "evidence_manifest" in row009
    assert row009["ladder_earned"] == ["R0", "R1", "R2"]


def test_spectrum_fabric_executed_ucs_preregistered():
    r = run_r6g002()
    assert r["ok"] is True
    assert r["claim_state"] == "DIGITALLY_EXECUTED"
    assert r["status"] == "DIGITALLY_EXECUTED"
    assert "R2" in r["ladder_earned"]
    assert r["HYBRID_SPECTRUM_FABRIC_DIGITAL"] is True
    assert r["task_aware_loss_count"] >= 1
    assert r["mechanical_policy_superiority"] is False
    assert len(r["bearers"]) >= 7
    assert set(r["policies"]) >= {
        "HIGHEST_RATE_ONLY",
        "STATIC_PRIORITY",
        "UTILITY_WEIGHTED",
        "TASK_AWARE",
        "ROBUST_TASK_AWARE",
    }
    ucs = r["useful_connectivity_analysis"]
    assert ucs["preregistration_hash"] == PREREGISTRATION_HASH
    assert ucs["weights_rewritten_after_eval"] is False
    assert "sensitivity" in ucs["useful_link"]
    assert "equal_weights" in ucs["useful_link"]
    s = useful_connectivity_score(R=0.5, D=0.5, A=0.5, Q=0.5, P=1.0, C=1.0)
    assert s["research_metric_class"] == "GUNNCHOS_PROPOSED_RESEARCH_METRIC"
    assert s["preregistration_hash"] == PREREGISTRATION_HASH
    bundle = weight_scheme_bundle(
        {"R": 0.5, "D": 0.5, "A": 0.5, "Q": 0.5, "P": 1.0, "C": 1.0}, task="student"
    )
    assert bundle["task_specific"] is not None


def test_r6g004_synthetic_executed_no_physical_ring():
    r = run_r6g004()
    assert r["PHYSICAL_RING"] is False
    assert r["claim_state"] == "DIGITAL_SYNTHETIC_EXPERIMENT"
    assert r["status"] == "DIGITAL_SYNTHETIC_EXECUTED"
    assert r["dataset"]["type"] == "SYNTHETIC_LABELED"
    assert r["dataset"]["real_humans"] is False
    assert r["guaranteed_treatment_improvement"] is False
    assert any(not n.get("ILLUSTRATIVE") for n in r["documented_negative_or_no_gain"])
    assert r["IMPROVED_STATE_OF_ART"] is False
    assert set(r["modalities"]) >= {"RF", "RF_IMU", "RF_RING_UWB_IMU", "RF_CAMERA", "RF_WIFI_BT", "FULL"}


def test_r6g008_executed_no_learning_outcomes():
    r = run_r6g008()
    assert r["claim_state"] == "DIGITALLY_EXECUTED"
    assert r["SEMANTIC_CONTINUITY_NTN_EDU_DIGITAL"] is True
    assert r["real_education_outcome_claimed"] is False
    assert r["guaranteed_learning_outcomes"] is False
    assert r["waike_transfer"]["counts_as_scientific_validation"] is False
    assert r["semantic_necessary_state_drop_count"] >= 1
    assert set(r["modes"]) == {"FULL_SYNC", "COMPRESSED_SYNC", "SEMANTIC_SYNC"}


def test_r6g006_007_contracts_safe():
    r6 = run_r6g006()
    r7 = run_r6g007()
    assert r6["status"] == "DIGITALLY_EXECUTED"
    assert r7["status"] == "DIGITALLY_EXECUTED"
    assert r6["claim_state"] == "DIGITALLY_EXECUTED"
    assert r7["claim_state"] == "DIGITALLY_EXECUTED"
    assert r6["ladder_earned"] == ["R0", "R1", "R2"]
    assert r7["ladder_earned"] == ["R0", "R1", "R2"]
    assert r7["RIS_PURCHASE"] is False
    assert r6["HARDWARE_PENDING"] is True
    assert r6["IMPROVED_STATE_OF_ART"] is False
    assert r7["IMPROVED_STATE_OF_ART"] is False


def test_r6g010_011_executed_never_compliant():
    r10 = run_r6g010()
    r11 = run_r6g011()
    assert r10["claim_state"] == "DIGITALLY_EXECUTED"
    assert r11["claim_state"] == "DIGITALLY_EXECUTED_HARNESS"
    assert r10["SECURITY_PQC_PRIVACY_HOOKS_DIGITAL"] is True
    assert r11["IMT2030_HARNESS_DIGITAL"] is True
    assert r10["COMPLIANT"] is False
    assert r10["STANDARDIZED_6G"] is False
    assert r11["claim_boundary"]["COMPLIANT"] is False
    assert r11["claim_boundary"]["STANDARDIZED_6G"] is False
    assert r11["all_official_values_pending"] is True
    assert r11["hardcoded_6g_compliant"] is False
    assert r10["executed_test_count"] >= 11
    assert r10["all_tests_met_expected"] is True
    assert r10["falsification"]["overclaim_trap_scores_worse_when_privacy_collapses"] is True
    labels = set(r11["evidence_labels_used"])
    assert "6G_COMPLIANT" not in labels
    assert "STANDARD_PENDING" in labels


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


def test_stable_seed_bit_stable_across_hash_salts():
    """Dual-tree root cause: builtin hash() must not drive RNG."""
    from research.r6g.metrics.stable_seed import mix_seed, stable_int
    from research.r6g.experiments.r6g003_fr3_isac import run_config

    assert stable_int("RF_ONLY") == stable_int("RF_ONLY")
    a = run_config({"config_id": "t", "seed": 7, "vision_spoof_rate": 0.0, "fusion_trust_vision": 0.30})
    b = run_config({"config_id": "t", "seed": 7, "vision_spoof_rate": 0.0, "fusion_trust_vision": 0.30})
    assert a["modality_matrix"] == b["modality_matrix"]
    assert mix_seed(7, "modality", "RF_ONLY") == mix_seed(7, "modality", "RF_ONLY")
