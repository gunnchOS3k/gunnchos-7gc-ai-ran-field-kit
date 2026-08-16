"""Ablations for multimodal / AI-PHY / twin composites — R5 gated on checked removals."""
from __future__ import annotations

from typing import Any

from research.r6g.experiments.r6g003_fr3_isac import run_config
from research.r6g.experiments.r6g005_ai_phy import run_r6g005
from research.r6g.experiments.r6g006_cellfree_mimo_contract import run_r6g006
from research.r6g.experiments.r6g007_adaptive_ris_contract import run_r6g007
from research.r6g.experiments.r6g009_predictive_twin import run_r6g009


def ablate_r6g003(seeds: list[int]) -> dict[str, Any]:
    """Drop modality trust / compare composites vs RF-only; gate on measurable deltas."""
    rows = []
    checks_pass = 0
    for seed in seeds:
        base = run_config({
            "config_id": f"abl_full_s{seed}",
            "seed": seed,
            "vision_spoof_rate": 0.0,
            "fusion_trust_vision": 0.30,
        })
        no_vision = run_config({
            "config_id": f"abl_no_vision_s{seed}",
            "seed": seed,
            "vision_spoof_rate": 0.0,
            "fusion_trust_vision": 0.0,
        })
        full = base["modality_matrix"]["RF_ALL_MODALITIES"]["position_RMSE"]
        ring = base["modality_matrix"]["RF_RING_UWB_IMU"]["position_RMSE"]
        imu = base["modality_matrix"]["RF_DEVICE_IMU"]["position_RMSE"]
        rf = base["modality_matrix"]["RF_ONLY"]["position_RMSE"]
        trust0 = no_vision["modality_matrix"]["RF_ALL_MODALITIES"]["position_RMSE"]
        # Checked removals: composites differ from RF-only; vision-trust=0 changes ALL path
        distinct = len({round(rf, 4), round(imu, 4), round(ring, 4), round(full, 4)}) >= 3
        trust_changes = abs(trust0 - full) > 1e-4
        ok = distinct and trust_changes
        if ok:
            checks_pass += 1
        rows.append({
            "seed": seed,
            "RF_ONLY": rf,
            "RF_DEVICE_IMU": imu,
            "RF_RING_UWB_IMU": ring,
            "RF_ALL": full,
            "delta_all_vs_rf": round(full - rf, 4),
            "delta_ring_vs_rf": round(ring - rf, 4),
            "delta_imu_vs_rf": round(imu - rf, 4),
            "no_vision_trust0_ALL": trust0,
            "ablation_check_ok": ok,
        })
    ablation_ok = checks_pass == len(seeds) and len(seeds) >= 1
    return {
        "packet": "R6G-003",
        "ablation": "modality_drop_and_vision_trust0",
        "rows": rows,
        "ablation_ok": ablation_ok,
        "checks_passed": checks_pass,
        "checks_required": len(seeds),
        "interpretation": (
            "Compares RF-only vs IMU vs Ring vs ALL; vision-trust=0 stresses fusion weight. "
            "Not an OTA SoA claim."
        ),
    }


def ablate_r6g005(seeds: list[int]) -> dict[str, Any]:
    """Method ablation across seeds: remove aware / compare naive vs conventional."""
    rows = []
    checks_pass = 0
    for seed in seeds:
        r = run_r6g005(seed=seed)
        results = r["results"]
        naive_adv = results["AI_CSF"]["adversarial_csi"]["failure_rate"]
        aware_adv = results["AI_CSF_UNCERTAINTY_AWARE"]["adversarial_csi"]["failure_rate"]
        conv_adv = results["CONVENTIONAL_CSI"]["adversarial_csi"]["failure_rate"]
        # Checked removal: dropping uncertainty-awareness (naive) worsens adversarial failure
        removing_aware_hurts = naive_adv > aware_adv
        # And naive is worse than conventional under adversarial (method family distinct)
        naive_worse_than_conv = naive_adv > conv_adv
        ok = removing_aware_hurts and naive_worse_than_conv
        if ok:
            checks_pass += 1
        rows.append({
            "seed": seed,
            "naive_adversarial_failure": naive_adv,
            "aware_adversarial_failure": aware_adv,
            "conventional_adversarial_failure": conv_adv,
            "removing_aware_increases_failure": removing_aware_hurts,
            "naive_worse_than_conventional": naive_worse_than_conv,
            "ablation_check_ok": ok,
            "in_distribution": {m: results[m]["in_distribution"] for m in results},
        })
    ablation_ok = checks_pass == len(seeds) and len(seeds) >= 1
    return {
        "packet": "R6G-005",
        "ablation": "method_family_conventional_vs_naive_vs_aware",
        "rows": rows,
        "ablation_ok": ablation_ok,
        "checks_passed": checks_pass,
        "checks_required": len(seeds),
        "interpretation": (
            "Checked removal of uncertainty-aware fallback increases adversarial failure. "
            "No physical distance claim."
        ),
    }


