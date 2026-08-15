"""Multi-seed digital replication suite — falsification-first, honest ladder caps."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from research.r6g.claim_firewall import assert_no_soa
from research.r6g.experiments.r6g002_spectrum_fabric import run_r6g002
from research.r6g.experiments.r6g003_fr3_isac import NEGATIVE_CONFIGS, run_config
from research.r6g.experiments.r6g005_ai_phy import run_r6g005
from research.r6g.experiments.r6g009_predictive_twin import run_r6g009
from research.r6g.experiments.semantic_continuity_ntn_education import run_semantic_continuity
from research.r6g.replication.ablations import ablate_r6g003, ablate_r6g005, ablate_r6g009
from research.r6g.replication.ladder import CLAIM_STATES_ALLOWED, LADDER, contiguous_earned
from research.r6g.replication.seed_registry import SEED_REGISTRY
from research.r6g.replication.stats import summarize, win_rate

ROOT = Path(__file__).resolve().parents[3]

# Same-PR arithmetic verifier is NOT external independence (R6).
SAME_PR_VERIFIER_COUNTS_AS_R6 = False


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _write_json(path: Path, obj: Any) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(obj, indent=2, sort_keys=True) + "\n").encode("utf-8")
    path.write_bytes(raw)
    return _sha256_bytes(raw)


def _values_vary(vals: list[float], *, min_unique: int = 2) -> bool:
    rounded = {round(v, 4) for v in vals}
    return len(rounded) >= min_unique


def _claim_state(candidate: str, *, multi_seed_ok: bool, negatives_ok: bool, ablations_ok: bool) -> str:
    """Honest claim states. PROMISING_DIGITAL requires external R6 — never same-PR."""
    if candidate == "R6G-003":
        if multi_seed_ok and negatives_ok and ablations_ok:
            return "DIGITAL_IMPROVEMENT_CANDIDATE"
        if negatives_ok and not multi_seed_ok:
            return "NEGATIVE_RESULT_DOCUMENTED"
        return "REPLICATION_INCOMPLETE"
    # 005/009: publish real multi-seed evidence but claim stays incomplete until
    # external protocol review awards R3+ (FAIL remediation: no PROMISING / not DIC yet).
    return "REPLICATION_INCOMPLETE"


def _empty_ladder(**flags: bool) -> dict[str, bool]:
    base = {f"R{i}": False for i in range(10)}
    base.update(flags)
    # R6+ never auto-set here
    base["R6"] = False
    base["R7"] = False
    base["R8"] = False
    base["R9"] = False
    return base


def _replicate_r6g003(raw_dir: Path) -> dict[str, Any]:
    seeds = SEED_REGISTRY["candidates"]["R6G-003"]
    primary_rows = []
    for seed in seeds["primary_seeds"]:
        cfg = {
            "config_id": f"rep_primary_s{seed}",
            "seed": seed,
            "vision_spoof_rate": 0.0 if seed % 3 else 0.02,
            "fusion_trust_vision": 0.28,
        }
        row = run_config(cfg)
        digest = _write_json(raw_dir / "R6G-003" / f"primary_s{seed}.json", row)
        primary_rows.append({
            "seed": seed,
            "rf_all_vs_rf_only_delta_m": row["rf_all_vs_rf_only_delta_m"],
            "win": row["rf_all_vs_rf_only_delta_m"] < 0.0,
            "sha256": digest,
            "RF_ONLY": row["modality_matrix"]["RF_ONLY"]["position_RMSE"],
            "RF_ALL": row["modality_matrix"]["RF_ALL_MODALITIES"]["position_RMSE"],
        })

    neg_rows = []
    for seed in seeds["negative_seeds"]:
        cfg = {
            "config_id": f"rep_neg_s{seed}",
            "seed": seed,
            "adversarial": True,
            "vision_spoof_rate": 0.55 + (seed % 10) * 0.02,
            "vision_spoof_mag_m": 3.0,
            "fusion_trust_vision": 0.75,
            "rf_noise_m": 0.22,
        }
        row = run_config(cfg)
        digest = _write_json(raw_dir / "R6G-003" / f"neg_s{seed}.json", row)
        neg_rows.append({
            "seed": seed,
            "rf_all_vs_rf_only_delta_m": row["rf_all_vs_rf_only_delta_m"],
            "multimodal_worse": row["rf_all_vs_rf_only_delta_m"] > 0.0,
            "sha256": digest,
        })

    for cfg in NEGATIVE_CONFIGS:
        row = run_config(cfg)
        # Canonical negatives under distinct names (not neg_s*) to avoid verifier double-count
        _write_json(raw_dir / "R6G-003" / f"canonical_{cfg['config_id']}.json", row)

    # Execute robustness_seeds (lightweight noise/spoof sweep)
    robustness_rows = []
    for seed in seeds["robustness_seeds"]:
        cfg = {
            "config_id": f"rob_s{seed}",
            "seed": seed,
            "rf_noise_m": 0.45,
            "vision_spoof_rate": 0.15,
            "fusion_trust_vision": 0.40,
        }
        row = run_config(cfg)
        digest = _write_json(raw_dir / "R6G-003" / f"rob_s{seed}.json", row)
        robustness_rows.append({
            "seed": seed,
            "rf_all_vs_rf_only_delta_m": row["rf_all_vs_rf_only_delta_m"],
            "sha256": digest,
        })

    deltas = [r["rf_all_vs_rf_only_delta_m"] for r in primary_rows]
    wins = [r["win"] for r in primary_rows]
    metrics_vary = _values_vary(deltas) and _values_vary([r["RF_ONLY"] for r in primary_rows])
    multi_ok = (
        metrics_vary
        and win_rate(wins)["win_rate"] >= 0.75
        and (summarize(deltas)["mean"] or 0) < 0
    )
    neg_ok = any(r["multimodal_worse"] for r in neg_rows)
    ablations = ablate_r6g003(seeds["ablation_seeds"])
    _write_json(raw_dir / "R6G-003" / "ablation.json", ablations)
    abl_ok = bool(ablations.get("ablation_ok"))

    ladder_flags = _empty_ladder(
        R0=True, R1=True, R2=True,
        R3=multi_ok, R4=neg_ok, R5=abl_ok,
    )
    claim = _claim_state("R6G-003", multi_seed_ok=multi_ok, negatives_ok=neg_ok, ablations_ok=abl_ok)
    assert claim in CLAIM_STATES_ALLOWED
    assert claim != "PROMISING_DIGITAL"

    return {
        "candidate": "R6G-003",
        "title": "FR3 multimodal ISAC digital fusion",
        "primary_runs": primary_rows,
        "negative_runs": neg_rows,
        "robustness_runs": robustness_rows,
        "primary_delta_summary": summarize(deltas),
        "primary_win_rate": win_rate(wins),
        "metrics_vary_across_seeds": metrics_vary,
        "negative_controls_observed": neg_ok,
        "ablation": ablations,
        "ladder_flags": ladder_flags,
        "ladder_earned": contiguous_earned(ladder_flags),
        "ladder_cap_note": "R6+ requires external independent path; same-PR verifier does not earn R6",
        "claim_state": claim,
        "IMPROVED_STATE_OF_ART": False,
        "DIGITAL_REPRODUCTION_MATCHED_TO_PHYSICAL": False,
    }


def _replicate_r6g005(raw_dir: Path) -> dict[str, Any]:
    seeds = SEED_REGISTRY["candidates"]["R6G-005"]
    seed_rows = []
    neg_notes_all: list[dict[str, Any]] = []
    primary_support_flags = []
    for seed in seeds["primary_seeds"]:
        report = run_r6g005(seed=seed)
        digest = _write_json(raw_dir / "R6G-005" / f"seed_{seed}.json", report)
        adv_delta = round(
            report["results"]["AI_CSF"]["adversarial_csi"]["failure_rate"]
            - report["results"]["AI_CSF_UNCERTAINTY_AWARE"]["adversarial_csi"]["failure_rate"],
            4,
        )
        seed_rows.append({
            "seed": seed,
            "sha256": digest,
            "aware_vs_naive_adversarial_fail_delta": adv_delta,
            "id_aware_throughput": report["results"]["AI_CSF_UNCERTAINTY_AWARE"]["in_distribution"]["throughput_norm"],
            "id_conventional_throughput": report["results"]["CONVENTIONAL_CSI"]["in_distribution"]["throughput_norm"],
            "primary_support_aware_vs_naive": report.get("primary_support_aware_vs_naive"),
            "HYPOTHESIS_SUPPORTED_DIGITALLY": report.get("HYPOTHESIS_SUPPORTED_DIGITALLY"),
        })
        primary_support_flags.append(bool(report.get("primary_support_aware_vs_naive")))
        for n in report.get("documented_negative_or_no_gain", []):
            neg_notes_all.append({"seed": seed, **n})

    # Representative full report = first primary seed (for aggregate consumers)
    full = run_r6g005(seed=seeds["primary_seeds"][0])
    _write_json(raw_dir / "R6G-005" / "full_report.json", full)

    robustness_rows = []
    for seed in seeds["robustness_seeds"]:
        report = run_r6g005(seed=seed)
        digest = _write_json(raw_dir / "R6G-005" / f"rob_s{seed}.json", report)
        robustness_rows.append({
            "seed": seed,
            "sha256": digest,
            "adv_naive_fail": report["results"]["AI_CSF"]["adversarial_csi"]["failure_rate"],
            "adv_aware_fail": report["results"]["AI_CSF_UNCERTAINTY_AWARE"]["adversarial_csi"]["failure_rate"],
        })

    deltas = [r["aware_vs_naive_adversarial_fail_delta"] for r in seed_rows]
    thr = [r["id_aware_throughput"] for r in seed_rows]
    metrics_vary = _values_vary(deltas) and _values_vary(thr)
    multi_ok_evidence = metrics_vary and sum(primary_support_flags) / max(1, len(primary_support_flags)) >= 0.75
    neg_ok = len(neg_notes_all) >= 1
    ablations = ablate_r6g005(seeds["ablation_seeds"])
    _write_json(raw_dir / "R6G-005" / "ablation.json", ablations)
    abl_ok_evidence = bool(ablations.get("ablation_ok"))

    # Ladder cap R0–R2 until external protocol review awards R3+ (FAIL remediation).
    # Real seed-varying evidence is published in seed_rows / metrics_vary_across_seeds.
    ladder_flags = _empty_ladder(
        R0=True, R1=True, R2=True,
        R3=False, R4=neg_ok, R5=False,
    )
    # R4 alone does not climb past R2 gap — contiguous stop at R2
    # Keep falsification evidence on flags for dashboard, but earned stops at R2:
    # Use R4 only if contiguous — so set R4 False on ladder_earned path; store separately
    claim = _claim_state("R6G-005", multi_seed_ok=False, negatives_ok=neg_ok, ablations_ok=False)
    assert claim == "REPLICATION_INCOMPLETE"

    return {
        "candidate": "R6G-005",
        "title": "Uncertainty-aware AI CSF digital",
        "seed_rows": seed_rows,
        "robustness_runs": robustness_rows,
        "metrics_vary_across_seeds": metrics_vary,
        "multi_seed_evidence_ready": multi_ok_evidence,
        "ablation_evidence_ready": abl_ok_evidence,
        "r3_r5_deferred": "PENDING_EXTERNAL_PROTOCOL_REVIEW",
        "documented_negative_or_no_gain": neg_notes_all[:8],
        "ablation": ablations,
        "falsification_evidence": neg_ok,
        "ladder_flags": ladder_flags,
        "ladder_earned": contiguous_earned(ladder_flags),
        "ladder_cap_note": (
            "R0–R2 this cycle; real multi-seed evidence published but R3–R5 not awarded "
            "until external protocol review. R6 requires external independent path."
        ),
        "claim_state": claim,
        "IMPROVED_STATE_OF_ART": False,
        "beats_nokia_qualcomm_ota": False,
    }


def _replicate_r6g009(raw_dir: Path) -> dict[str, Any]:
    seeds = SEED_REGISTRY["candidates"]["R6G-009"]
    seed_rows = []
    neg_notes_all: list[dict[str, Any]] = []
    moderate_flags = []
    for seed in seeds["primary_seeds"]:
        report = run_r6g009(seed=seed)
        digest = _write_json(raw_dir / "R6G-009" / f"seed_{seed}.json", report)
        g = report["delay_grid_ms"]["25"]
        seed_rows.append({
            "seed": seed,
            "sha256": digest,
            "predictive_regret_25ms": g["PREDICTIVE_BELIEF_STATE"]["policy_regret"],
            "current_regret_25ms": g["CURRENT_STATE_ONLY"]["policy_regret"],
            "win_25ms": g["PREDICTIVE_BELIEF_STATE"]["policy_regret"] < g["CURRENT_STATE_ONLY"]["policy_regret"],
            "primary_moderate_delay_improvement": report.get("primary_moderate_delay_improvement"),
        })
        moderate_flags.append(bool(report.get("primary_moderate_delay_improvement")))
        for n in report.get("documented_negative_or_no_gain", []):
            neg_notes_all.append({"seed": seed, **n})

    full = run_r6g009(seed=seeds["primary_seeds"][0])
    _write_json(raw_dir / "R6G-009" / "full_report.json", full)

    robustness_rows = []
    for seed in seeds["robustness_seeds"]:
        report = run_r6g009(seed=seed)
        digest = _write_json(raw_dir / "R6G-009" / f"rob_s{seed}.json", report)
        g100 = report["delay_grid_ms"]["100"]
        robustness_rows.append({
            "seed": seed,
            "sha256": digest,
            "pred100": g100["PREDICTIVE_BELIEF_STATE"]["policy_regret"],
            "cur100": g100["CURRENT_STATE_ONLY"]["policy_regret"],
        })

    pred25 = [r["predictive_regret_25ms"] for r in seed_rows]
    metrics_vary = _values_vary(pred25) and _values_vary([r["current_regret_25ms"] for r in seed_rows])
    multi_ok_evidence = metrics_vary and sum(moderate_flags) / max(1, len(moderate_flags)) >= 0.5
    neg_ok = len(neg_notes_all) >= 1
    ablations = ablate_r6g009(seeds["ablation_seeds"])
    _write_json(raw_dir / "R6G-009" / "ablation.json", ablations)
    abl_ok_evidence = bool(ablations.get("ablation_ok"))

    # Ladder cap R0–R2 until external protocol review awards R3+ (FAIL remediation).
    ladder_flags = _empty_ladder(
        R0=True, R1=True, R2=True,
        R3=False, R4=False, R5=False,
    )
    claim = _claim_state("R6G-009", multi_seed_ok=False, negatives_ok=neg_ok, ablations_ok=False)
    assert claim == "REPLICATION_INCOMPLETE"

    return {
        "candidate": "R6G-009",
        "title": "Predictive belief-state radio twin digital",
        "seed_rows": seed_rows,
        "robustness_runs": robustness_rows,
        "metrics_vary_across_seeds": metrics_vary,
        "multi_seed_evidence_ready": multi_ok_evidence,
        "ablation_evidence_ready": abl_ok_evidence,
        "r3_r5_deferred": "PENDING_EXTERNAL_PROTOCOL_REVIEW",
        "falsification_evidence": neg_ok,
        "documented_negative_or_no_gain": neg_notes_all[:8],
        "ablation": ablations,
        "ladder_flags": ladder_flags,
        "ladder_earned": contiguous_earned(ladder_flags),
        "ladder_cap_note": (
            "R0–R2 this cycle; real multi-seed evidence published but R3–R5 not awarded "
            "until external protocol review. R6 requires external independent path."
        ),
        "claim_state": claim,
        "IMPROVED_STATE_OF_ART": False,
    }


def _collect_negatives(c003: dict, c005: dict, c009: dict) -> list[dict[str, Any]]:
    """Real negatives only (003/005/009). Construction stubs live in illustrative list."""
    out: list[dict[str, Any]] = []
    for r in c003.get("negative_runs", []):
        if r.get("multimodal_worse"):
            out.append({
                "packet": "R6G-003",
                "experiment": f"rep_neg_s{r['seed']}",
                "result": "MULTIMODAL_WORSE_THAN_RF_ONLY",
                "delta_m": r["rf_all_vs_rf_only_delta_m"],
                "preserved": True,
                "ILLUSTRATIVE": False,
            })
    for n in c005.get("documented_negative_or_no_gain", []):
        out.append({"packet": "R6G-005", **n, "preserved": True, "ILLUSTRATIVE": False})
    for n in c009.get("documented_negative_or_no_gain", []):
        out.append({"packet": "R6G-009", **n, "preserved": True, "ILLUSTRATIVE": False})
    return out


def _illustrative_negatives() -> list[dict[str, Any]]:
    """Construction-stub negatives — do not count toward real negative_result_count."""
    return [
        {
            "packet": "R6G-002",
            "experiment": "peaky_vs_useful_connectivity",
            "result": "PEAK_RATE_OPTIMIZER_WORSE_UCS",
            "reason": "Illustrative UCS sketch — not a falsifiable digital campaign",
            "ILLUSTRATIVE": True,
            "counts_toward_real_negatives": False,
        },
        {
            "packet": "R6G-008",
            "experiment": "full_content_long_outage",
            "result": "FULL_SYNC_FAILS_UNDER_LONG_OUTAGE",
            "reason": "Lookup-table sketch only — not replication-ladder evidence",
            "ILLUSTRATIVE": True,
            "counts_toward_real_negatives": False,
        },
    ]

def _dashboard_row(c: dict[str, Any], *, adoption: str) -> dict[str, Any]:
    flags = c.get("ladder_flags", {})
    return {
        "packet": c["candidate"],
        "baseline_registered": flags.get("R0", False),
        "baseline_reproduced": flags.get("R3", False),
        "multi_seed": flags.get("R3", False),
        "falsification": flags.get("R4", False),
        "negative_controls": flags.get("R4", False),
        "ablation": flags.get("R5", False),
        "robustness": "EXECUTED_LIGHTWEIGHT" if c.get("robustness_runs") else "NOT_EXECUTED",
        "clean_checkout": False,
        "independent_verify": False,  # same-PR never counts
        "integration": False,
        "adoption_package": adoption,
        "external_reproduction": False,
        "physical_validation": False,
        "paper_status": "NOT_SUBMITTED",
        "standard_mapping": "STANDARD_PENDING_WHERE_UNFINALIZED",
        "claim_state": c.get("claim_state"),
        "IMPROVED_STATE_OF_ART": False,
    }


def run_replication_suite(out_dir: Path | None = None) -> dict[str, Any]:
    out = Path(out_dir) if out_dir else (ROOT / "artifacts" / "r6g" / "replication")
    raw_dir = out / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    c003 = _replicate_r6g003(raw_dir)
    c005 = _replicate_r6g005(raw_dir)
    c009 = _replicate_r6g009(raw_dir)
    r002 = run_r6g002()
    sem = run_semantic_continuity()
    _write_json(raw_dir / "R6G-002" / "report.json", r002)
    _write_json(raw_dir / "R6G-008" / "semantic_continuity.json", sem)

    negatives = _collect_negatives(c003, c005, c009)
    illustrative = _illustrative_negatives()
    neg_doc = {
        "schema": "gunnchos.r6g.negative_results.v1",
        "as_of": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "IMPROVED_STATE_OF_ART": False,
        "note": "Real negatives define the operating envelope; illustrative stubs are separate.",
        "count": len(negatives),
        "results": negatives,
        "illustrative_count": len(illustrative),
        "illustrative_results": illustrative,
    }
    _write_json(out / "R6G_NEGATIVE_RESULTS.json", neg_doc)
    _write_json(ROOT / "research" / "6g_breakthroughs" / "R6G_NEGATIVE_RESULTS.json", neg_doc)

    adoption = {
        "R6G-001": "A1_STABLE_REFERENCE_REGISTRY",
        "R6G-002": "A0_INTERNAL_EXPERIMENT",
        "R6G-003": (
            "A1_STABLE_REFERENCE_IMPLEMENTATION"
            if c003["claim_state"] == "DIGITAL_IMPROVEMENT_CANDIDATE"
            else "A0_INTERNAL_EXPERIMENT"
        ),
        "R6G-004": "A0_INTERNAL_EXPERIMENT",
        "R6G-005": "A0_INTERNAL_EXPERIMENT",  # incomplete until claim upgrades
        "R6G-006": "A0_STAGED_MODELED_CONTRACT",
        "R6G-007": "A0_STAGED_MODELED_CONTRACT",
        "R6G-008": "A0_INTERNAL_EXPERIMENT",
        "R6G-009": "A0_INTERNAL_EXPERIMENT",
        "R6G-010": "A0_INTERNAL_EXPERIMENT",
        "R6G-011": "A0_INTERNAL_EXPERIMENT",
        "levels_do_not_skip": True,
        "A2_plus": "NOT_CLAIMED_THIS_CYCLE",
    }
    if c005["claim_state"] == "DIGITAL_IMPROVEMENT_CANDIDATE":
        adoption["R6G-005"] = "A1_STABLE_REFERENCE_IMPLEMENTATION"
    if c009["claim_state"] == "DIGITAL_IMPROVEMENT_CANDIDATE":
        adoption["R6G-009"] = "A1_STABLE_REFERENCE_IMPLEMENTATION"

    candidates = [c003, c005, c009]
    dashboard = {
        "schema": "gunnchos.r6g.portfolio_dashboard.v1",
        "IMPROVED_STATE_OF_ART": False,
        "disclaimer": (
            "Interesting simulation ≠ accepted breakthrough. "
            "Same-PR arithmetic verifier ≠ R6 independent. "
            "No PROMISING_DIGITAL without external path."
        ),
        "ladder_definition": LADDER,
        "rows": [
            _dashboard_row(c003, adoption=adoption["R6G-003"]),
            {
                "packet": "R6G-002",
                "baseline_registered": True,
                "baseline_reproduced": False,
                "multi_seed": False,
                "falsification": False,
                "negative_controls": False,
                "ablation": False,
                "robustness": "NOT_EXECUTED",
                "clean_checkout": False,
                "independent_verify": False,
                "integration": False,
                "adoption_package": adoption["R6G-002"],
                "external_reproduction": False,
                "physical_validation": False,
                "paper_status": "NOT_SUBMITTED",
                "standard_mapping": "N/A",
                "claim_state": "MODELED_ILLUSTRATIVE",
                "ladder_earned": ["R0", "R1"],
                "IMPROVED_STATE_OF_ART": False,
            },
            _dashboard_row(c005, adoption=adoption["R6G-005"]),
            _dashboard_row(c009, adoption=adoption["R6G-009"]),
            {
                "packet": "R6G-008",
                "baseline_registered": True,
                "baseline_reproduced": False,
                "multi_seed": False,
                "falsification": False,
                "negative_controls": False,
                "ablation": False,
                "robustness": "NOT_EXECUTED",
                "clean_checkout": False,
                "independent_verify": False,
                "integration": False,
                "adoption_package": adoption["R6G-008"],
                "external_reproduction": False,
                "physical_validation": False,
                "paper_status": "NOT_SUBMITTED",
                "standard_mapping": "N/A",
                "claim_state": "MODELED_LOOKUP_TABLE",
                "ladder_earned": ["R0", "R1"],
                "IMPROVED_STATE_OF_ART": False,
                "real_education_outcome_claimed": False,
            },
        ],
    }
    _write_json(out / "R6G_PORTFOLIO_DASHBOARD.json", dashboard)
    _write_json(ROOT / "research" / "6g_breakthroughs" / "R6G_PORTFOLIO_DASHBOARD.json", dashboard)

    all_r3 = all(c["ladder_flags"].get("R3") for c in candidates)
    # Falsification: 003 has R4; 005/009 publish negatives but ladder R4 not contiguous — use evidence flags
    falsification = (
        bool(c003["ladder_flags"].get("R4"))
        and bool(c005.get("falsification_evidence"))
        and bool(c009.get("falsification_evidence"))
    )
    all_r5 = all(c["ladder_flags"].get("R5") for c in candidates)
    any_r5 = any(c["ladder_flags"].get("R5") for c in candidates)

    # DIGITAL_REPLICATION_PASS requires R3–R5 on all active candidates AND external R6 — not this cycle
    digital_replication_pass = False
    assert SAME_PR_VERIFIER_COUNTS_AS_R6 is False

    suite = {
        "schema": "gunnchos.r6g.replication_suite.v1",
        "as_of_utc": datetime.now(timezone.utc).isoformat(),
        "seed_registry": SEED_REGISTRY,
        "candidates": {c["candidate"]: c for c in candidates},
        "supporting": {
            "R6G-002": {
                "ok": r002["ok"],
                "claim_state": "MODELED_ILLUSTRATIVE",
                "ladder_earned": ["R0", "R1"],
                "IMPROVED_STATE_OF_ART": False,
            },
            "R6G-008": {
                "ok": sem["ok"],
                "claim_state": "MODELED_LOOKUP_TABLE",
                "ladder_earned": ["R0", "R1"],
                "real_education_outcome_claimed": False,
                "IMPROVED_STATE_OF_ART": False,
            },
        },
        "negative_result_count": len(negatives),
        "illustrative_negative_count": len(illustrative),
        "adoption_levels": adoption,
        "dashboard": dashboard,
        "tokens": {
            "R6G_DIGITAL_REPLICATION_PASS": digital_replication_pass,
            "R6G_MULTI_SEED_REPRODUCED": all_r3,  # false while 005/009 R3 deferred
            "R6G_FALSIFICATION_DOCUMENTED": falsification,
            "R6G_ABLATIONS_DOCUMENTED": all_r5,  # false until 005/009 R5 awarded
            "R6G_ABLATIONS_PARTIAL": bool(any_r5 and not all_r5),  # 003 only this cycle
            "R6G_INDEPENDENT_VERIFIER_PASS": False,  # never earned by same-PR recalculator
            "IMPROVED_STATE_OF_ART": False,
            "PHYSICAL_REPRODUCTION_PENDING": True,
            "EXTERNAL_REPRODUCTION_PENDING": True,
            "PEER_REVIEWED": False,
            "STANDARDIZED_6G": False,
            "6G_BREAKTHROUGH_PASS": None,
            "BREAKTHROUGH_PROVEN": False,
            "PROMISING_DIGITAL_ANY": False,
        },
        "IMPROVED_STATE_OF_ART": False,
        "OPEN": [
            "R6 independent verification requires EXTERNAL path — same-PR arithmetic does not earn R6",
            "R6G_DIGITAL_REPLICATION_PASS remains false until R3–R5 all candidates + external R6",
            "Clean-checkout CI soak (R7) EXTERNAL_PENDING",
            "External reproduction packet EXTERNAL_REPRODUCTION_PENDING",
            "Physical/SDR/OTA R8/R9 not claimed",
            "R6G-006/007 MODELED_CONTRACT_ONLY — no physical exaggeration",
            "R6G-002/004/008/010/011 honesty-demoted to illustrative/stub/hooks/map (R0–R1)",
            "Construction-stub negatives marked ILLUSTRATIVE — excluded from real count",
            "Large robustness / Sionna / ns-3 sweeps deferred (Product-Use may own QEMU)",
            "IMPROVED_STATE_OF_ART remains false",
            "PROMISING_DIGITAL not awarded this cycle",
            "R6G-003 DIGITAL_IMPROVEMENT_CANDIDATE; 005/009 REPLICATION_INCOMPLETE preserved",
        ],
        "deferred_heavy_work": [
            "ns-3 / Sionna / DeepMIMO campaign sweeps",
            "multi-hour RF / THz physical campaigns",
            "extra QEMU",
            "physical RIS / THz purchase",
        ],
    }
    assert_no_soa(suite)
    _write_json(out / "R6G_REPLICATION_SUITE.json", suite)
    _write_json(out / "SEED_REGISTRY.json", SEED_REGISTRY)
    return suite


def main() -> int:
    suite = run_replication_suite()
    print("R6G_REPLICATION_PASS" if suite["tokens"]["R6G_DIGITAL_REPLICATION_PASS"] else "R6G_REPLICATION_PARTIAL")
    print("negatives", suite["negative_result_count"])
    print("SoA", suite["IMPROVED_STATE_OF_ART"])
    for k, v in suite["candidates"].items():
        print(k, v["claim_state"], v["ladder_earned"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
