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
from research.r6g.experiments.r6g004_multimodal_isac_personal import run_r6g004
from research.r6g.experiments.r6g005_ai_phy import run_r6g005
from research.r6g.experiments.r6g006_cellfree_mimo_contract import run_r6g006
from research.r6g.experiments.r6g007_adaptive_ris_contract import run_r6g007
from research.r6g.experiments.r6g008_semantic_ntn import run_r6g008
from research.r6g.experiments.r6g009_predictive_twin import run_r6g009
from research.r6g.experiments.r6g010_security_pqc_privacy import run_r6g010
from research.r6g.experiments.r6g011_imt2030_harness import run_r6g011
from research.r6g.experiments.semantic_continuity_ntn_education import run_semantic_continuity
from research.r6g.replication.ablations import (
    ablate_r6g003,
    ablate_r6g005,
    ablate_r6g006,
    ablate_r6g007,
    ablate_r6g009,
)
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


def _replicate_r6g006(raw_dir: Path) -> dict[str, Any]:
    seeds = SEED_REGISTRY["candidates"]["R6G-006"]
    seed_rows = []
    neg_notes_all: list[dict[str, Any]] = []
    support_flags = []
    for seed in seeds["primary_seeds"]:
        report = run_r6g006(seed=seed)
        digest = _write_json(raw_dir / "R6G-006" / f"seed_{seed}.json", report)
        ideal = report["ideal_iid"]
        seed_rows.append({
            "seed": seed,
            "sha256": digest,
            "rzf": ideal["RZF_DIGITAL"],
            "mrt": ideal["MRT"],
            "mf": ideal["MATCHED_FILTER_BASELINE"],
            "delta_rzf_mrt": report["delta_rzf_minus_mrt_ideal"],
            "hypothesis": report["HYPOTHESIS_SUPPORTED_DIGITALLY"],
        })
        support_flags.append(bool(report["HYPOTHESIS_SUPPORTED_DIGITALLY"]))
        for n in report.get("documented_negative_or_no_gain", []):
            neg_notes_all.append({"seed": seed, **n})

    full = run_r6g006(seed=seeds["primary_seeds"][0])
    _write_json(raw_dir / "R6G-006" / "full_report.json", full)

    robustness_rows = []
    for seed in seeds["robustness_seeds"]:
        report = run_r6g006(seed=seed)
        digest = _write_json(raw_dir / "R6G-006" / f"rob_s{seed}.json", report)
        robustness_rows.append({
            "seed": seed,
            "sha256": digest,
            "delta_rzf_mrt": report["delta_rzf_minus_mrt_ideal"],
            "neg_count": len(report.get("documented_negative_or_no_gain") or []),
        })

    deltas = [r["delta_rzf_mrt"] for r in seed_rows]
    metrics_vary = _values_vary(deltas)
    multi_ok_evidence = metrics_vary and sum(support_flags) / max(1, len(support_flags)) >= 0.5
    neg_ok = len(neg_notes_all) >= 1
    ablations = ablate_r6g006(seeds["ablation_seeds"])
    _write_json(raw_dir / "R6G-006" / "ablation.json", ablations)
    abl_ok_evidence = bool(ablations.get("ablation_ok"))

    # New digital packet: earn R0–R2 only this cycle (no R3+ auto-promotion).
    ladder_flags = _empty_ladder(R0=True, R1=True, R2=True, R3=False, R4=False, R5=False)
    return {
        "candidate": "R6G-006",
        "title": "Cell-free MIMO digital (seeded)",
        "seed_rows": seed_rows,
        "robustness_runs": robustness_rows,
        "metrics_vary_across_seeds": metrics_vary,
        "multi_seed_evidence_ready": multi_ok_evidence,
        "ablation_evidence_ready": abl_ok_evidence,
        "falsification_evidence": neg_ok,
        "documented_negative_or_no_gain": neg_notes_all[:8],
        "ablation": ablations,
        "ladder_flags": ladder_flags,
        "ladder_earned": contiguous_earned(ladder_flags),
        "ladder_cap_note": (
            "R0–R2 this cycle after MODELED_CONTRACT_ONLY → DIGITALLY_EXECUTED. "
            "R3+ deferred; R6 external-only. No physical cell-free claim."
        ),
        "claim_state": "DIGITALLY_EXECUTED",
        "status": "DIGITALLY_EXECUTED",
        "IMPROVED_STATE_OF_ART": False,
        "prior_status": "MODELED_CONTRACT_ONLY",
    }


