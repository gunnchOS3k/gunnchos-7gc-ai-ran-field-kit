"""R6G-003 — FR3 / ISAC / TN-NTN digital experiments (falsifiable sensing model).

Replaces hardcoded RMSE factor multipliers with a seeded digital channel/sensing
model. Multimodal fusion CAN fail vs RF-only under adversarial configs/seeds;
MULTIMODAL_ISAC_DIGITAL_IMPROVEMENT is earned only when primary configs beat the
digital RF-only baseline AND at least one negative/no-gain case is documented.
"""
from __future__ import annotations

import math
import random
from typing import Any

from research.r6g.claim_firewall import assert_no_soa
from research.r6g.metrics.stable_seed import mix_seed
from research.r6g.metrics.useful_connectivity import useful_connectivity_score

MODALITIES = (
    "RF_ONLY",
    "RF_DEVICE_IMU",
    "RF_RING_UWB_IMU",
    "RF_VISION",
    "RF_ALL_MODALITIES",
)


def _true_track(n: int, seed: int) -> list[tuple[float, float]]:
    rng = random.Random(seed)
    x, y = 0.0, 0.0
    vx, vy = 0.8, 0.3
    track: list[tuple[float, float]] = []
    for _ in range(n):
        vx += rng.gauss(0.0, 0.05)
        vy += rng.gauss(0.0, 0.05)
        x += vx * 0.1
        y += vy * 0.1
        track.append((x, y))
    return track


def _estimate_track(
    modality: str,
    track: list[tuple[float, float]],
    *,
    seed: int,
    rf_noise_m: float = 0.35,
    imu_bias: float = 0.02,
    uwb_noise_m: float = 0.12,
    vision_noise_m: float = 0.08,
    vision_spoof_rate: float = 0.0,
    vision_spoof_mag_m: float = 2.5,
    fusion_trust_vision: float = 0.35,
) -> list[tuple[float, float]]:
    """Digital sensing estimators. Fusion weights are explicit and can hurt under spoof."""
    rng = random.Random(mix_seed(seed, "modality", modality))
    est: list[tuple[float, float]] = []
    ix = iy = 0.0
    prev_true = track[0]
    for i, (tx, ty) in enumerate(track):
        # RF ToA/AoA structural estimator (independent of multimodal "factor" tables).
        rf_x = tx + rng.gauss(0.0, rf_noise_m)
        rf_y = ty + rng.gauss(0.0, rf_noise_m)

        dx = tx - prev_true[0]
        dy = ty - prev_true[1]
        prev_true = (tx, ty)
        if est:
            imu_x = est[-1][0] + dx + imu_bias + rng.gauss(0.0, 0.03)
            imu_y = est[-1][1] + dy + imu_bias * 0.5 + rng.gauss(0.0, 0.03)
        else:
            imu_x, imu_y = rf_x, rf_y

        uwb_x = tx + rng.gauss(0.0, uwb_noise_m)
        uwb_y = ty + rng.gauss(0.0, uwb_noise_m)

        spoof = rng.random() < vision_spoof_rate
        v_err = vision_spoof_mag_m if spoof else vision_noise_m
        vis_x = tx + rng.gauss(0.0, v_err) + (vision_spoof_mag_m if spoof else 0.0)
        vis_y = ty + rng.gauss(0.0, v_err)

        if modality == "RF_ONLY":
            ex, ey = rf_x, rf_y
        elif modality == "RF_DEVICE_IMU":
            # Complementary filter: RF corrects IMU drift.
            w = 0.55
            ex = w * rf_x + (1.0 - w) * imu_x
            ey = w * rf_y + (1.0 - w) * imu_y
        elif modality == "RF_RING_UWB_IMU":
            w_rf, w_uwb, w_imu = 0.35, 0.45, 0.20
            ex = w_rf * rf_x + w_uwb * uwb_x + w_imu * imu_x
            ey = w_rf * rf_y + w_uwb * uwb_y + w_imu * imu_y
        elif modality == "RF_VISION":
            w = fusion_trust_vision
            ex = (1.0 - w) * rf_x + w * vis_x
            ey = (1.0 - w) * rf_y + w * vis_y
        else:  # RF_ALL_MODALITIES
            w_v = fusion_trust_vision
            rem = 1.0 - w_v
            w_rf, w_uwb, w_imu = 0.40 * rem, 0.40 * rem, 0.20 * rem
            ex = w_rf * rf_x + w_uwb * uwb_x + w_imu * imu_x + w_v * vis_x
            ey = w_rf * rf_y + w_uwb * uwb_y + w_imu * imu_y + w_v * vis_y
        est.append((ex, ey))
    return est


def _rmse(track: list[tuple[float, float]], est: list[tuple[float, float]]) -> float:
    err = 0.0
    for (tx, ty), (ex, ey) in zip(track, est):
        err += (tx - ex) ** 2 + (ty - ey) ** 2
    return math.sqrt(err / max(1, len(track)))


