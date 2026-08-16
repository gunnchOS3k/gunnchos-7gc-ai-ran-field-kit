"""R6G-007 — Adaptive RIS / intelligent environment — seeded digital experiment.

Advances MODELED_CONTRACT_ONLY → DIGITALLY_EXECUTED with preregistered seeds,
negatives, and control ablations. No RIS purchase, no physical panel, no SoA.
"""
from __future__ import annotations

import math
import random
from typing import Any

from research.r6g.claim_firewall import assert_no_soa
from research.r6g.metrics.stable_seed import mix_seed

CONTRACT = {
    "elements_modeled": 64,
    "control": "PHASE_ONLY_DIGITAL",
    "channel": "SINGLE_BOUNCE_SYNTHETIC",
    "purchase_authorized": False,
    "forbidden_claims": [
        "PHYSICAL_RIS_VALIDATED",
        "PURCHASED_HARDWARE",
        "IMPROVED_STATE_OF_ART",
    ],
}

CONTROLS = ("PASSIVE_FIXED", "RANDOM_PHASE", "ADAPTIVE_PHASE")
STRESSES = (
    "static_los",
    "blocked_direct",
    "phase_quant_2bit",
    "element_failure",
    "mobility_mismatch",
)


def _path_gain(n: int, ctrl_phases: list[float], incident: list[float], rng: random.Random, *, direct: float) -> float:
    """Coherent sum of direct + RIS-reflected phasors."""
    re = direct
    im = 0.0
    amp = 1.0 / math.sqrt(max(1, n))
    for i in range(n):
        a = amp * (1.0 + rng.gauss(0.0, 0.015))
        ph = incident[i] + ctrl_phases[i]
        re += a * math.cos(ph)
        im += a * math.sin(ph)
    return math.hypot(re, im)


def _snr_db(gain: float, noise: float) -> float:
    snr_lin = max(1e-6, (gain * gain) / max(1e-6, noise))
    return 10.0 * math.log10(snr_lin)


def _ctrl_phases(
    control: str,
    n: int,
    incident: list[float],
    rng: random.Random,
    *,
    quant_bits: int | None,
    failed: set[int],
    mismatch_per_element: list[float] | None = None,
) -> list[float]:
    phases: list[float] = []
    mm = mismatch_per_element or [0.0] * n
    for i in range(n):
        if i in failed:
            phases.append(0.0)
            continue
        if control == "PASSIVE_FIXED":
            ph = 0.0
        elif control == "RANDOM_PHASE":
            ph = rng.uniform(-math.pi, math.pi)
        else:
            # Align reflected path to common phase 0 (oracle digital phase conjugation)
            ph = -incident[i] + mm[i]
        if quant_bits is not None:
            levels = 2 ** quant_bits
            step = 2 * math.pi / levels
            ph = round(ph / step) * step
        phases.append(ph)
    return phases


def run_r6g007(seed: int = 11) -> dict[str, Any]:
    n = int(CONTRACT["elements_modeled"])
    results: dict[str, dict[str, float]] = {}
    negatives: list[dict[str, Any]] = []

    for stress in STRESSES:
        rng = random.Random(mix_seed(seed, "r6g007", stress))
        incident = [rng.uniform(-math.pi, math.pi) for _ in range(n)]
        direct = 0.35 if stress != "blocked_direct" else 0.04
        noise = 0.08
        quant = 2 if stress == "phase_quant_2bit" else None
        failed: set[int] = set()
        mismatch = [0.0] * n
        if stress == "element_failure":
            failed = set(rng.sample(range(n), max(1, n // 3)))
        if stress == "mobility_mismatch":
            # Per-element stale conjugation error (global offset would still be coherent)
            mismatch = [rng.uniform(-math.pi, math.pi) for _ in range(n)]
            noise = 0.14
        if stress == "phase_quant_2bit":
            noise = 0.12

        row: dict[str, float] = {}
        for ctrl in CONTROLS:
            crng = random.Random(mix_seed(seed, "r6g007", stress, ctrl))
            phases = _ctrl_phases(
                ctrl,
                n,
                incident,
                crng,
                quant_bits=quant,
                failed=failed,
                mismatch_per_element=mismatch,
            )
            g = _path_gain(n, phases, incident, crng, direct=direct)
            row[ctrl] = round(_snr_db(g, noise), 6)
        results[stress] = row

        if row["ADAPTIVE_PHASE"] <= row["PASSIVE_FIXED"] + 1e-9:
            negatives.append({
                "stress": stress,
                "result": "ADAPTIVE_NO_GAIN_VS_PASSIVE",
                "adaptive": row["ADAPTIVE_PHASE"],
                "passive": row["PASSIVE_FIXED"],
                "delta_db": round(row["ADAPTIVE_PHASE"] - row["PASSIVE_FIXED"], 6),
            })
        if row["ADAPTIVE_PHASE"] <= row["RANDOM_PHASE"] + 1e-9:
            negatives.append({
                "stress": stress,
                "result": "ADAPTIVE_NO_GAIN_VS_RANDOM",
                "adaptive": row["ADAPTIVE_PHASE"],
                "random": row["RANDOM_PHASE"],
            })

    static = results["static_los"]
    delta_db = round(static["ADAPTIVE_PHASE"] - static["PASSIVE_FIXED"], 6)
    hypothesis = delta_db > 0.0 and len(negatives) >= 1

    report = {
        "schema": "gunnchos.r6g.r6g007.v1",
        "packet": "R6G-007",
        "ok": True,
        "status": "DIGITALLY_EXECUTED",
        "claim_state": "DIGITALLY_EXECUTED",
        "execution_class": "SEEDED_DIGITAL_SIMULATOR",
        "seed": seed,
        "contract": CONTRACT,
        "controls": list(CONTROLS),
        "stresses": list(STRESSES),
        "results_snr_db": results,
        "static_los": static,
        "delta_adaptive_minus_passive_db": delta_db,
        "documented_negative_or_no_gain": negatives,
        "HYPOTHESIS_SUPPORTED_DIGITALLY": hypothesis,
        "ladder_earned": ["R0", "R1", "R2"],
        "PHYSICAL_REPRODUCTION_PENDING": True,
        "RIS_PURCHASE": False,
        "IMPROVED_STATE_OF_ART": False,
        "note": (
            "Seeded RIS phase-control digital experiment only; "
            "no physical purchase or panel validation this cycle."
        ),
    }
    assert_no_soa(report)
    return report
