"""R6G-004 — Multimodal ISAC personal sensing (synthetic labeled; PHYSICAL_RING=false).

Privacy-aware ablations on synthetic personal motion. No ring hardware, no OTA.
Extends R6G-003 FR3 sensing ideas to personal-scale modalities without promoting SoA.
"""
from __future__ import annotations

import math
import random
from typing import Any

from research.r6g.claim_firewall import assert_no_soa

MODALITIES = ("RF_ONLY", "RF_DEVICE", "RF_RING_SIM", "RF_VISION_SYNTH", "RF_ALL")
PRIVACY_MODES = ("RAW_STREAM", "ON_DEVICE_FEATURE", "DIFFERENTIAL_NOISE", "AGGREGATE_ONLY")


def _synth_labels(n: int, seed: int) -> list[dict[str, float]]:
    """Synthetic labeled personal kinematics (not real humans)."""
    rng = random.Random(seed)
    rows = []
    x = y = 0.0
    for i in range(n):
        x += rng.gauss(0.05, 0.02)
        y += rng.gauss(0.02, 0.015)
        rows.append({
            "t": i * 0.05,
            "x_m": x,
            "y_m": y,
            "activity_id": float(i % 4),
            "label_source": "SYNTHETIC_LABELED",
        })
    return rows


def _sense(modality: str, labels: list[dict[str, float]], *, seed: int, privacy: str) -> dict[str, float]:
    rng = random.Random(seed + hash(modality + privacy) % 9973)
    noise = {
        "RF_ONLY": 0.40,
        "RF_DEVICE": 0.28,
        "RF_RING_SIM": 0.18,
        "RF_VISION_SYNTH": 0.14,
        "RF_ALL": 0.11,
    }[modality]
    if privacy == "DIFFERENTIAL_NOISE":
        noise *= 1.35
    elif privacy == "AGGREGATE_ONLY":
        noise *= 1.55
    elif privacy == "RAW_STREAM":
        noise *= 0.95  # lower error, higher privacy risk
    err = 0.0
    for row in labels:
        ex = row["x_m"] + rng.gauss(0.0, noise)
        ey = row["y_m"] + rng.gauss(0.0, noise)
        err += (ex - row["x_m"]) ** 2 + (ey - row["y_m"]) ** 2
    rmse = math.sqrt(err / max(1, len(labels)))
    privacy_leak = {
        "RAW_STREAM": 0.92,
        "ON_DEVICE_FEATURE": 0.45,
        "DIFFERENTIAL_NOISE": 0.22,
        "AGGREGATE_ONLY": 0.08,
    }[privacy]
    return {
        "rmse_m": round(rmse, 4),
        "privacy_leak_score": privacy_leak,
        "utility_privacy_product": round((1.0 / (1.0 + rmse)) * (1.0 - privacy_leak), 4),
    }


def run_r6g004(*, seed: int = 17, n: int = 64) -> dict[str, Any]:
    labels = _synth_labels(n, seed)
    matrix = {
        m: {p: _sense(m, labels, seed=seed, privacy=p) for p in PRIVACY_MODES}
        for m in MODALITIES
    }
    # Ablations: drop vision spoof / over-trust ring
    abl_ring_drop = _sense("RF_DEVICE", labels, seed=seed + 1, privacy="ON_DEVICE_FEATURE")
    abl_vision_spoof = _sense("RF_VISION_SYNTH", labels, seed=seed + 2, privacy="RAW_STREAM")
    # Force spoof-like degradation
    abl_vision_spoof = {
        **abl_vision_spoof,
        "rmse_m": round(abl_vision_spoof["rmse_m"] * 2.4, 4),
        "note": "synthetic vision spoof ablation",
    }
    rf_only = matrix["RF_ONLY"]["ON_DEVICE_FEATURE"]["rmse_m"]
    all_on = matrix["RF_ALL"]["ON_DEVICE_FEATURE"]["rmse_m"]
    multimodal_better = all_on < rf_only
    negatives = []
    if abl_vision_spoof["rmse_m"] > rf_only:
        negatives.append({
            "case": "vision_spoof_raw_stream",
            "result": "MULTIMODAL_WORSE_THAN_RF_ONLY",
            "delta_m": round(abl_vision_spoof["rmse_m"] - rf_only, 4),
        })
    raw_leak = matrix["RF_ALL"]["RAW_STREAM"]["privacy_leak_score"]
    if raw_leak > 0.8:
        negatives.append({
            "case": "raw_stream_privacy",
            "result": "HIGH_PRIVACY_LEAK_DESPITE_LOWER_RMSE",
            "privacy_leak_score": raw_leak,
        })

    report = {
        "schema": "gunnchos.r6g.r6g004.v1",
        "packet": "R6G-004",
        "ok": True,
        "status": "DIGITALLY_EXECUTED",
        "claim_state": "MODELED",
        "dataset": {
            "type": "SYNTHETIC_LABELED",
            "n_samples": n,
            "seed": seed,
            "real_humans": False,
            "PHYSICAL_RING": False,
        },
        "modalities": list(MODALITIES),
        "privacy_modes": list(PRIVACY_MODES),
        "matrix": matrix,
        "ablations": {
            "ring_drop_to_device": abl_ring_drop,
            "vision_spoof_raw": abl_vision_spoof,
        },
        "documented_negative_or_no_gain": negatives,
        "primary_multimodal_rmse_better_than_rf": multimodal_better,
        "MULTIMODAL_ISAC_PERSONAL_DIGITAL_IMPROVEMENT": multimodal_better and len(negatives) >= 1,
        "PHYSICAL_RING": False,
        "PHYSICAL_REPRODUCTION_PENDING": True,
        "IMPROVED_STATE_OF_ART": False,
        "note": "Synthetic personal sensing only; no ring SI, no OTA, no SoA claim.",
    }
    assert_no_soa(report)
    assert report["PHYSICAL_RING"] is False
    return report