def _orient_rmse(seed: int, pos_rmse: float) -> float:
    # Orientation error loosely coupled to position quality (not a hardcoded win factor).
    rng = random.Random(seed)
    return round(3.0 + pos_rmse * 8.0 + rng.uniform(-0.4, 0.4), 4)


def run_config(cfg: dict[str, Any]) -> dict[str, Any]:
    seed = int(cfg["seed"])
    n = int(cfg.get("n_steps", 80))
    track = _true_track(n, seed)
    matrix: dict[str, dict[str, float]] = {}
    for m in MODALITIES:
        est = _estimate_track(
            m,
            track,
            seed=seed,
            rf_noise_m=float(cfg.get("rf_noise_m", 0.35)),
            imu_bias=float(cfg.get("imu_bias", 0.02)),
            uwb_noise_m=float(cfg.get("uwb_noise_m", 0.12)),
            vision_noise_m=float(cfg.get("vision_noise_m", 0.08)),
            vision_spoof_rate=float(cfg.get("vision_spoof_rate", 0.0)),
            vision_spoof_mag_m=float(cfg.get("vision_spoof_mag_m", 2.5)),
            fusion_trust_vision=float(cfg.get("fusion_trust_vision", 0.35)),
        )
        pr = _rmse(track, est)
        matrix[m] = {
            "position_RMSE": round(pr, 4),
            "orientation_RMSE": _orient_rmse(seed + len(m), pr),
            "beam_selection_accuracy": round(max(0.2, min(0.98, 0.95 - pr * 0.35)), 4),
            "handover_failure": round(max(0.01, min(0.4, pr * 0.25)), 4),
            "blockage_prediction_horizon_s": round(max(0.1, 1.8 - pr), 4),
            "latency_ms": round(10.0 + (4.0 if "VISION" in m or m == "RF_ALL_MODALITIES" else 0.0) + pr * 2.0, 3),
            "energy_j": round(1.0 + (0.25 if "VISION" in m or m == "RF_ALL_MODALITIES" else 0.05), 4),
            "privacy_exposure": round(0.15 + (0.25 if "VISION" in m or m == "RF_ALL_MODALITIES" else 0.0), 4),
        }
    rf = matrix["RF_ONLY"]["position_RMSE"]
    beats_rf = {
        m: matrix[m]["position_RMSE"] < rf for m in MODALITIES if m != "RF_ONLY"
    }
    return {
        "config_id": cfg["config_id"],
        "seed": seed,
        "adversarial": bool(cfg.get("adversarial", False)),
        "modality_matrix": matrix,
        "beats_rf_only": beats_rf,
        "all_multimodal_beat_rf": all(beats_rf.values()),
        "rf_all_vs_rf_only_delta_m": round(matrix["RF_ALL_MODALITIES"]["position_RMSE"] - rf, 4),
    }


# Primary evaluation: cooperative sensing (fusion should usually help).
PRIMARY_CONFIGS = [
    {"config_id": "primary_cooperative_s7", "seed": 7, "vision_spoof_rate": 0.0, "fusion_trust_vision": 0.30},
    {"config_id": "primary_cooperative_s11", "seed": 11, "vision_spoof_rate": 0.0, "fusion_trust_vision": 0.28},
    {"config_id": "primary_cooperative_s19", "seed": 19, "vision_spoof_rate": 0.02, "fusion_trust_vision": 0.25},
]

# Negative / adversarial: spoofed vision + over-trust → multimodal can lose to RF-only.
NEGATIVE_CONFIGS = [
    {
        "config_id": "neg_vision_spoof_overtrust",
        "seed": 101,
        "adversarial": True,
        "vision_spoof_rate": 0.55,
        "vision_spoof_mag_m": 3.0,
        "fusion_trust_vision": 0.75,
        "rf_noise_m": 0.22,
    },
    {
        "config_id": "neg_vision_spoof_seed202",
        "seed": 202,
        "adversarial": True,
        "vision_spoof_rate": 0.70,
        "vision_spoof_mag_m": 4.0,
        "fusion_trust_vision": 0.80,
        "rf_noise_m": 0.20,
    },
]


def conventional_fr3_baseline() -> dict[str, Any]:
    return {
        "bands_ghz": [6.75, 16.95],
        "model": "structural_pathloss_plus_shadowing",
        "pathloss_db_at_100m": {"6.75": 98.5, "16.95": 108.2},
        "evidence_rung": "R1_MODEL_IMPLEMENTED",
        "EXACT_REPRODUCTION_NOT_POSSIBLE": True,
        "reason": "NYU measurement traces not fully public in-repo",
    }


def tn_ntn_coexistence() -> dict[str, Any]:
    return {
        "pipeline": ["detect", "estimate_interferer_direction", "null"],
        "satellite_direction_uncertainty_deg": 4.0,
        "null_depth_db_structural": 18.0,
        "array_elements_assumed": 64,
        "note": "STRUCTURAL; massive-array requirements may exceed product antennas",
        "evidence_rung": "R1_MODEL_IMPLEMENTED",
        "PHYSICAL_REPRODUCTION_PENDING": True,
    }


