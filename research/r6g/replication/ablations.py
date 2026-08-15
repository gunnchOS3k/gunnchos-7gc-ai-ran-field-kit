"""Ablations for multimodal / AI-PHY / twin composites (lightweight)."""
from __future__ import annotations

from typing import Any

from research.r6g.experiments.r6g003_fr3_isac import run_config
from research.r6g.experiments.r6g005_ai_phy import run_r6g005
from research.r6g.experiments.r6g009_predictive_twin import run_r6g009


def ablate_r6g003(seeds: list[int]) -> dict[str, Any]:
    """Drop one modality family at a time vs full fusion."""
    rows = []
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
            "fusion_trust_vision": 0.0,  # zero trust ≈ RF+UWB+IMU path dominates ALL
        })
        # Proxy: RF_RING_UWB_IMU as "no vision" composite
        full = base["modality_matrix"]["RF_ALL_MODALITIES"]["position_RMSE"]
        ring = base["modality_matrix"]["RF_RING_UWB_IMU"]["position_RMSE"]
        imu = base["modality_matrix"]["RF_DEVICE_IMU"]["position_RMSE"]
        rf = base["modality_matrix"]["RF_ONLY"]["position_RMSE"]
        rows.append({
            "seed": seed,
            "RF_ONLY": rf,
            "RF_DEVICE_IMU": imu,
            "RF_RING_UWB_IMU": ring,
            "RF_ALL": full,
            "delta_all_vs_rf": round(full - rf, 4),
            "delta_ring_vs_rf": round(ring - rf, 4),
            "delta_imu_vs_rf": round(imu - rf, 4),
            "no_vision_trust0_ALL": no_vision["modality_matrix"]["RF_ALL_MODALITIES"]["position_RMSE"],
        })
    return {
        "packet": "R6G-003",
        "ablation": "modality_drop_and_vision_trust0",
        "rows": rows,
        "interpretation": (
            "Compares RF-only vs IMU vs Ring vs ALL; vision-trust=0 stresses fusion weight. "
            "Not an OTA SoA claim."
        ),
    }


def ablate_r6g005() -> dict[str, Any]:
    """Method ablation: conventional vs naive AI vs uncertainty-aware."""
    r = run_r6g005()
    # Extract adversarial + ID contrasts as ablation evidence
    results = r["results"]
    return {
        "packet": "R6G-005",
        "ablation": "method_family_conventional_vs_naive_vs_aware",
        "in_distribution": {
            m: results[m]["in_distribution"] for m in results
        },
        "adversarial_csi": {
            m: results[m]["adversarial_csi"] for m in results
        },
        "interpretation": (
            "Naive AI may win compression on IID but fails OOD; aware falls back. "
            "No physical distance claim."
        ),
    }


def ablate_r6g009() -> dict[str, Any]:
    """Policy ablation across delay grid."""
    r = run_r6g009()
    return {
        "packet": "R6G-009",
        "ablation": "policy_family_across_delay",
        "delay_grid_ms": r["delay_grid_ms"],
        "interpretation": (
            "Predictive vs current/belief/delayed; long-horizon and jump can negate gains."
        ),
    }
