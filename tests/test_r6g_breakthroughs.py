"""R6G breakthrough program tests — claim firewall + active packets."""
from __future__ import annotations

import json
from pathlib import Path

from research.r6g import evaluate_r6g
from net_sec_rc001 import evaluate_net_sec_rc001
from net_sec_rc001.tokens import FORBIDDEN_TOKENS, PRODUCT_WORDING

ROOT = Path(__file__).resolve().parents[1]


def test_r6g_registry_has_at_least_20_breakthroughs():
    reg = json.loads((ROOT / "research/6g_breakthroughs/BREAKTHROUGH_REGISTRY.json").read_text())
    assert reg["count"] >= 20
    assert reg["claim_firewall"]["IMPROVED_STATE_OF_ART"] is False
    assert reg["NEW_6G_RESEARCH_REPO_CREATION"] == "FORBIDDEN_BY_DEFAULT"
    required = {
        "id", "title", "organization", "baseline_metric", "baseline_value", "baseline_units",
        "reproduction_owner_repo", "digital_reproduction_possible", "status",
    }
    for b in reg["breakthroughs"]:
        assert required <= set(b.keys())
        assert b["IMPROVED_STATE_OF_ART"] is False


def test_r6g_backlog_eleven_packets_ownership():
    backlog = json.loads((ROOT / "research/6g_breakthroughs/RESEARCH_BACKLOG.json").read_text())
    assert len(backlog["packets"]) == 11
    by_id = {p["work_packet"]: p for p in backlog["packets"]}
    assert by_id["R6G-001"]["status"] == "ACTIVE"
    assert by_id["R6G-003"]["status"] == "ACTIVE"
    assert by_id["R6G-005"]["status"] == "ACTIVE"
    assert by_id["R6G-009"]["status"] == "ACTIVE"
    assert by_id["R6G-002"]["status"] == "ACTIVE"
    for pid, st in (
        ("R6G-004", "MODELED_SYNTHETIC_STUB"),
        ("R6G-008", "MODELED_LOOKUP_TABLE"),
        ("R6G-010", "MODELED_SCORING_HOOKS"),
        ("R6G-011", "HARNESS_MAP_ONLY"),
    ):
        assert by_id[pid]["status"] == st
    for pid in ("R6G-006", "R6G-007"):
        assert by_id[pid]["status"] == "MODELED_CONTRACT_ONLY"


def test_r6g_aggregate_and_firewall(tmp_path: Path):
    report = evaluate_r6g(tmp_path)
    assert report["ok"] is True
    assert report["IMPROVED_STATE_OF_ART"] is False
    assert report["breakthroughs_registered"] >= 20
    assert report["tokens"]["IMPROVED_STATE_OF_ART"] is False
    assert report["tokens"]["6G_BREAKTHROUGH_PASS"] is None
    assert report["independent_improvements_verified"] is False
    assert report["physical_pending"] is True
    assert report["baselines_digitally_matched_to_published_physical"] is False
    assert report["naked_numeric_headline_count"] == 0
    assert report["falsifiability"]["R6G-003"] is True
    assert report["falsifiability"]["R6G-005"] is True
    assert report["falsifiability"]["R6G-009"] is True
    assert len(report["documented_negative_experiments"]["R6G-003"]) >= 1
    assert len(report["documented_negative_experiments"]["R6G-005"]) >= 1
    assert len(report["documented_negative_experiments"]["R6G-009"]) >= 1


def test_registry_no_naked_numeric_headlines():
    reg = json.loads((ROOT / "research/6g_breakthroughs/BREAKTHROUGH_REGISTRY.json").read_text())
    naked = 0
    for b in reg["breakthroughs"]:
        val = b.get("baseline_value")
        if isinstance(val, (int, float)) and b.get("headline_numeric_claim") is True:
            dist = str(b.get("distance", "")).upper()
            bw = str(b.get("bandwidth", "")).upper()
            if "NOT_PUBLICLY_PINNED" in dist or "NOT_PUBLICLY_PINNED" in bw:
                naked += 1
        if isinstance(val, (int, float)):
            # Soft policy: numeric values require explicit pin status
            assert b.get("baseline_value_status") == "PINNED_WITH_CONTEXT"
            assert b.get("headline_numeric_claim") is True
        else:
            assert b.get("headline_numeric_claim") is not True
    assert naked == 0
    assert reg.get("naked_headline_policy", {}).get("naked_numeric_headline_count", 0) == 0