def _replicate_r6g007(raw_dir: Path) -> dict[str, Any]:
    seeds = SEED_REGISTRY["candidates"]["R6G-007"]
    seed_rows = []
    neg_notes_all: list[dict[str, Any]] = []
    support_flags = []
    for seed in seeds["primary_seeds"]:
        report = run_r6g007(seed=seed)
        digest = _write_json(raw_dir / "R6G-007" / f"seed_{seed}.json", report)
        static = report["static_los"]
        seed_rows.append({
            "seed": seed,
            "sha256": digest,
            "adaptive": static["ADAPTIVE_PHASE"],
            "passive": static["PASSIVE_FIXED"],
            "random": static["RANDOM_PHASE"],
            "delta_db": report["delta_adaptive_minus_passive_db"],
            "hypothesis": report["HYPOTHESIS_SUPPORTED_DIGITALLY"],
        })
        support_flags.append(bool(report["HYPOTHESIS_SUPPORTED_DIGITALLY"]))
        for n in report.get("documented_negative_or_no_gain", []):
            neg_notes_all.append({"seed": seed, **n})

    full = run_r6g007(seed=seeds["primary_seeds"][0])
    _write_json(raw_dir / "R6G-007" / "full_report.json", full)

    robustness_rows = []
    for seed in seeds["robustness_seeds"]:
        report = run_r6g007(seed=seed)
        digest = _write_json(raw_dir / "R6G-007" / f"rob_s{seed}.json", report)
        robustness_rows.append({
            "seed": seed,
            "sha256": digest,
            "delta_db": report["delta_adaptive_minus_passive_db"],
            "neg_count": len(report.get("documented_negative_or_no_gain") or []),
        })

    deltas = [r["delta_db"] for r in seed_rows]
    metrics_vary = _values_vary(deltas)
    multi_ok_evidence = metrics_vary and sum(support_flags) / max(1, len(support_flags)) >= 0.5
    neg_ok = len(neg_notes_all) >= 1
    ablations = ablate_r6g007(seeds["ablation_seeds"])
    _write_json(raw_dir / "R6G-007" / "ablation.json", ablations)
    abl_ok_evidence = bool(ablations.get("ablation_ok"))

    ladder_flags = _empty_ladder(R0=True, R1=True, R2=True, R3=False, R4=False, R5=False)
    return {
        "candidate": "R6G-007",
        "title": "Adaptive RIS digital (seeded; no purchase)",
        "seed_rows": seed_rows,
        "robustness_runs": robustness_rows,
        "metrics_vary_across_seeds": metrics_vary,
        "multi_seed_evidence_ready": multi_ok_evidence,
        "ablation_evidence_ready": abl_ok_evidence,
        "falsification_evidence": neg_ok,
        "documented_negative_or_no_gain": neg_notes_all[:8],
        "ablation": ablations,
        "ladder_flags": ladder_flags,
        "ladder_earned": contiguous_earned(ladder_flags),
        "ladder_cap_note": (
            "R0–R2 this cycle after MODELED_CONTRACT_ONLY → DIGITALLY_EXECUTED. "
            "R3+ deferred; R6 external-only. RIS_PURCHASE=false."
        ),
        "claim_state": "DIGITALLY_EXECUTED",
        "status": "DIGITALLY_EXECUTED",
        "IMPROVED_STATE_OF_ART": False,
        "RIS_PURCHASE": False,
        "prior_status": "MODELED_CONTRACT_ONLY",
    }


