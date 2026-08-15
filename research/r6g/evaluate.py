"""Aggregate R6G evaluation for NET-SEC stream extension."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any

from research.r6g.claim_firewall import IMPROVED_STATE_OF_ART, assert_no_soa
from research.r6g.experiments.r6g002_spectrum_fabric import run_r6g002
from research.r6g.experiments.r6g003_fr3_isac import run_r6g003
from research.r6g.experiments.r6g005_ai_phy import run_r6g005
from research.r6g.experiments.r6g009_predictive_twin import run_r6g009
from research.r6g.experiments.semantic_continuity_ntn_education import run_semantic_continuity

ROOT = Path(__file__).resolve().parents[2]
REG = ROOT / "research" / "6g_breakthroughs"


def evaluate_r6g(out_dir: Path | None = None) -> dict[str, Any]:
    registry = json.loads((REG / "BREAKTHROUGH_REGISTRY.json").read_text(encoding="utf-8"))
    backlog = json.loads((REG / "RESEARCH_BACKLOG.json").read_text(encoding="utf-8"))
    r001 = {
        "packet": "R6G-001",
        "ok": registry["count"] >= 20 and len(backlog["packets"]) == 11,
        "status": "COMPLETE_DIGITAL_REGISTRY",
        "breakthroughs_registered": registry["count"],
        "IMPROVED_STATE_OF_ART": False,
        "sources_verified": "PORTAL_OR_PENDING_DOI_PIN",
        "NEW_6G_RESEARCH_REPO_CREATION": "FORBIDDEN_BY_DEFAULT",
    }
    r003 = run_r6g003()
    r005 = run_r6g005()
    r009 = run_r6g009()
    r002 = run_r6g002()
    sem = run_semantic_continuity()

    active = {
        "R6G-001": {"status": "COMPLETE_DIGITAL_REGISTRY", "ok": r001["ok"]},
        "R6G-003": {"status": r003["status"], "ok": r003["ok"], "MULTIMODAL_ISAC_DIGITAL_IMPROVEMENT": r003["MULTIMODAL_ISAC_DIGITAL_IMPROVEMENT"]},
        "R6G-005": {"status": r005["status"], "ok": r005["ok"], "HYPOTHESIS_SUPPORTED_DIGITALLY": r005["HYPOTHESIS_SUPPORTED_DIGITALLY"]},
        "R6G-009": {"status": r009["status"], "ok": r009["ok"], "HYPOTHESIS_SUPPORTED_DIGITALLY": r009["HYPOTHESIS_SUPPORTED_DIGITALLY"]},
        "R6G-002": {"status": r002["status"], "ok": r002["ok"]},
    }
    not_active = [p["work_packet"] for p in backlog["packets"] if p["status"] == "REGISTERED_NOT_ACTIVE"]

    tokens = {
        "R6G_REGISTRY_COMPLETE": r001["ok"],
        "MULTIMODAL_ISAC_DIGITAL_IMPROVEMENT": bool(r003["MULTIMODAL_ISAC_DIGITAL_IMPROVEMENT"]),
        "AI_PHY_UNCERTAINTY_AWARE_DIGITAL": bool(r005["HYPOTHESIS_SUPPORTED_DIGITALLY"]),
        "PREDICTIVE_RADIO_DT_DIGITAL": bool(r009["HYPOTHESIS_SUPPORTED_DIGITALLY"]),
        "HYBRID_SPECTRUM_FABRIC_DIGITAL": bool(r002["ok"]),
        "SEMANTIC_CONTINUITY_NTN_EDU_DIGITAL": bool(sem["ok"]),
        "IMPROVED_STATE_OF_ART": False,
        "6G_BREAKTHROUGH_PASS": None,
        "PHYSICAL_REPRODUCTION_PENDING": True,
        "COMPARABLE_EVIDENCE_PENDING": True,
    }

    report = {
        "schema": "gunnchos.r6g.aggregate.v1",
        "ok": all(v["ok"] for v in active.values()) and sem["ok"],
        "IMPROVED_STATE_OF_ART": False,
        "breakthroughs_registered": registry["count"],
        "sources_verified": "PUBLIC_PORTALS_AND_PENDING_DOI_PINS",
        "baselines_digitally_reproducible_or_structural": True,
        "baselines_digitally_matched_to_published_physical": False,
        "digital_improvements_observed": {
            "R6G-003": r003["MULTIMODAL_ISAC_DIGITAL_IMPROVEMENT"],
            "R6G-005": r005["SIMULATION_IMPROVEMENT_OBSERVED"],
            "R6G-009": r009["SIMULATION_IMPROVEMENT_OBSERVED"],
        },
        "independent_improvements_verified": False,
        "physical_pending": True,
        "product_candidates": [
            {"id": "semantic_ntn_education_mode", "gate": "RESEARCH_ONLY"},
            {"id": "uncertainty_aware_ai_csf_digital", "gate": "CANDIDATE_DIGITAL"},
            {"id": "predictive_radio_dt_policy", "gate": "CANDIDATE_DIGITAL"},
            {"id": "hybrid_spectrum_fabric_policy", "gate": "CANDIDATE_DIGITAL"},
        ],
        "negative_or_no_gain_notes": [
            "AI_CSF without uncertainty can catastrophically degrade under adversarial/shift stresses",
            "Peak-only THz links can score worse on Useful Connectivity Score than lower-rate high-availability paths",
            "FULL_CONTENT_TRANSFER fails hardest under long NTN outage vs LEARNING_STATE_DELTA",
        ],
        "active_packet_status": active,
        "registered_not_active": not_active,
        "packets": {
            "R6G-001": r001,
            "R6G-003": r003,
            "R6G-005": r005,
            "R6G-009": r009,
            "R6G-002": r002,
            "semantic_continuity": sem,
        },
        "tokens": tokens,
        "OPEN": [
            "DOI/PDF pins for many atlas baselines still PENDING",
            "DIGITAL_REPRODUCTION_MATCHED to published physical values generally false (structural only)",
            "Independent digital improvement verification (R5) not claimed this cycle",
            "Physical/SDR/OTA (R6+) PHYSICAL_REPRODUCTION_PENDING",
            "IMPROVED_STATE_OF_ART remains false",
            "Large ns-3/Sionna/DeepMIMO/multi-hour RF deferred",
            "R6G-004/006/007/008/010/011 REGISTERED_NOT_ACTIVE",
        ],
        "deferred_heavy_work": [
            "ns-3 / Sionna / DeepMIMO campaign sweeps",
            "multi-hour RF / THz physical campaigns",
            "extra QEMU",
            "large twin cinematic renders",
        ],
    }
    assert_no_soa(report)
    assert report["IMPROVED_STATE_OF_ART"] is IMPROVED_STATE_OF_ART is False

    if out_dir is not None:
        out_dir = Path(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "R6G_AGGREGATE_RESULT.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        for name, obj in [
            ("R6G001_REGISTRY.json", r001),
            ("R6G003_FR3_ISAC.json", r003),
            ("R6G005_AI_PHY.json", r005),
            ("R6G009_PREDICTIVE_DT.json", r009),
            ("R6G002_SPECTRUM_FABRIC.json", r002),
            ("SEMANTIC_CONTINUITY_NTN_EDU.json", sem),
            ("R6G_TOKEN_TABLE.json", {"tokens": tokens}),
        ]:
            (out_dir / name).write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")
    return report


def main() -> int:
    report = evaluate_r6g(ROOT / "artifacts" / "r6g")
    print("R6G_PASS" if report["ok"] else "R6G_FAIL")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