def test_net_sec_includes_r6g_tokens(tmp_path: Path):
    report = evaluate_net_sec_rc001(tmp_path)
    assert report["ok"] is True
    assert report["tokens"]["5GA_TERRESTRIAL_DIGITAL_RUNTIME"] is False
    assert report["tokens"]["5G_REL16_TERRESTRIAL_DIGITAL_RUNTIME"] is True
    assert report["tokens"]["R6G_REGISTRY_COMPLETE"] is True
    assert report["tokens"]["IMPROVED_STATE_OF_ART"] is False
    # Capability depth (#80): spectrum/semantic digital tokens earned via execution
    assert report["tokens"]["HYBRID_SPECTRUM_FABRIC_DIGITAL"] is True
    assert report["tokens"]["SEMANTIC_CONTINUITY_NTN_EDU_DIGITAL"] is True
    for k in FORBIDDEN_TOKENS:
        assert report["tokens"][k] is False
    assert "Rel-16" in PRODUCT_WORDING
    assert report["r6g"]["breakthroughs_registered"] >= 20
    assert report["r6g"]["naked_numeric_headline_count"] == 0
    # Dual-tree: authoritative path pointer, not a forked metric tree
    assert (tmp_path / "r6g" / "AUTHORITATIVE_PATH.json").exists()


def test_multimodal_improvement_only_vs_digital_rf_only():
    from research.r6g.experiments.r6g003_fr3_isac import run_r6g003

    r = run_r6g003()
    assert r["IMPROVED_STATE_OF_ART"] is False
    assert r["falsifiable"] is True
    assert r["rf_only_digital_baseline"]["DIGITAL_REPRODUCTION_MATCHED"] is False
    assert r["negative_cases_observed"] is True
    assert len(r["documented_negative_or_no_gain"]) >= 1
    # Negative suite must include at least one multimodal loss vs RF-only
    assert any(n["multimodal_failed_to_beat_rf"] for n in r["negative_suite"])
    if r["MULTIMODAL_ISAC_DIGITAL_IMPROVEMENT"]:
        assert r["primary_improvement_observed"] is True
        for p in r["primary_suite"]:
            assert p["RF_ALL_RMSE"] < p["RF_ONLY_RMSE"]


def test_ai_phy_and_predictive_are_falsifiable():
    from research.r6g.experiments.r6g005_ai_phy import run_r6g005
    from research.r6g.experiments.r6g009_predictive_twin import run_r6g009

    r5 = run_r6g005()
    assert r5["falsifiable"] is True
    assert r5["beats_nokia_qualcomm_ota"] is False
    assert r5["IMPROVED_STATE_OF_ART"] is False
    assert len(r5["documented_negative_or_no_gain"]) >= 1
    if r5["HYPOTHESIS_SUPPORTED_DIGITALLY"]:
        assert r5["primary_support_aware_vs_naive"] is True

    r9 = run_r6g009()
    assert r9["falsifiable"] is True
    assert r9["IMPROVED_STATE_OF_ART"] is False
    assert len(r9["documented_negative_or_no_gain"]) >= 1
    # Must be able to lose: long horizon or jump suite
    assert r9["negative_suite"]["long_horizon_no_gain"] or r9["negative_suite"]["jump_no_gain"]
    if r9["HYPOTHESIS_SUPPORTED_DIGITALLY"]:
        assert r9["primary_moderate_delay_improvement"] is True


def test_useful_connectivity_is_proposed_metric_only():
    from research.r6g.metrics.useful_connectivity import useful_connectivity_score

    s = useful_connectivity_score(R=1, D=1, A=1, Q=1, P=1, C=1)
    assert s["classification"] == "GUNNCHOS_PROPOSED_METRIC"
    assert s["NOT_ITU_METRIC"] is True


def test_semantic_continuity_no_real_education_claim():
    from research.r6g.experiments.semantic_continuity_ntn_education import run_semantic_continuity

    r = run_semantic_continuity()
    assert r["real_education_outcome_claimed"] is False
    assert r["human_study"] == "EXTERNAL_PENDING"
