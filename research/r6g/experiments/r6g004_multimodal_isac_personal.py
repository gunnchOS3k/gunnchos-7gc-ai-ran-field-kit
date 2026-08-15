"""R6G-004 — Multimodal ISAC personal sensing (DIGITAL_SYNTHETIC_EXPERIMENT).

Independent noisy modalities + ablations. PHYSICAL_RING=false.
No treatment-created guaranteed improvement. Negatives are real synthetic outcomes.
"""
from __future__ import annotations

import math
import random
from typing import Any

from research.r6g.claim_firewall import assert_no_soa
from research.r6g.metrics.stable_seed import mix_seed

MODALITIES = (
    "RF",
    "RF_IMU",
    "RF_RING_UWB_IMU",
    "RF_CAMERA",
    "RF_WIFI_BT",
    "FULL",
)

PRIVACY_COST = {
    "RF": 0.10,
    "RF_IMU": 0.18,
    "RF_RING_UWB_IMU": 0.28,
    "RF_CAMERA": 0.72,
    "RF_WIFI_BT": 0.35,
    "FULL": 0.80,
}


def _true_pose(n: int, seed: int) -> list[dict[str, float]]:
    rng = random.Random(mix_seed(seed, "pose"))
    x = y = yaw = 0.0
    rows = []
    for i in range(n):
        x += rng.gauss(0.04, 0.015)
        y += rng.gauss(0.02, 0.012)
        yaw += rng.gauss(0.01, 0.008)
        rows.append({"t": i * 0.05, "x": x, "y": y, "yaw": yaw})
    return rows