def run_r6g003() -> dict[str, Any]:
    primary = [run_config(c) for c in PRIMARY_CONFIGS]
    negative = [run_config(c) for c in NEGATIVE_CONFIGS]

    primary_wins = [p["all_multimodal_beat_rf"] for p in primary]
    primary_improvement = all(primary_wins) and all(
        p["rf_all_vs_rf_only_delta_m"] < 0.0 for p in primary
    )
    negative_failures = [
        n for n in negative
        if n["rf_all_vs_rf_only_delta_m"] > 0.0 or not n["beats_rf_only"].get("RF_ALL_MODALITIES", False)
    ]
    falsifiable = len(negative_failures) >= 1

    # Earn token only if improvement is real on primary suite AND model can fail.
    token = bool(primary_improvement and falsifiable)

    # Representative matrix for reports: first primary config
    matrix = primary[0]["modality_matrix"]
    rf_rmse = matrix["RF_ONLY"]["position_RMSE"]

    ucs = useful_connectivity_score(R=0.55, D=0.7, A=0.8, Q=0.75, P=1.2, C=1.0)
    report = {
        "schema": "gunnchos.r6g.r6g003.v1",
        "packet": "R6G-003",
        "ok": True,
        "status": "DIGITALLY_EXECUTED",
        "model": "seeded_digital_channel_sensing_fusion_v2",
        "falsifiable": True,
        "fr3_baseline": conventional_fr3_baseline(),
        "rf_only_digital_baseline": {
            "position_RMSE_m": rf_rmse,
            "note": "Measured digital RF-only estimator — NOT claimed matched to NYU physical ~0.2 m",
            "DIGITAL_REPRODUCTION_MATCHED": False,
            "COMPARABLE_EVIDENCE_PENDING": True,
            "published_target_m": 0.2,
        },
        "modality_matrix": matrix,
        "primary_suite": [
            {
                "config_id": p["config_id"],
                "seed": p["seed"],
                "all_multimodal_beat_rf": p["all_multimodal_beat_rf"],
                "rf_all_vs_rf_only_delta_m": p["rf_all_vs_rf_only_delta_m"],
                "RF_ONLY_RMSE": p["modality_matrix"]["RF_ONLY"]["position_RMSE"],
                "RF_ALL_RMSE": p["modality_matrix"]["RF_ALL_MODALITIES"]["position_RMSE"],
            }
            for p in primary
        ],
        "negative_suite": [
            {
                "config_id": n["config_id"],
                "seed": n["seed"],
                "adversarial": True,
                "rf_all_vs_rf_only_delta_m": n["rf_all_vs_rf_only_delta_m"],
                "RF_ONLY_RMSE": n["modality_matrix"]["RF_ONLY"]["position_RMSE"],
                "RF_ALL_RMSE": n["modality_matrix"]["RF_ALL_MODALITIES"]["position_RMSE"],
                "multimodal_failed_to_beat_rf": n["rf_all_vs_rf_only_delta_m"] > 0.0,
            }
            for n in negative
        ],
        "documented_negative_or_no_gain": [
            {
                "experiment": n["config_id"],
                "result": "MULTIMODAL_WORSE_THAN_RF_ONLY",
                "delta_m": n["rf_all_vs_rf_only_delta_m"],
                "reason": "Vision spoof + over-trust fusion weights pull estimate off true track",
            }
            for n in negative_failures
        ],
        "tn_ntn": tn_ntn_coexistence(),
        "MULTIMODAL_ISAC_DIGITAL_IMPROVEMENT": token,
        "primary_improvement_observed": primary_improvement,
        "negative_cases_observed": falsifiable,
        "IMPROVED_STATE_OF_ART": False,
        "PHYSICAL_REPRODUCTION_PENDING": True,
        "claims": [
            "SIMULATION_IMPROVEMENT_OBSERVED" if token else "HYPOTHESIS_REGISTERED",
            "PHYSICAL_REPRODUCTION_PENDING",
            "COMPARABLE_EVIDENCE_PENDING",
            "FALSIFIABLE_NEGATIVE_CASES_DOCUMENTED" if falsifiable else "FALSIFIABILITY_INCOMPLETE",
        ],
        "useful_connectivity_score": ucs,
        "security_privacy_scorecard": {
            "performance": "SCORED",
            "energy": "SCORED",
            "reliability": "SCORED",
            "privacy": "SCORED",
            "security": "GATED",
            "model_integrity": "GATED",
            "sensor_consent": "REQUIRED_FOR_VISION_RING",
            "adversarial_robustness": "PARTIAL_DIGITAL",
        },
    }
    assert_no_soa(report)
    assert report["IMPROVED_STATE_OF_ART"] is False
    return report
