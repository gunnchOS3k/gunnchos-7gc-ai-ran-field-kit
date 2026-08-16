"""Aggregate R6G evaluation — portfolio adoption wave + replication suite."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any

from research.r6g.claim_firewall import IMPROVED_STATE_OF_ART, assert_no_soa
from research.r6g.experiments.r6g002_spectrum_fabric import run_r6g002
from research.r6g.experiments.r6g003_fr3_isac import run_r6g003
from research.r6g.experiments.r6g004_multimodal_isac_personal import run_r6g004
from research.r6g.experiments.r6g005_ai_phy import run_r6g005
from research.r6g.experiments.r6g006_cellfree_mimo_contract import run_r6g006
from research.r6g.experiments.r6g007_adaptive_ris_contract import run_r6g007
from research.r6g.experiments.r6g008_semantic_ntn import run_r6g008
from research.r6g.experiments.r6g009_predictive_twin import run_r6g009
from research.r6g.experiments.r6g010_security_pqc_privacy import run_r6g010
from research.r6g.experiments.r6g011_imt2030_harness import run_r6g011
from research.r6g.experiments.semantic_continuity_ntn_education import run_semantic_continuity
from research.r6g.replication.reproduce import run_replication_suite
from research.r6g.replication.verify_independent import verify_from_raw

ROOT = Path(__file__).resolve().parents[2]
REG = ROOT / "research" / "6g_breakthroughs"


def _matrix_row(packet: str, *, status: str, claim_state: str, adoption: str, ladder: list[str], notes: str) -> dict[str, Any]:
    return {
        "packet": packet,
        "status": status,
        "claim_state": claim_state,
        "adoption_package": adoption,
        "ladder_earned": ladder,
        "IMPROVED_STATE_OF_ART": False,
        "notes": notes,
    }


def build_portfolio_matrix(
    *,
    r001: dict,
    r002: dict,
    r003: dict,
    r004: dict,
    r005: dict,
    r006: dict,
    r007: dict,
    r008: dict,
    r009: dict,
    r010: dict,
    r011: dict,
    replication: dict,
) -> dict[str, Any]:
    cand = replication.get("candidates", {})
    adopt = replication.get("adoption_levels", {})
    rows = [
        _matrix_row(
            "R6G-001",
            status=r001["status"],
            claim_state="REGISTERED",
            adoption=adopt.get("R6G-001", "A1_STABLE_REFERENCE_REGISTRY"),
            ladder=["R0", "R1"],
            notes="Full atlas registry; OFFICIAL_VALUE_PENDING where unpinned",
        ),
        _matrix_row(
            "R6G-002",
            status=r002["status"],
            claim_state=r002.get("claim_state", "DIGITALLY_EXECUTED"),
            adoption=adopt.get("R6G-002", "A0_INTERNAL_EXPERIMENT"),
            ladder=r002.get("ladder_earned", ["R0", "R1", "R2"]),
            notes="Seeded spectrum-fabric digital campaign; UCS preregistered; TASK_AWARE can lose",
        ),
        _matrix_row(
            "R6G-003",
            status=r003["status"],
            claim_state=cand.get("R6G-003", {}).get("claim_state", "DIGITAL_IMPROVEMENT_CANDIDATE"),
            adoption=adopt.get("R6G-003", "A1_STABLE_REFERENCE_IMPLEMENTATION"),
            ladder=cand.get("R6G-003", {}).get("ladder_earned", []),
            notes="Preserved from #79; no silent promotion",
        ),
        _matrix_row(
            "R6G-004",
            status=r004["status"],
            claim_state=r004["claim_state"],
            adoption=adopt.get("R6G-004", "A0_INTERNAL_EXPERIMENT"),
            ladder=r004.get("ladder_earned", ["R0", "R1", "R2"]),
            notes="DIGITAL_SYNTHETIC_EXPERIMENT; PHYSICAL_RING=false; real synthetic negatives",
        ),
        _matrix_row(
            "R6G-005",
            status=r005["status"],
            claim_state=cand.get("R6G-005", {}).get("claim_state", "REPLICATION_INCOMPLETE"),
            adoption=adopt.get("R6G-005", "A0_INTERNAL_EXPERIMENT"),
            ladder=cand.get("R6G-005", {}).get("ladder_earned", []),
            notes="Preserved REPLICATION_INCOMPLETE from #79",
        ),
        _matrix_row(
            "R6G-006",
            status=r006["status"],
            claim_state=r006["claim_state"],
            adoption=adopt.get("R6G-006", "A0_INTERNAL_EXPERIMENT"),
            ladder=r006.get("ladder_earned", ["R0", "R1", "R2"]),
            notes="DIGITALLY_EXECUTED R0–R2 seeded cell-free sim; no physical MIMO / SoA claim",
        ),
        _matrix_row(
            "R6G-007",
            status=r007["status"],
            claim_state=r007["claim_state"],
            adoption=adopt.get("R6G-007", "A0_INTERNAL_EXPERIMENT"),
            ladder=r007.get("ladder_earned", ["R0", "R1", "R2"]),
            notes="DIGITALLY_EXECUTED R0–R2 seeded RIS sim; RIS_PURCHASE=false; no SoA claim",
        ),
        _matrix_row(
            "R6G-008",
            status=r008["status"],
            claim_state=r008["claim_state"],
            adoption=adopt.get("R6G-008", "A0_INTERNAL_EXPERIMENT"),
            ladder=r008.get("ladder_earned", ["R0", "R1", "R2"]),
            notes="Controlled-trace semantic NTN with WAIKE payloads; no learning outcomes",
        ),
        _matrix_row(
            "R6G-009",
            status=r009["status"],
            claim_state=cand.get("R6G-009", {}).get("claim_state", "REPLICATION_INCOMPLETE"),
            adoption=adopt.get("R6G-009", "A0_INTERNAL_EXPERIMENT"),
            ladder=cand.get("R6G-009", {}).get("ladder_earned", []),
            notes="Preserved REPLICATION_INCOMPLETE from #79",
        ),
        _matrix_row(
            "R6G-010",
            status=r010["status"],
            claim_state=r010["claim_state"],
            adoption=adopt.get("R6G-010", "A0_INTERNAL_EXPERIMENT"),
            ladder=r010.get("ladder_earned", ["R0", "R1", "R2"]),
            notes="Executed accept/reject security battery; not certification",
        ),
        _matrix_row(
            "R6G-011",
            status=r011["status"],
            claim_state=r011["claim_state"],
            adoption=adopt.get("R6G-011", "A0_INTERNAL_EXPERIMENT"),
            ladder=r011.get("ladder_earned", ["R0", "R1", "R2"]),
            notes="Executable IMT-2030 harness; STANDARD_PENDING; never COMPLIANT",
        ),
    ]
    return {
        "schema": "gunnchos.r6g.portfolio_matrix.v1",
        "wave": "R6G-PORTFOLIO-ADOPTION-002",
        "IMPROVED_STATE_OF_ART": False,
        "rows": rows,
        "preserved_claim_states": {
            "R6G-003": "DIGITAL_IMPROVEMENT_CANDIDATE",
            "R6G-005": "REPLICATION_INCOMPLETE",
            "R6G-009": "REPLICATION_INCOMPLETE",
        },
    }


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
        "official_value_pending_policy": "OFFICIAL_VALUE_PENDING for unpinned baselines",
    }
    r003 = run_r6g003()
    r004 = run_r6g004()
    r005 = run_r6g005()
    r006 = run_r6g006()
    r007 = run_r6g007()
    r008 = run_r6g008()
    r009 = run_r6g009()
    r002 = run_r6g002()
    r010 = run_r6g010()
    r011 = run_r6g011()
    sem = run_semantic_continuity()

    rep_dir = (Path(out_dir) / "replication") if out_dir is not None else (ROOT / "artifacts" / "r6g" / "replication")
    replication = run_replication_suite(rep_dir)
    independent = verify_from_raw(rep_dir)
    # Reload suite after verifier upgrades R6 flags / tokens
    replication = json.loads((rep_dir / "R6G_REPLICATION_SUITE.json").read_text(encoding="utf-8"))

    active = {
        "R6G-001": {"status": "COMPLETE_DIGITAL_REGISTRY", "ok": r001["ok"]},
        "R6G-003": {"status": r003["status"], "ok": r003["ok"], "MULTIMODAL_ISAC_DIGITAL_IMPROVEMENT": r003["MULTIMODAL_ISAC_DIGITAL_IMPROVEMENT"]},
        "R6G-005": {"status": r005["status"], "ok": r005["ok"], "HYPOTHESIS_SUPPORTED_DIGITALLY": r005["HYPOTHESIS_SUPPORTED_DIGITALLY"]},
        "R6G-009": {"status": r009["status"], "ok": r009["ok"], "HYPOTHESIS_SUPPORTED_DIGITALLY": r009["HYPOTHESIS_SUPPORTED_DIGITALLY"]},
        "R6G-002": {"status": r002["status"], "ok": r002["ok"]},
        "R6G-004": {"status": r004["status"], "ok": r004["ok"]},
        "R6G-006": {"status": r006["status"], "ok": r006["ok"]},
        "R6G-007": {"status": r007["status"], "ok": r007["ok"]},
        "R6G-008": {"status": r008["status"], "ok": r008["ok"]},
        "R6G-010": {"status": r010["status"], "ok": r010["ok"]},
        "R6G-011": {"status": r011["status"], "ok": r011["ok"]},
    }
    modeled_contracts = {
        # Retained key for consumers; packets are DIGITALLY_EXECUTED as of STREAM-C-PKT-001.
        "R6G-006": {"status": r006["status"], "ok": r006["ok"], "prior": "MODELED_CONTRACT_ONLY"},
        "R6G-007": {"status": r007["status"], "ok": r007["ok"], "prior": "MODELED_CONTRACT_ONLY"},
    }
    not_active = [p["work_packet"] for p in backlog["packets"] if p["status"] == "REGISTERED_NOT_ACTIVE"]

    matrix = build_portfolio_matrix(
        r001=r001, r002=r002, r003=r003, r004=r004, r005=r005,
        r006=r006, r007=r007, r008=r008, r009=r009, r010=r010, r011=r011,
        replication=replication,
    )

    tokens = {
        "R6G_REGISTRY_COMPLETE": r001["ok"],
        "MULTIMODAL_ISAC_DIGITAL_IMPROVEMENT": bool(r003["MULTIMODAL_ISAC_DIGITAL_IMPROVEMENT"]),
        "AI_PHY_UNCERTAINTY_AWARE_DIGITAL": bool(r005["HYPOTHESIS_SUPPORTED_DIGITALLY"]),
        "PREDICTIVE_RADIO_DT_DIGITAL": bool(r009["HYPOTHESIS_SUPPORTED_DIGITALLY"]),
        # Earned only when packets actually execute digital campaigns
        "HYBRID_SPECTRUM_FABRIC_DIGITAL": bool(r002.get("HYBRID_SPECTRUM_FABRIC_DIGITAL")),
        "SEMANTIC_CONTINUITY_NTN_EDU_DIGITAL": bool(r008.get("SEMANTIC_CONTINUITY_NTN_EDU_DIGITAL")),
        "MULTIMODAL_ISAC_PERSONAL_DIGITAL": bool(r004.get("MULTIMODAL_ISAC_PERSONAL_DIGITAL")),
        "SECURITY_PQC_PRIVACY_HOOKS_DIGITAL": bool(r010.get("SECURITY_PQC_PRIVACY_HOOKS_DIGITAL")),
        "IMT2030_HARNESS_DIGITAL": bool(r011.get("IMT2030_HARNESS_DIGITAL")),
        "R6G_DIGITAL_REPLICATION_PASS": bool(replication["tokens"].get("R6G_DIGITAL_REPLICATION_PASS")),
        "R6G_MULTI_SEED_REPRODUCED": bool(replication["tokens"].get("R6G_MULTI_SEED_REPRODUCED")),
        "R6G_FALSIFICATION_DOCUMENTED": bool(replication["tokens"].get("R6G_FALSIFICATION_DOCUMENTED")),
        "R6G_ABLATIONS_DOCUMENTED": bool(replication["tokens"].get("R6G_ABLATIONS_DOCUMENTED")),
        "R6G_INDEPENDENT_VERIFIER_PASS": bool(independent.get("R6G_INDEPENDENT_VERIFIER_PASS")),
        "R6G_ABLATIONS_PARTIAL": bool(replication.get("tokens", {}).get("R6G_ABLATIONS_PARTIAL")),
        "IMPROVED_STATE_OF_ART": False,
        "6G_BREAKTHROUGH_PASS": None,
        "BREAKTHROUGH_PROVEN": False,
        "PHYSICAL_REPRODUCTION_PENDING": True,
        "EXTERNAL_REPRODUCTION_PENDING": True,
        "COMPARABLE_EVIDENCE_PENDING": True,
        "PEER_REVIEWED": False,
        "STANDARDIZED_6G": False,
        "COMPLIANT": False,
        "PHYSICAL_RING": False,
    }

    open_items = [
        "DOI/PDF pins for many atlas baselines still PENDING",
        "DIGITAL_REPRODUCTION_MATCHED to published physical values generally false (structural only)",
        "Independent digital improvement verification (R5/R6 external) not claimed this cycle",
        "Physical/SDR/OTA (R6+) PHYSICAL_REPRODUCTION_PENDING",
        "IMPROVED_STATE_OF_ART remains false",
        "Large ns-3/Sionna/DeepMIMO/multi-hour RF deferred (Product-Use may own QEMU)",
        "R6G-006/007 DIGITALLY_EXECUTED (R0–R2) — no physical / purchase / SoA claim",
        "R6G-002/008/010 DIGITALLY_EXECUTED; 011 DIGITALLY_EXECUTED_HARNESS; 004 DIGITAL_SYNTHETIC_EXPERIMENT",
        "Dual-tree disposition: artifacts/r6g authoritative; stable_seed fixes PYTHONHASHSEED drift",
        "Registry numeric headlines scrubbed to OFFICIAL_VALUE_PENDING until distance+bandwidth pinned",
        "EXTERNAL_REPRODUCTION_PENDING / PHYSICAL_REPRODUCTION_PENDING",
        "R6G-003 DIGITAL_IMPROVEMENT_CANDIDATE preserved; 005/009 REPLICATION_INCOMPLETE preserved",
        "Never STANDARDIZED_6G/COMPLIANT without official evidence",
        "WAIKE case studies do not count as scientific validation",
        "No 11 new research repos (NEW_6G_RESEARCH_REPO_CREATION=FORBIDDEN_BY_DEFAULT)",
        "STREAM-C-PKT-001: deepened 003/005/009 seeds; 006/007 exited MODELED_CONTRACT_ONLY",
    ]

    report = {
        "schema": "gunnchos.r6g.aggregate.v1",
        "wave": "R6G-PORTFOLIO-ADOPTION-002",
        "ok": all(v["ok"] for v in active.values()) and all(v["ok"] for v in modeled_contracts.values()) and sem["ok"],
        "IMPROVED_STATE_OF_ART": False,
        "breakthroughs_registered": registry["count"],
        "sources_verified": "PUBLIC_PORTALS_AND_PENDING_DOI_PINS",
        "baselines_digitally_reproducible_or_structural": True,
        "baselines_digitally_matched_to_published_physical": False,
        "digital_improvements_observed": {
            "R6G-003": r003["MULTIMODAL_ISAC_DIGITAL_IMPROVEMENT"],
            "R6G-004": bool(r004.get("MULTIMODAL_ISAC_PERSONAL_DIGITAL_IMPROVEMENT")),
            "R6G-005": r005["SIMULATION_IMPROVEMENT_OBSERVED"],
            "R6G-009": r009["SIMULATION_IMPROVEMENT_OBSERVED"],
        },
        "independent_improvements_verified": False,
        "independent_verifier_recalc_pass": bool(independent.get("ok")),
        "independent_verifier": independent,
        "replication": {
            "negative_result_count": replication.get("negative_result_count"),
            "adoption_levels": replication.get("adoption_levels"),
            "candidates": {
                k: {
                    "claim_state": v.get("claim_state"),
                    "ladder_earned": v.get("ladder_earned"),
                    "IMPROVED_STATE_OF_ART": False,
                }
                for k, v in replication.get("candidates", {}).items()
            },
            "tokens": replication.get("tokens"),
        },
        "portfolio_matrix": matrix,
        "physical_pending": True,
        "product_candidates": [
            {"id": "semantic_ntn_education_mode", "gate": "RESEARCH_ONLY"},
            {"id": "uncertainty_aware_ai_csf_digital", "gate": "CANDIDATE_DIGITAL"},
            {"id": "predictive_radio_dt_policy", "gate": "CANDIDATE_DIGITAL"},
            {"id": "hybrid_spectrum_fabric_policy", "gate": "CANDIDATE_DIGITAL"},
            {"id": "security_pqc_privacy_hooks", "gate": "EXECUTED_DIGITAL_TESTS"},
            {"id": "imt2030_harness_map", "gate": "EXECUTABLE_HARNESS"},
        ],
        "negative_or_no_gain_notes": [
            "AI_CSF without uncertainty can catastrophically degrade under adversarial/shift stresses",
            "Peak-only THz links can score worse on Useful Connectivity Score than lower-rate high-availability paths",
            "TASK_AWARE spectrum policy loses under blockage/weather vs ROBUST_TASK_AWARE",
            "FULL_SYNC fails hardest under long NTN outage; SEMANTIC_SYNC can drop necessary state",
            "R6G-003: vision spoof + over-trust fusion → multimodal RMSE worse than RF-only",
            "R6G-004: camera spoof / ring bias / privacy-cost negatives on synthetic personal sensing",
            "R6G-005: uncertainty-aware CSF shows no throughput gain vs conventional on IID CSI",
            "R6G-009: predictive belief worse than current at 100 ms horizon and under jump/burst dynamics",
            "R6G-006: RZF can lose to MRT under fronthaul quantization / AP dropout",
            "R6G-007: adaptive RIS phases can lose under element failure / mobility mismatch / 2-bit quant",
            "R6G-010: overclaim trap collapses when sensing privacy is ignored",
        ],
        "documented_negative_experiments": {
            "R6G-002": r002.get("documented_negative_or_no_gain", []),
            "R6G-003": r003.get("documented_negative_or_no_gain", []),
            "R6G-004": r004.get("documented_negative_or_no_gain", []),
            "R6G-005": r005.get("documented_negative_or_no_gain", []),
            "R6G-008": r008.get("documented_negative_or_no_gain", []),
            "R6G-009": r009.get("documented_negative_or_no_gain", []),
            "R6G-006": r006.get("documented_negative_or_no_gain", []),
            "R6G-007": r007.get("documented_negative_or_no_gain", []),
            "R6G-010": r010.get("documented_negative_or_no_gain", []),
        },
        "falsifiability": {
            "R6G-003": bool(r003.get("falsifiable")),
            "R6G-005": bool(r005.get("falsifiable")),
            "R6G-009": bool(r009.get("falsifiable")),
            "R6G-006": len(r006.get("documented_negative_or_no_gain", [])) >= 1,
            "R6G-007": len(r007.get("documented_negative_or_no_gain", [])) >= 1,
            "R6G-002": len(r002.get("documented_negative_or_no_gain", [])) >= 1,
            "R6G-004": len(r004.get("documented_negative_or_no_gain", [])) >= 1,
            "R6G-008": len(r008.get("documented_negative_or_no_gain", [])) >= 1,
            "R6G-010": bool(r010.get("falsification", {}).get("overclaim_trap_scores_worse_when_privacy_collapses")),
        },
        "dual_tree_disposition": {
            "authoritative": "artifacts/r6g",
            "mirror": "artifacts/net_sec_rc001/r6g",
            "root_cause_fixed": "PYTHONHASHSEED-unstable builtin hash() replaced with research.r6g.metrics.stable_seed",
            "tolerance_policy": "none — bit-stable floats expected after regenerate",
        },
        "naked_numeric_headline_count": sum(
            1 for b in registry.get("breakthroughs", []) if b.get("headline_numeric_claim") is True
        ),
        "active_packet_status": active,
        "modeled_contract_status": modeled_contracts,
        "registered_not_active": not_active,
        "packets": {
            "R6G-001": r001,
            "R6G-002": r002,
            "R6G-003": r003,
            "R6G-004": r004,
            "R6G-005": r005,
            "R6G-006": r006,
            "R6G-007": r007,
            "R6G-008": r008,
            "R6G-009": r009,
            "R6G-010": r010,
            "R6G-011": r011,
            "semantic_continuity": sem,
        },
        "tokens": tokens,
        "OPEN": open_items,
        "deferred_heavy_work": [
            "ns-3 / Sionna / DeepMIMO campaign sweeps",
            "multi-hour RF / THz physical campaigns",
            "extra QEMU (Product-Use may own)",
            "large twin cinematic renders",
            "physical RIS / THz purchase",
        ],
    }
    assert_no_soa(report)
    assert report["IMPROVED_STATE_OF_ART"] is IMPROVED_STATE_OF_ART is False
    assert report["tokens"]["STANDARDIZED_6G"] is False
    assert report["tokens"]["PHYSICAL_RING"] is False

    # Preserve #79 claim states on replication candidates
    assert report["replication"]["candidates"]["R6G-003"]["claim_state"] == "DIGITAL_IMPROVEMENT_CANDIDATE"
    assert report["replication"]["candidates"]["R6G-005"]["claim_state"] == "REPLICATION_INCOMPLETE"
    assert report["replication"]["candidates"]["R6G-009"]["claim_state"] == "REPLICATION_INCOMPLETE"

    if out_dir is not None:
        out_dir = Path(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "R6G_AGGREGATE_RESULT.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        (out_dir / "R6G_PORTFOLIO_MATRIX.json").write_text(json.dumps(matrix, indent=2) + "\n", encoding="utf-8")
        (REG / "R6G_PORTFOLIO_MATRIX.json").write_text(json.dumps(matrix, indent=2) + "\n", encoding="utf-8")
        open_md = "# R6G OPEN — Portfolio Adoption 002\n\n" + "\n".join(f"- {x}" for x in open_items) + "\n"
        (out_dir / "OPEN.md").write_text(open_md, encoding="utf-8")
        for name, obj in [
            ("R6G001_REGISTRY.json", r001),
            ("R6G002_SPECTRUM_FABRIC.json", r002),
            ("R6G003_FR3_ISAC.json", r003),
            ("R6G004_PERSONAL_ISAC.json", r004),
            ("R6G005_AI_PHY.json", r005),
            ("R6G006_CELLFREE_CONTRACT.json", r006),
            ("R6G007_RIS_CONTRACT.json", r007),
            ("R6G008_SEMANTIC_NTN.json", r008),
            ("R6G009_PREDICTIVE_DT.json", r009),
            ("R6G010_SECURITY_PQC_PRIVACY.json", r010),
            ("R6G011_IMT2030_HARNESS.json", r011),
            ("SEMANTIC_CONTINUITY_NTN_EDU.json", sem),
            ("R6G_TOKEN_TABLE.json", {"tokens": tokens}),
            ("R6G_CLAIM_STATES.json", {
                "IMPROVED_STATE_OF_ART": False,
                "BREAKTHROUGH_PROVEN": False,
                "STANDARDIZED_6G": False,
                "candidates": report["replication"]["candidates"],
                "supporting": {
                    "R6G-002": r002["claim_state"],
                    "R6G-004": r004["claim_state"],
                    "R6G-006": r006["claim_state"],
                    "R6G-007": r007["claim_state"],
                    "R6G-008": r008["claim_state"],
                    "R6G-010": r010["claim_state"],
                    "R6G-011": r011["claim_state"],
                },
            }),
        ]:
            (out_dir / name).write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")
    return report


def main() -> int:
    report = evaluate_r6g(ROOT / "artifacts" / "r6g")
    print("R6G_PASS" if report["ok"] else "R6G_FAIL")
    print("SoA", report["IMPROVED_STATE_OF_ART"])
    print("wave", report["wave"])
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
