"""Tests for C-PKT-002 external reproduction honesty + runners."""
from __future__ import annotations

import json
from pathlib import Path

from research.external_reproduction.adapters.probe import probe_all
from research.external_reproduction.claim_firewall import enforce_firewall
from research.external_reproduction.oulu001_fr3_mmwave import range_resolution_m, run_suite as run_oulu001
from research.external_reproduction.oulu002_cfmimo_isac import run_suite as run_oulu002

ROOT = Path(__file__).resolve().parents[1]


def test_adapters_fail_closed_on_this_host():
    probe = probe_all()
    for bid, rep in probe["adapters"].items():
        if not rep["present"]:
            assert rep["status"] == "UNAVAILABLE_FAIL_CLOSED"
            assert rep["silent_fake_forbidden"] is True
    assert probe["policy"]["silent_fake_aodt"] is False


def test_claim_firewall_forces_soa_false():
    out = enforce_firewall({"IMPROVED_STATE_OF_ART": False, "classification": "SOURCE_VERIFIED"})
    assert out["IMPROVED_STATE_OF_ART"] is False
    assert out["PHYSICAL"] is False
    assert out["6G_CERTIFIED"] is False


def test_oulu001_fr1_vs_fr3_resolvability():
    suite = run_oulu001(seeds=[7, 11])
    cls = suite["classification"]
    assert cls["IMPROVED_STATE_OF_ART"] is False
    assert cls["classification"] in ("REFERENCE_SPEC_INCOMPLETE", "DIGITAL_REPRODUCTION_PASS")
    assert cls["qualitative"]["fr1_cannot_resolve_20_21m"] is True
    assert cls["qualitative"]["fr3_can_resolve_20_21m"] is True
    # FR2 table discrepancy blocks full PASS on this host interpretation
    assert cls["classification"] == "REFERENCE_SPEC_INCOMPLETE"
    assert abs(range_resolution_m(0.1) - 1.49896) < 0.01


def test_oulu002_no_improvement_without_baseline():
    suite = run_oulu002(seeds=[7, 11])
    cls = suite["classification"]
    assert cls["IMPROVED_STATE_OF_ART"] is False
    assert cls["baseline"]["baseline_matched"] is False
    assert cls["classification"] in ("BASELINE_MATCH_PENDING", "REFERENCE_SPEC_INCOMPLETE")
    assert cls["qualitative"]["sum_rate_increases_L8_to_L16"] is True
    assert cls["qualitative"]["sensing_penalizes_communications"] is True


def test_registry_has_six_source_verified_targets():
    reg = json.loads((ROOT / "research/external_reproduction/NVIDIA_OULU_TARGET_REGISTRY.json").read_text())
    assert len(reg["queue"]) == 6
    assert all(t["source_verified"] for t in reg["queue"])
    assert all(t.get("news_only") is False for t in reg["queue"])
    ids = [t["id"] for t in reg["queue"]]
    assert ids == ["OULU-001", "OULU-002", "OULU-003", "OULU-004", "NVIDIA-001", "NVIDIA-002"]