def ablate_r6g009(seeds: list[int]) -> dict[str, Any]:
    """Policy ablation: remove predictive vs current across seeds + delay."""
    rows = []
    checks_pass = 0
    for seed in seeds:
        r = run_r6g009(seed=seed)
        g25 = r["delay_grid_ms"]["25"]
        g100 = r["delay_grid_ms"]["100"]
        pred25 = g25["PREDICTIVE_BELIEF_STATE"]["policy_regret"]
        cur25 = g25["CURRENT_STATE_ONLY"]["policy_regret"]
        pred100 = g100["PREDICTIVE_BELIEF_STATE"]["policy_regret"]
        cur100 = g100["CURRENT_STATE_ONLY"]["policy_regret"]
        belief25 = g25["BELIEF_STATE"]["policy_regret"]
        # Checked: policies are not identical; predictive can help at moderate delay
        distinct = len({round(pred25, 4), round(cur25, 4), round(belief25, 4)}) >= 2
        # And removing predictive at long horizon is not always worse (falsifying ablation)
        long_horizon_not_always_win = pred100 >= cur100 * 0.98
        ok = distinct and long_horizon_not_always_win
        if ok:
            checks_pass += 1
        rows.append({
            "seed": seed,
            "pred25": pred25,
            "cur25": cur25,
            "belief25": belief25,
            "pred100": pred100,
            "cur100": cur100,
            "policies_distinct_at_25ms": distinct,
            "long_horizon_predictive_no_gain": long_horizon_not_always_win,
            "ablation_check_ok": ok,
        })
    ablation_ok = checks_pass >= max(1, len(seeds) // 2) and len(seeds) >= 1
    return {
        "packet": "R6G-009",
        "ablation": "policy_family_across_delay",
        "rows": rows,
        "ablation_ok": ablation_ok,
        "checks_passed": checks_pass,
        "checks_required": len(seeds),
        "interpretation": (
            "Checked policy removal: predictive vs current/belief; long-horizon can negate gains."
        ),
    }


def ablate_r6g006(seeds: list[int]) -> dict[str, Any]:
    """Precoder ablation: remove RZF vs MRT vs matched-filter baseline."""
    rows = []
    checks_pass = 0
    for seed in seeds:
        r = run_r6g006(seed=seed)
        ideal = r["results_se_bps_hz"]["ideal_iid"]
        drop = r["results_se_bps_hz"]["ap_dropout"]
        rzf_i, mrt_i, mf_i = ideal["RZF_DIGITAL"], ideal["MRT"], ideal["MATCHED_FILTER_BASELINE"]
        rzf_d, mrt_d = drop["RZF_DIGITAL"], drop["MRT"]
        distinct = len({round(rzf_i, 4), round(mrt_i, 4), round(mf_i, 4)}) >= 2
        # Checked removal: under AP dropout, RZF advantage vs MRT shrinks or flips
        dropout_hurts_rzf_edge = (rzf_i - mrt_i) > (rzf_d - mrt_d) - 1e-9
        ok = distinct and dropout_hurts_rzf_edge
        if ok:
            checks_pass += 1
        rows.append({
            "seed": seed,
            "ideal_rzf": rzf_i,
            "ideal_mrt": mrt_i,
            "ideal_mf": mf_i,
            "dropout_rzf": rzf_d,
            "dropout_mrt": mrt_d,
            "precoders_distinct": distinct,
            "dropout_shrinks_rzf_edge": dropout_hurts_rzf_edge,
            "ablation_check_ok": ok,
        })
    ablation_ok = checks_pass == len(seeds) and len(seeds) >= 1
    return {
        "packet": "R6G-006",
        "ablation": "precoder_family_mrt_rzf_vs_dropout",
        "rows": rows,
        "ablation_ok": ablation_ok,
        "checks_passed": checks_pass,
        "checks_required": len(seeds),
        "interpretation": (
            "Checked precoder family under ideal vs AP dropout; not a physical cell-free claim."
        ),
    }


def ablate_r6g007(seeds: list[int]) -> dict[str, Any]:
    """Control ablation: adaptive absolute SNR drops under element failure; families distinct."""
    rows = []
    checks_pass = 0
    for seed in seeds:
        r = run_r6g007(seed=seed)
        static = r["results_snr_db"]["static_los"]
        fail = r["results_snr_db"]["element_failure"]
        mob = r["results_snr_db"]["mobility_mismatch"]
        a_s, p_s, rnd_s = static["ADAPTIVE_PHASE"], static["PASSIVE_FIXED"], static["RANDOM_PHASE"]
        a_f = fail["ADAPTIVE_PHASE"]
        a_m, p_m = mob["ADAPTIVE_PHASE"], mob["PASSIVE_FIXED"]
        distinct = len({round(a_s, 4), round(p_s, 4), round(rnd_s, 4)}) >= 2
        adaptive_drops_on_failure = a_f < a_s - 0.25
        # Mobility stress is a checked removal of accurate CSI/phases
        mobility_hurts = a_m < a_s - 0.25
        ok = distinct and adaptive_drops_on_failure and mobility_hurts
        if ok:
            checks_pass += 1
        rows.append({
            "seed": seed,
            "static_adaptive": a_s,
            "static_passive": p_s,
            "static_random": rnd_s,
            "fail_adaptive": a_f,
            "mobility_adaptive": a_m,
            "mobility_passive": p_m,
            "controls_distinct": distinct,
            "adaptive_drops_on_failure": adaptive_drops_on_failure,
            "mobility_hurts_adaptive": mobility_hurts,
            "ablation_check_ok": ok,
        })
    ablation_ok = checks_pass == len(seeds) and len(seeds) >= 1
    return {
        "packet": "R6G-007",
        "ablation": "control_family_adaptive_vs_failure_and_mobility",
        "rows": rows,
        "ablation_ok": ablation_ok,
        "checks_passed": checks_pass,
        "checks_required": len(seeds),
        "interpretation": (
            "Checked adaptive vs passive/random; element failure and mobility mismatch hurt adaptive SNR. "
            "No RIS purchase."
        ),
    }