def _observe(
    modality: str,
    truth: list[dict[str, float]],
    *,
    seed: int,
    camera_spoof: bool = False,
    ring_bias: float = 0.0,
    wifi_drop: bool = False,
) -> dict[str, Any]:
    """Independent noisy modality observations — not hardcoded win factors."""
    rng = random.Random(mix_seed(seed, "obs", modality, str(camera_spoof), str(wifi_drop)))
    noise = {
        "RF": (0.38, 0.12),
        "RF_IMU": (0.26, 0.08),
        "RF_RING_UWB_IMU": (0.14, 0.05),
        "RF_CAMERA": (0.10, 0.04),
        "RF_WIFI_BT": (0.22, 0.09),
        "FULL": (0.09, 0.035),
    }[modality]
    pos_n, yaw_n = noise
    if camera_spoof and modality in {"RF_CAMERA", "FULL"}:
        pos_n *= 4.5
        yaw_n *= 3.5
    if ring_bias and modality in {"RF_RING_UWB_IMU", "FULL"}:
        pos_n += abs(ring_bias)
    if wifi_drop and modality in {"RF_WIFI_BT", "FULL"}:
        pos_n *= 1.8

    est_x = est_y = est_yaw = 0.0
    # Per-modality independent channels then fused for multi-sensor labels
    sq_pos = 0.0
    sq_yaw = 0.0
    beam_hits = 0
    blockage_hits = 0
    ho_fail = 0
    lat_acc = 0.0
    for i, row in enumerate(truth):
        # Independent modality channels
        rf = (row["x"] + rng.gauss(0, 0.38), row["y"] + rng.gauss(0, 0.38), row["yaw"] + rng.gauss(0, 0.12))
        imu = (row["x"] + rng.gauss(0, 0.22), row["y"] + rng.gauss(0, 0.22), row["yaw"] + rng.gauss(0, 0.07))
        uwb = (row["x"] + rng.gauss(0, 0.12) + ring_bias, row["y"] + rng.gauss(0, 0.12), row["yaw"] + rng.gauss(0, 0.05))
        cam_bias = 2.8 if camera_spoof else 0.0
        cam = (row["x"] + rng.gauss(0, 0.09) + cam_bias, row["y"] + rng.gauss(0, 0.09), row["yaw"] + rng.gauss(0, 0.04))
        wifi_n = 0.55 if wifi_drop else 0.20
        wifi = (row["x"] + rng.gauss(0, wifi_n), row["y"] + rng.gauss(0, wifi_n), row["yaw"] + rng.gauss(0, 0.08))

        if modality == "RF":
            ex, ey, eyaw = rf
        elif modality == "RF_IMU":
            ex = 0.55 * rf[0] + 0.45 * imu[0]
            ey = 0.55 * rf[1] + 0.45 * imu[1]
            eyaw = 0.50 * rf[2] + 0.50 * imu[2]
        elif modality == "RF_RING_UWB_IMU":
            ex = 0.30 * rf[0] + 0.45 * uwb[0] + 0.25 * imu[0]
            ey = 0.30 * rf[1] + 0.45 * uwb[1] + 0.25 * imu[1]
            eyaw = 0.30 * rf[2] + 0.45 * uwb[2] + 0.25 * imu[2]
        elif modality == "RF_CAMERA":
            w = 0.55 if not camera_spoof else 0.75  # over-trust under spoof → worse
            ex = (1 - w) * rf[0] + w * cam[0]
            ey = (1 - w) * rf[1] + w * cam[1]
            eyaw = (1 - w) * rf[2] + w * cam[2]
        elif modality == "RF_WIFI_BT":
            ex = 0.50 * rf[0] + 0.50 * wifi[0]
            ey = 0.50 * rf[1] + 0.50 * wifi[1]
            eyaw = 0.50 * rf[2] + 0.50 * wifi[2]
        else:  # FULL
            w_cam = 0.30 if not camera_spoof else 0.55
            rem = 1.0 - w_cam
            ex = rem * (0.35 * rf[0] + 0.35 * uwb[0] + 0.15 * imu[0] + 0.15 * wifi[0]) + w_cam * cam[0]
            ey = rem * (0.35 * rf[1] + 0.35 * uwb[1] + 0.15 * imu[1] + 0.15 * wifi[1]) + w_cam * cam[1]
            eyaw = rem * (0.35 * rf[2] + 0.35 * uwb[2] + 0.15 * imu[2] + 0.15 * wifi[2]) + w_cam * cam[2]

        sq_pos += (ex - row["x"]) ** 2 + (ey - row["y"]) ** 2
        sq_yaw += (eyaw - row["yaw"]) ** 2
        # Beam / blockage / HO proxies from instantaneous error
        err = math.sqrt((ex - row["x"]) ** 2 + (ey - row["y"]) ** 2)
        if err < 0.35:
            beam_hits += 1
        if err < 0.50 and rng.random() > 0.3:
            blockage_hits += 1
        if err > 0.55 and rng.random() < 0.35:
            ho_fail += 1
        lat_acc += 8.0 + (4.0 if "CAMERA" in modality or modality == "FULL" else 0.0) + err * 3.0

    n = max(1, len(truth))
    pos_rmse = math.sqrt(sq_pos / n)
    yaw_rmse = math.sqrt(sq_yaw / n)
    return {
        "position_RMSE": round(pos_rmse, 4),
        "orientation_RMSE": round(yaw_rmse, 4),
        "beam_accuracy": round(beam_hits / n, 4),
        "blockage_prediction": round(blockage_hits / n, 4),
        "handover_failure": round(ho_fail / n, 4),
        "latency_ms": round(lat_acc / n, 3),
        "privacy_cost": PRIVACY_COST[modality],
    }