def _collect_negatives(
    c003: dict,
    c005: dict,
    c009: dict,
    *,
    extra: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Real negatives (003/005/009 + executed 002/004/006/007/008/010). Illus. stubs separate."""
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
    for n in extra or []:
        if n.get("ILLUSTRATIVE"):
            continue
        out.append(n)
    return out


def _illustrative_negatives() -> list[dict[str, Any]]:
    """Legacy construction stubs — do not count toward real negative_result_count."""
    return []

def _dashboard_row(c: dict[str, Any], *, adoption: str) -> dict[str, Any]:
    """Dashboard consumes evidence manifests — never invents claim truth / ladder promotion.

    Boolean evidence columns reflect published evidence fields. Ladder/claim stay
    on the candidate record (preserved #79 caps for 005/009).
    """
    flags = c.get("ladder_flags", {})
    earned = c.get("ladder_earned") or contiguous_earned(flags)
    falsification_ev = bool(c.get("falsification_evidence")) or bool(
        c.get("documented_negative_or_no_gain")
    )
    multi_seed_ev = bool(c.get("multi_seed_evidence_ready")) or bool(
        c.get("metrics_vary_across_seeds")
    )
    abl_ev = bool(c.get("ablation_evidence_ready")) or bool(
        (c.get("ablation") or {}).get("ablation_ok")
    )
    return {
        "packet": c["candidate"],
        "baseline_registered": bool(flags.get("R0", False)) or "R0" in earned,
        "baseline_reproduced": "R3" in earned,  # earned only — not evidence-ready alone
        "multi_seed": multi_seed_ev,
        "multi_seed_ladder_earned": "R3" in earned,
        "falsification": falsification_ev,
        "falsification_ladder_earned": "R4" in earned,
        "negative_controls": falsification_ev,
        "ablation": abl_ev,
        "ablation_ladder_earned": "R5" in earned,
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
        "ladder_earned": earned,
        "evidence_manifest": {
            "metrics_vary_across_seeds": bool(c.get("metrics_vary_across_seeds")),
            "multi_seed_evidence_ready": bool(c.get("multi_seed_evidence_ready")),
            "falsification_evidence": bool(c.get("falsification_evidence")),
            "ablation_evidence_ready": bool(c.get("ablation_evidence_ready")),
            "r3_r5_deferred": c.get("r3_r5_deferred"),
            "ladder_cap_note": c.get("ladder_cap_note"),
        },
        "IMPROVED_STATE_OF_ART": False,
    }


def _supporting_dashboard_row(packet: str, report: dict[str, Any], *, adoption: str) -> dict[str, Any]:
    negatives = report.get("documented_negative_or_no_gain") or []
    real_neg = [n for n in negatives if not n.get("ILLUSTRATIVE")]
    return {
        "packet": packet,
        "baseline_registered": True,
        "baseline_reproduced": False,
        "multi_seed": bool(report.get("primary_seeds") or report.get("seeds")),
        "falsification": len(real_neg) >= 1,
        "negative_controls": len(real_neg) >= 1,
        "ablation": bool(report.get("ablations")),
        "robustness": "EXECUTED_LIGHTWEIGHT" if report.get("status", "").startswith("DIGITAL") else "NOT_EXECUTED",
        "clean_checkout": False,
        "independent_verify": False,
        "integration": False,
        "adoption_package": adoption,
        "external_reproduction": False,
        "physical_validation": False,
        "paper_status": "NOT_SUBMITTED",
        "standard_mapping": "N/A",
        "claim_state": report.get("claim_state"),
        "ladder_earned": report.get("ladder_earned", ["R0", "R1"]),
        "evidence_manifest": {
            "execution_class": report.get("execution_class"),
            "status": report.get("status"),
            "real_negative_count": len(real_neg),
        },
        "IMPROVED_STATE_OF_ART": False,
        "real_education_outcome_claimed": report.get("real_education_outcome_claimed", False),
    }


def run_replication_suite(out_dir: Path | None = None) -> dict[str, Any]:
    out = Path(out_dir) if out_dir else (ROOT / "artifacts" / "r6g" / "replication")
    raw_dir = out / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    c003 = _replicate_r6g003(raw_dir)
    c005 = _replicate_r6g005(raw_dir)
    c009 = _replicate_r6g009(raw_dir)
    c006 = _replicate_r6g006(raw_dir)
    c007 = _replicate_r6g007(raw_dir)
    r002 = run_r6g002()
    r004 = run_r6g004()
    r008 = run_r6g008()
    r010 = run_r6g010()
    r011 = run_r6g011()
    sem = run_semantic_continuity()
    _write_json(raw_dir / "R6G-002" / "report.json", r002)
    _write_json(raw_dir / "R6G-004" / "report.json", r004)
    _write_json(raw_dir / "R6G-008" / "report.json", r008)
    _write_json(raw_dir / "R6G-008" / "semantic_continuity.json", sem)
    _write_json(raw_dir / "R6G-010" / "report.json", r010)
    _write_json(raw_dir / "R6G-011" / "report.json", r011)

    extra_negs: list[dict[str, Any]] = []
    for packet, rep in (("R6G-002", r002), ("R6G-004", r004), ("R6G-008", r008), ("R6G-010", r010)):
        for n in rep.get("documented_negative_or_no_gain") or []:
            extra_negs.append({"packet": packet, **n})
    for packet, rep in (("R6G-006", c006), ("R6G-007", c007)):
        for n in rep.get("documented_negative_or_no_gain") or []:
            extra_negs.append({"packet": packet, **n})
    negatives = _collect_negatives(c003, c005, c009, extra=extra_negs)
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
        "R6G-006": "A0_INTERNAL_EXPERIMENT",
        "R6G-007": "A0_INTERNAL_EXPERIMENT",
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
    executed_support = [c006, c007]
    dashboard = {
        "schema": "gunnchos.r6g.portfolio_dashboard.v1",
        "IMPROVED_STATE_OF_ART": False,
        "disclaimer": (
            "Interesting simulation ≠ accepted breakthrough. "
            "Same-PR arithmetic verifier ≠ R6 independent. "
            "Dashboard evidence columns consume manifests; ladder/claim are not auto-promoted."
        ),
        "ladder_definition": LADDER,
        "rows": [
            _dashboard_row(c003, adoption=adoption["R6G-003"]),
            _supporting_dashboard_row("R6G-002", r002, adoption=adoption["R6G-002"]),
            _dashboard_row(c005, adoption=adoption["R6G-005"]),
            _dashboard_row(c009, adoption=adoption["R6G-009"]),
            _dashboard_row(c006, adoption=adoption["R6G-006"]),
            _dashboard_row(c007, adoption=adoption["R6G-007"]),
            _supporting_dashboard_row("R6G-008", r008, adoption=adoption["R6G-008"]),
            _supporting_dashboard_row("R6G-004", r004, adoption=adoption["R6G-004"]),
            _supporting_dashboard_row("R6G-010", r010, adoption=adoption["R6G-010"]),
            _supporting_dashboard_row("R6G-011", r011, adoption=adoption["R6G-011"]),
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
                "claim_state": r002["claim_state"],
                "ladder_earned": r002["ladder_earned"],
                "IMPROVED_STATE_OF_ART": False,
            },
            "R6G-004": {
                "ok": r004["ok"],
                "claim_state": r004["claim_state"],
                "ladder_earned": r004["ladder_earned"],
                "IMPROVED_STATE_OF_ART": False,
            },
            "R6G-008": {
                "ok": r008["ok"],
                "claim_state": r008["claim_state"],
                "ladder_earned": r008["ladder_earned"],
                "real_education_outcome_claimed": False,
                "IMPROVED_STATE_OF_ART": False,
            },
            "R6G-010": {
                "ok": r010["ok"],
                "claim_state": r010["claim_state"],
                "ladder_earned": r010["ladder_earned"],
                "IMPROVED_STATE_OF_ART": False,
            },
            "R6G-011": {
                "ok": r011["ok"],
                "claim_state": r011["claim_state"],
                "ladder_earned": r011["ladder_earned"],
                "IMPROVED_STATE_OF_ART": False,
            },
            "R6G-006": {
                "ok": True,
                "claim_state": c006["claim_state"],
                "ladder_earned": c006["ladder_earned"],
                "status": c006["status"],
                "prior_status": c006.get("prior_status"),
                "IMPROVED_STATE_OF_ART": False,
            },
            "R6G-007": {
                "ok": True,
                "claim_state": c007["claim_state"],
                "ladder_earned": c007["ladder_earned"],
                "status": c007["status"],
                "prior_status": c007.get("prior_status"),
                "RIS_PURCHASE": False,
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
            "R6G_006_007_DIGITALLY_EXECUTED": True,
        },
        "IMPROVED_STATE_OF_ART": False,
        "OPEN": [
            "R6 independent verification requires EXTERNAL path — same-PR arithmetic does not earn R6",
            "R6G_DIGITAL_REPLICATION_PASS remains false until R3–R5 all candidates + external R6",
            "Clean-checkout CI soak (R7) EXTERNAL_PENDING",
            "External reproduction packet EXTERNAL_REPRODUCTION_PENDING",
            "Physical/SDR/OTA R8/R9 not claimed",
            "R6G-006/007 DIGITALLY_EXECUTED (R0–R2) — still no physical / purchase / SoA claim",
            "R6G-002/008/010 DIGITALLY_EXECUTED; 011 DIGITALLY_EXECUTED_HARNESS; 004 DIGITAL_SYNTHETIC_EXPERIMENT",
            "Dual-tree: artifacts/r6g is authoritative; stable_seed replaces process-salted hash()",
            "Large robustness / Sionna / ns-3 sweeps deferred (Product-Use may own QEMU)",
            "IMPROVED_STATE_OF_ART remains false",
            "PROMISING_DIGITAL not awarded this cycle",
            "R6G-003 DIGITAL_IMPROVEMENT_CANDIDATE; 005/009 REPLICATION_INCOMPLETE preserved",
            "STREAM-C-PKT-001 deepened 003/005/009 seed sets; 011 harness seeds reserved",
        ],
        "deferred_heavy_work": [
            "ns-3 / Sionna / DeepMIMO campaign sweeps",
            "multi-hour RF / THz physical campaigns",
            "extra QEMU",
            "physical RIS / THz purchase",
        ],
        "executed_support_candidates": {c["candidate"]: c for c in executed_support},
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
