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
    for pid in ("R6G-004", "R6G-006", "R6G-007", "R6G-008", "R6G-010", "R6G-011"):
        assert by_id[pid]["status"] == "REGISTERED_NOT_ACTIVE"


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


def test_net_sec_includes_r6g_tokens(tmp_path: Path):
    report = evaluate_net_sec_rc001(tmp_path)
    assert report["ok"] is True
    assert report["tokens"]["5GA_TERRESTRIAL_DIGITAL_RUNTIME"] is False
    assert report["tokens"]["5G_REL16_TERRESTRIAL_DIGITAL_RUNTIME"] is True
    assert report["tokens"]["R6G_REGISTRY_COMPLETE"] is True
    assert report["tokens"]["IMPROVED_STATE_OF_ART"] is False
    for k in FORBIDDEN_TOKENS:
        assert report["tokens"][k] is False
    assert "Rel-16" in PRODUCT_WORDING
    assert report["r6g"]["breakthroughs_registered"] >= 20


def test_multimodal_improvement_only_vs_digital_rf_only():
    from research.r6g.experiments.r6g003_fr3_isac import run_r6g003

    r = run_r6g003()
    assert r["IMPROVED_STATE_OF_ART"] is False
    assert r["rf_only_digital_baseline"]["DIGITAL_REPRODUCTION_MATCHED"] is False
    if r["MULTIMODAL_ISAC_DIGITAL_IMPROVEMENT"]:
        rf = r["modality_matrix"]["RF_ONLY"]["position_RMSE"]
        assert all(
            r["modality_matrix"][m]["position_RMSE"] < rf
            for m in r["modality_matrix"]
            if m != "RF_ONLY"
        )


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