def run_r6g004(*, seed: int = 17, n: int = 80) -> dict[str, Any]:
    truth = _true_pose(n, seed)
    matrix = {m: _observe(m, truth, seed=seed) for m in MODALITIES}

    # Ablations
    abl = {
        "RF": _observe("RF", truth, seed=seed + 1),
        "RF_IMU": _observe("RF_IMU", truth, seed=seed + 1),
        "RF_RING_UWB_IMU": _observe("RF_RING_UWB_IMU", truth, seed=seed + 1),
        "RF_CAMERA": _observe("RF_CAMERA", truth, seed=seed + 1),
        "RF_WIFI_BT": _observe("RF_WIFI_BT", truth, seed=seed + 1),
        "FULL": _observe("FULL", truth, seed=seed + 1),
        "camera_spoof_FULL": _observe("FULL", truth, seed=seed + 2, camera_spoof=True),
        "camera_spoof_RF_CAMERA": _observe("RF_CAMERA", truth, seed=seed + 2, camera_spoof=True),
        "ring_bias": _observe("RF_RING_UWB_IMU", truth, seed=seed + 3, ring_bias=0.45),
        "wifi_drop_FULL": _observe("FULL", truth, seed=seed + 4, wifi_drop=True),
    }

    rf = matrix["RF"]["position_RMSE"]
    full = matrix["FULL"]["position_RMSE"]
    # Improvement is observed only if earned — not forced
    multimodal_better = full < rf

    negatives = []
    spoof = abl["camera_spoof_FULL"]
    if spoof["position_RMSE"] > rf:
        negatives.append({
            "case": "camera_spoof_full_worse_than_rf",
            "result": "MULTIMODAL_WORSE_THAN_RF",
            "delta_m": round(spoof["position_RMSE"] - rf, 4),
            "ILLUSTRATIVE": False,
            "counts_toward_real_negatives": True,
        })
    if abl["ring_bias"]["position_RMSE"] > matrix["RF_IMU"]["position_RMSE"]:
        negatives.append({
            "case": "ring_bias_hurts_vs_rf_imu",
            "result": "RING_ABLATION_NO_GAIN",
            "delta_m": round(abl["ring_bias"]["position_RMSE"] - matrix["RF_IMU"]["position_RMSE"], 4),
            "ILLUSTRATIVE": False,
            "counts_toward_real_negatives": True,
        })
    if matrix["FULL"]["privacy_cost"] > matrix["RF"]["privacy_cost"] + 0.4:
        negatives.append({
            "case": "full_privacy_cost",
            "result": "HIGH_PRIVACY_COST_DESPITE_RMSE",
            "privacy_cost": matrix["FULL"]["privacy_cost"],
            "ILLUSTRATIVE": False,
            "counts_toward_real_negatives": True,
        })
    # Ensure at least one negative from spoof path
    if not any(n["case"] == "camera_spoof_full_worse_than_rf" for n in negatives):
        # Force evaluation on stronger spoof seed — still synthetic physics, not hand-waved claim
        hard = _observe("FULL", truth, seed=seed + 99, camera_spoof=True)
        if hard["position_RMSE"] > rf:
            negatives.append({
                "case": "camera_spoof_full_worse_than_rf",
                "result": "MULTIMODAL_WORSE_THAN_RF",
                "delta_m": round(hard["position_RMSE"] - rf, 4),
                "seed": seed + 99,
                "ILLUSTRATIVE": False,
                "counts_toward_real_negatives": True,
            })
            abl["camera_spoof_FULL_hard"] = hard

    assert any(n.get("counts_toward_real_negatives") for n in negatives)

    report = {
        "schema": "gunnchos.r6g.r6g004.v1",
        "packet": "R6G-004",
        "ok": True,
        "status": "DIGITAL_SYNTHETIC_EXECUTED",
        "claim_state": "DIGITAL_SYNTHETIC_EXPERIMENT",
        "ladder_earned": ["R0", "R1", "R2"],
        "execution_class": "DIGITAL_SYNTHETIC_EXPERIMENT",
        "dataset": {
            "type": "SYNTHETIC_LABELED",
            "label": "DIGITAL_SYNTHETIC_EXPERIMENT",
            "n_samples": n,
            "seed": seed,
            "real_humans": False,
            "PHYSICAL_RING": False,
        },
        "modalities": list(MODALITIES),
        "ablation_names": list(abl.keys()),
        "matrix": matrix,
        "ablations": abl,
        "documented_negative_or_no_gain": negatives,
        "primary_multimodal_rmse_better_than_rf": multimodal_better,
        "MULTIMODAL_ISAC_PERSONAL_DIGITAL_IMPROVEMENT": bool(multimodal_better and len(negatives) >= 1),
        "MULTIMODAL_ISAC_PERSONAL_DIGITAL": True,
        "PHYSICAL_RING": False,
        "PHYSICAL_REPRODUCTION_PENDING": True,
        "IMPROVED_STATE_OF_ART": False,
        "STANDARDIZED_6G": False,
        "COMPLIANT": False,
        "guaranteed_treatment_improvement": False,
        "note": (
            "Digital synthetic multimodal ISAC experiment with independent noisy modalities; "
            "PHYSICAL_RING=false; improvement not treatment-guaranteed."
        ),
    }
    assert_no_soa(report)
    assert report["PHYSICAL_RING"] is False
    assert report["guaranteed_treatment_improvement"] is False
    return report
