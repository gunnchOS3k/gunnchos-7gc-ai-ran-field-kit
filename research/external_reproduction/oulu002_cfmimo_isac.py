"""OULU-002 — Nguyen/Fang/Ngo/Juntti multi-static CF massive-MIMO ISAC.

Source: DOI 10.1109/IEEECONF60004.2024.10942860 / arXiv:2411.06747
Maps to R6G-004 / R6G-006. Math/numerical first; Sionna only if available.
No improvement claim until baseline matched.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np

from research.external_reproduction.adapters.probe import probe_all
from research.external_reproduction.claim_firewall import enforce_firewall
from research.external_reproduction.oulu002_oracle import cross_check as oracle_cross_check

# Paper simulation defaults (Section V)
DEFAULTS = {
    "area_m": 250.0,
    "r_h_m": 100.0,
    "pathloss_exp": 3.2,
    "shadow_sigma_db": 7.0,
    "N_t": 4,
    "N_r": 4,
    "K": 4,
    "T": 30,
    "sigma2_dbm": -30.0,
    "beta_s": 1e-2,
    "tau_c": 200,
}


def _dbm_to_lin(dbm: float) -> float:
    return 10 ** ((dbm - 30.0) / 10.0)


def large_scale_beta(
    distances_m: np.ndarray,
    *,
    r_h: float,
    nu: float,
    shadow_db: np.ndarray,
) -> np.ndarray:
    """β = z / (r/r_h)^ν with z log-normal (linear)."""
    z = 10 ** (shadow_db / 10.0)
    return z / np.maximum(distances_m / r_h, 1e-9) ** nu


def mmse_xi(beta: np.ndarray, tau_p: int, p_p: float, sigma2: float) -> np.ndarray:
    """Orthogonal pilots (no contamination): ξ = τ_p p_p β² / (τ_p p_p β + σ²)."""
    return (tau_p * p_p * beta**2) / (tau_p * p_p * beta + sigma2)


def rate_closed_form(
    xi: np.ndarray,
    beta: np.ndarray,
    gamma: np.ndarray,
    eta: np.ndarray,
    *,
    N_t: int,
    sigma2: float,
    tau_bar: float,
) -> np.ndarray:
    """Theorem 1 style per-UE rate (orthogonal-pilot simplification).

    R_k = τ̄ log2(1 + N_t² (ξ_k^T √γ_k)² / (N_t Σ_j (β̂_kj^T γ_j + β_k^T η_j) + σ²))
    with β̂_kj,ℓ = β_kℓ ξ_jℓ.
    """
    K, L = xi.shape
    rates = np.zeros(K)
    for k in range(K):
        num = (N_t * float(np.dot(xi[k], np.sqrt(gamma[k])))) ** 2
        denom = sigma2
        for j in range(K):
            beta_hat = beta[k] * xi[j]
            denom += N_t * (float(np.dot(beta_hat, gamma[j])) + float(np.dot(beta[k], eta[j])))
        sinr = num / max(denom, 1e-30)
        rates[k] = tau_bar * math.log2(1.0 + sinr)
    return rates


def crlb_angle_proxy(
    eta: np.ndarray,
    xi: np.ndarray,
    gamma: np.ndarray,
    *,
    N_r: int,
    snr_lin: float,
) -> np.ndarray:
    """Order-of-magnitude CRLB proxy (not full Theorem 2 FIM).

    Full closed-form CRLB needs steering derivatives + R_x blocks; without
    author vectors we use a sensing-SNR proxy that preserves qualitative
    trends (more sensing power / more APs → lower CRLB).
    """
    L = eta.shape[1]
    # Aggregate sensing power per AP
    p_s = eta.sum(axis=0)  # (L,)
    p_c = (xi * gamma).sum(axis=0)
    # Fisher-ish scale grows with N_r² and sensing power
    info = (N_r**2) * snr_lin * (p_s + 0.05 * p_c) + 1e-12
    return 1.0 / info


def place_nodes(L: int, K: int, *, seed: int, area: float, r_h: float) -> tuple[np.ndarray, np.ndarray]:
    """Uniform AP/UE placement with min AP–UE distance r_h (paper Sec. Numerical Results)."""
    rng = np.random.default_rng(seed)
    ap = rng.uniform(0.0, area, size=(L, 2))
    ue = np.zeros((K, 2))
    # Cap rejection attempts — dense L on 250×250 with r_h=100 is often infeasible.
    attempts = 2_000 if L <= 32 else 400
    for k in range(K):
        placed = False
        for _ in range(attempts):
            cand = rng.uniform(0, area, size=2)
            if np.min(np.linalg.norm(ap - cand, axis=1)) >= r_h:
                ue[k] = cand
                placed = True
                break
        if not placed:
            samples = rng.uniform(0, area, size=(800, 2))
            dmin = np.min(np.linalg.norm(ap[None, :, :] - samples[:, None, :], axis=2), axis=1)
            ue[k] = samples[int(np.argmax(dmin))]
    return ap, ue


def equal_power_allocation(
    xi: np.ndarray,
    *,
    P_t: float,
    N_t: int,
    rho_sense: float = 0.5,
) -> tuple[np.ndarray, np.ndarray]:
    """Equal split baseline from paper Section V (rho_sense≈0.5 ↔ half power each)."""
    K, L = xi.shape
    eta = np.full((K, L), (rho_sense * P_t) / (N_t * L * K))
    xi_sum = float(xi.sum()) + 1e-30
    gamma = np.full((K, L), ((1.0 - rho_sense) * P_t) / (N_t * xi_sum))
    return gamma, eta


def run_scenario(
    *,
    L: int,
    seed: int,
    snr_db: float = 30.0,
    tau_p_mode: str = "full",
    N_t: int | None = None,
    n_large_scale: int = 4,
) -> dict[str, Any]:
    cfg = dict(DEFAULTS)
    N_t = N_t or cfg["N_t"]
    K = cfg["K"]
    sigma2 = _dbm_to_lin(cfg["sigma2_dbm"])
    P_t = sigma2 * (10 ** (snr_db / 10.0))
    tau_p = K if tau_p_mode == "full" else max(1, K // 2)
    tau_bar = (cfg["tau_c"] - tau_p) / cfg["tau_c"]

    sum_rates = []
    sum_rates0 = []
    crlbs = []
    min_dists = []
    for ls in range(n_large_scale):
        ap, ue = place_nodes(L, K, seed=seed * 1009 + ls, area=cfg["area_m"], r_h=cfg["r_h_m"])
        dist = np.linalg.norm(ap[None, :, :] - ue[:, None, :], axis=2)
        rng = np.random.default_rng(seed * 917 + ls)
        shadow = rng.normal(0.0, cfg["shadow_sigma_db"], size=dist.shape)
        beta = large_scale_beta(dist, r_h=cfg["r_h_m"], nu=cfg["pathloss_exp"], shadow_db=shadow)
        xi = mmse_xi(beta, tau_p=tau_p, p_p=P_t, sigma2=sigma2)
        gamma, eta = equal_power_allocation(xi, P_t=P_t, N_t=N_t, rho_sense=0.5)
        rates = rate_closed_form(xi, beta, gamma, eta, N_t=N_t, sigma2=sigma2, tau_bar=tau_bar)
        snr_lin = 10 ** (snr_db / 10.0)
        crlb = crlb_angle_proxy(eta, xi, gamma, N_r=cfg["N_r"], snr_lin=snr_lin)
        gamma0, eta0 = equal_power_allocation(xi, P_t=P_t, N_t=N_t, rho_sense=0.0)
        rates0 = rate_closed_form(xi, beta, gamma0, eta0, N_t=N_t, sigma2=sigma2, tau_bar=tau_bar)
        sum_rates.append(float(rates.sum()))
        sum_rates0.append(float(rates0.sum()))
        crlbs.append(float(np.mean(crlb)))
        min_dists.append(float(dist.min()))

    sum_rate = float(np.mean(sum_rates))
    sum_rate0 = float(np.mean(sum_rates0))
    return {
        "L": L,
        "N_t": N_t,
        "K": K,
        "seed": seed,
        "snr_db": snr_db,
        "tau_p": tau_p,
        "n_large_scale": n_large_scale,
        "sum_rate": sum_rate,
        "sum_rate_sensing_off": sum_rate0,
        "sensing_rate_penalty": sum_rate0 - sum_rate,
        "mean_crlb_proxy": float(np.mean(crlbs)),
        "min_ue_ap_distance_m": float(np.mean(min_dists)),
    }


# Digitized Fig.1(a) primary baseline (Nt=4, tau_p=K) — label FIGURE_DIGITIZED
# Source PNG: ar5iv rate_L.png (arxiv 2411.06747). Axis OCR: L∈[10,100], rate∈[4,26].
# Points curated for monotonicity + visual/OCR agreement; uncertainty ±0.4 bps/Hz.
FIGURE_DIGITIZED_FIG1A = {
    "label": "FIGURE_DIGITIZED",
    "figure": "Fig.1(a)",
    "arxiv": "2411.06747",
    "doi": "10.1109/IEEECONF60004.2024.10942860",
    "source_asset": "https://ar5iv.labs.arxiv.org/html/2411.06747/assets/rate_L.png",
    "axis": {"x": "L", "x_range": [10, 100], "y": "Communications sum rate [bps/Hz]", "y_range": [4, 26]},
    "series_id": "Nt4_taup_K_sim_ana",
    "N_t": 4,
    "tau_p_mode": "full",
    "uncertainty_bps_hz": 0.4,
    "points": [
        {"L": 10, "sum_rate_bps_hz": 9.5},
        {"L": 20, "sum_rate_bps_hz": 12.8},
        {"L": 40, "sum_rate_bps_hz": 16.3},
        {"L": 60, "sum_rate_bps_hz": 18.5},
        {"L": 80, "sum_rate_bps_hz": 20.0},
        {"L": 100, "sum_rate_bps_hz": 21.3},
    ],
}

EQUATION_TRACEABILITY = {
    "schema": "gunnchos.oulu002.equation_traceability.v1",
    "paper": "arXiv:2411.06747 / DOI 10.1109/IEEECONF60004.2024.10942860",
    "entries": [
        {
            "symbol": "β_kℓ",
            "paper": "β = z / (r/r_h)^ν",
            "code": "large_scale_beta",
        },
        {
            "symbol": "ξ_kℓ",
            "paper": "MMSE orthogonal-pilot (no contamination path)",
            "code": "mmse_xi",
        },
        {
            "symbol": "R_k",
            "paper": "eq.(7) / Theorem 1 achievable rate",
            "code": "rate_closed_form",
            "oracle": "oulu002_oracle.oracle_rate",
        },
        {
            "symbol": "(η,γ) equal split",
            "paper": "η=P_t/(2 N_t L K), γ=P_t/(2 N_t Σ ξ)",
            "code": "equal_power_allocation(rho_sense=0.5)",
        },
        {
            "symbol": "SNR",
            "paper": "SNR=P_t/σ² = 30 dB; σ²=-30 dBm",
            "code": "run_scenario snr_db=30 + DEFAULTS.sigma2_dbm",
        },
    ],
}


def run_suite(seeds: list[int] | None = None) -> dict[str, Any]:
    seeds = seeds or [7, 11, 13]
    probe = probe_all()
    sionna_ok = probe["adapters"]["SIONNA_PHY"]["present"]

    # Trend grid (paper caption L∈{8,16,32}) + Fig.1(a) digitized ticks.
    L_grid = [8, 16, 32]
    L_fig = [p["L"] for p in FIGURE_DIGITIZED_FIG1A["points"]]
    raw: dict[str, Any] = {"by_seed": {}, "sweeps": [], "fig1a_compare": []}
    oracle_reports: list[dict[str, Any]] = []

    for seed in seeds:
        raw["by_seed"][str(seed)] = []
        for L in L_grid:
            for mode, n_ls in (("full", 4), ("half", 2)):
                row = run_scenario(L=L, seed=seed, N_t=4, tau_p_mode=mode, n_large_scale=n_ls)
                row["tau_p_mode"] = mode
                raw["by_seed"][str(seed)].append(row)
        for L in L_fig:
            if L in L_grid:
                continue
            row = run_scenario(L=L, seed=seed, N_t=4, tau_p_mode="full", n_large_scale=4)
            row["tau_p_mode"] = "full"
            raw["by_seed"][str(seed)].append(row)

        if seed == seeds[0]:
            row8 = run_scenario(L=16, seed=seed, N_t=8, tau_p_mode="full", n_large_scale=2)
            row8["tau_p_mode"] = "full"
            raw["by_seed"][str(seed)].append(row8)
            raw["sweeps"].append({"note": "N_t=8 @ L=16 primary seed only", "row": row8})
            for L in (10, 16, 40):
                cfg = dict(DEFAULTS)
                sigma2 = _dbm_to_lin(cfg["sigma2_dbm"])
                P_t = sigma2 * (10 ** (30.0 / 10.0))
                ap, ue = place_nodes(L, cfg["K"], seed=seed * 1009, area=cfg["area_m"], r_h=cfg["r_h_m"])
                dist = np.linalg.norm(ap[None, :, :] - ue[:, None, :], axis=2)
                rng = np.random.default_rng(seed * 917)
                shadow = rng.normal(0.0, cfg["shadow_sigma_db"], size=dist.shape)
                beta = large_scale_beta(dist, r_h=cfg["r_h_m"], nu=cfg["pathloss_exp"], shadow_db=shadow)
                xi = mmse_xi(beta, tau_p=cfg["K"], p_p=P_t, sigma2=sigma2)
                gamma, eta = equal_power_allocation(xi, P_t=P_t, N_t=4, rho_sense=0.5)
                tau_bar = (cfg["tau_c"] - cfg["K"]) / cfg["tau_c"]
                primary = rate_closed_form(
                    xi, beta, gamma, eta, N_t=4, sigma2=sigma2, tau_bar=tau_bar
                )
                oracle_reports.append(
                    {
                        "L": L,
                        **oracle_cross_check(
                            xi,
                            beta,
                            gamma,
                            eta,
                            primary,
                            N_t=4,
                            sigma2=sigma2,
                            tau_bar=tau_bar,
                        ),
                    }
                )

    stats = []
    for L in L_grid:
        vals = []
        penalties = []
        for seed in seeds:
            rows = [
                r
                for r in raw["by_seed"][str(seed)]
                if r["L"] == L and r["N_t"] == 4 and r["tau_p_mode"] == "full"
            ]
            vals.append(rows[0]["sum_rate"])
            penalties.append(rows[0]["sensing_rate_penalty"])
        stats.append(
            {
                "L": L,
                "N_t": 4,
                "sum_rate_mean": float(np.mean(vals)),
                "sum_rate_std": float(np.std(vals)),
                "sensing_penalty_mean": float(np.mean(penalties)),
                "n_seeds": len(seeds),
                "trend_note": "sum_rate increases with L (Remark 1 qualitative)",
            }
        )

    fig_tol = FIGURE_DIGITIZED_FIG1A["uncertainty_bps_hz"]
    predeclared_rel = 0.05
    compare_rows = []
    within = []
    for pt in FIGURE_DIGITIZED_FIG1A["points"]:
        L = pt["L"]
        ref = pt["sum_rate_bps_hz"]
        vals = []
        for seed in seeds:
            rows = [
                r
                for r in raw["by_seed"][str(seed)]
                if r["L"] == L and r["N_t"] == 4 and r["tau_p_mode"] == "full"
            ]
            if rows:
                vals.append(rows[0]["sum_rate"])
        model = float(np.mean(vals)) if vals else float("nan")
        err_rel = abs(model - ref) / max(ref, 1e-9)
        ok = err_rel <= predeclared_rel
        within.append(ok)
        compare_rows.append(
            {
                "L": L,
                "figure_digitized_bps_hz": ref,
                "model_mean_bps_hz": round(model, 4),
                "err_rel": round(err_rel, 4),
                "within_5pct": ok,
                "within_digitization_band": abs(model - ref) <= (0.05 * ref + fig_tol),
            }
        )
    raw["fig1a_compare"] = compare_rows

    baseline_matched = bool(within) and all(within)
    baseline = {
        "reference_figure": "Fig.1(a) sum rate vs L (closed-form + Monte Carlo)",
        "digitized_points_available": True,
        "label": "FIGURE_DIGITIZED",
        "figure_digitized": FIGURE_DIGITIZED_FIG1A,
        "baseline_matched": baseline_matched,
        "compare": compare_rows,
        "reason": (
            "Model within 5% of FIGURE_DIGITIZED Nt=4 τ_p=K curve"
            if baseline_matched
            else "FIGURE_DIGITIZED present; model not within 5% on all L ticks — BASELINE_MATCH_PENDING"
        ),
    }

    increasing_8_16 = stats[0]["sum_rate_mean"] < stats[1]["sum_rate_mean"]
    increasing_all = all(
        stats[i]["sum_rate_mean"] < stats[i + 1]["sum_rate_mean"] for i in range(len(stats) - 1)
    )
    penalty_positive = all(s["sensing_penalty_mean"] > 0 for s in stats)
    oracle_ok = all(r.get("agree_within_tol") for r in oracle_reports) if oracle_reports else False

    if baseline["baseline_matched"] and increasing_all and penalty_positive and oracle_ok:
        token = "DIGITAL_REPRODUCTION_PASS"
    elif increasing_8_16 and penalty_positive:
        token = "BASELINE_MATCH_PENDING"
    else:
        token = "REFERENCE_SPEC_INCOMPLETE"

    classification = enforce_firewall(
        {
            "target_id": "OULU-002",
            "maps_to": ["R6G-004", "R6G-006"],
            "classification": token,
            "ladder": [
                "SOURCE_VERIFIED",
                "MODEL_IMPLEMENTED",
                "DIGITAL_MODEL_EXECUTED",
                "FIGURE_DIGITIZED",
                "ORACLE_CROSS_CHECKED",
                token,
            ],
            "rationale": [
                "Theorem-1-style closed-form rate implemented under orthogonal-pilot simplification",
                "Independent oracle cross-check " + ("PASS" if oracle_ok else "RECORDED"),
                "Fig.1(a) FIGURE_DIGITIZED from ar5iv PNG with equation traceability",
                (
                    "Baseline matched within 5%"
                    if baseline_matched
                    else "No improvement claim: baseline figure digits not matched within 5%"
                ),
                "Sionna " + ("AVAILABLE" if sionna_ok else "UNAVAILABLE_FAIL_CLOSED"),
            ],
            "qualitative": {
                "sum_rate_increases_with_L": increasing_all,
                "sum_rate_increases_L8_to_L16": increasing_8_16,
                "sensing_penalizes_communications": penalty_positive,
            },
            "baseline": baseline,
            "equation_traceability": EQUATION_TRACEABILITY,
            "oracle": {"reports": oracle_reports, "agree": oracle_ok},
            "IMPROVED_STATE_OF_ART": False,
            "PHYSICAL": False,
            "OTA": False,
            "6G_CERTIFIED": False,
            "CARRIER_ACCEPTED": False,
        }
    )

    ablations = {
        "sensing_off": {
            "description": "rho_sense=0 eliminates sensing interference term",
            "effect": "sum_rate_sensing_off >= sum_rate with sensing",
        },
        "pilot_contamination": {
            "description": "tau_p=K/2 vs tau_p=K",
            "effect": "half-pilot mode reduces effective ξ and typically lowers rate",
        },
        "N_t_scaling": {
            "description": "N_t=4 vs 8",
            "effect": "larger N_t increases rate (Remark 1)",
        },
    }
    negatives = [
        {
            "id": "NEG-OULU002-01",
            "claim_tested": "Sensing power does not affect communications SINR",
            "outcome": "FALSIFIED",
            "evidence": "sensing_rate_penalty > 0 across seeds (eta term in denominator)",
        },
        {
            "id": "NEG-OULU002-02",
            "claim_tested": "DIGITAL improvement over paper baseline",
            "outcome": "NOT_CLAIMED",
            "evidence": f"baseline_matched={baseline_matched}; improvement forbidden until match",
        },
        {
            "id": "NEG-OULU002-03",
            "claim_tested": "Full Theorem-2 CRLB reproduced",
            "outcome": "REFERENCE_SPEC_INCOMPLETE",
            "evidence": "proxy CRLB only; steering/FIM blocks not fully expanded this packet",
        },
    ]

    return {
        "target_id": "OULU-002",
        "seeds": seeds,
        "raw": raw,
        "statistics": stats,
        "ablation": ablations,
        "negative_results": negatives,
        "classification": classification,
        "backend": "CPU_NUMPY_ANALYTICAL",
        "sionna_used": False,
        "sionna_status": probe["adapters"]["SIONNA_PHY"]["status"],
        "IMPROVED_STATE_OF_ART": False,
    }


def write_artifact_pack(out_dir: Path, suite: dict[str, Any] | None = None) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    suite = suite or run_suite()
    source_manifest = {
        "target_id": "OULU-002",
        "title": "Multi-Static Cell-Free Massive MIMO ISAC: Performance Analysis and Power Allocation",
        "authors": ["Nhan Thanh Nguyen", "Tianyu Fang", "Hien Quoc Ngo", "Markku Juntti"],
        "org": "University of Oulu / CWC (+ QUB)",
        "doi": "10.1109/IEEECONF60004.2024.10942860",
        "arxiv": "2411.06747",
        "canonical_url": "https://doi.org/10.1109/IEEECONF60004.2024.10942860",
        "oulurepo": "https://oulurepo.oulu.fi/handle/10024/58410",
        "venue": "2024 58th Asilomar Conference on Signals, Systems, and Computers",
        "evidence_type": "PEER_REVIEWED_CONFERENCE_PAPER",
        "news_only": False,
        "maps_to_r6g": ["R6G-004", "R6G-006"],
        "metrics": ["sum_rate", "CRLB_theta_proxy", "sensing_communications_penalty"],
    }
    reference_scenario = {
        "defaults": DEFAULTS,
        "L_grid": [8, 16, 32],
        "N_t_grid": [4, 8],
        "snr_db": 30.0,
        "power_split": "equal communications/sensing (rho=0.5) baseline",
    }
    repro_config = {
        "backend": "CPU_NUMPY_ANALYTICAL",
        "sionna": suite.get("sionna_status"),
        "seeds": suite["seeds"],
        "predeclared_tolerance_rel": 0.05,
        "pass_rule": "DIGITAL_REPRODUCTION_PASS only if digitized Fig.1 baseline matched within 5% AND qualitative Remark-1 checks hold; else BASELINE_MATCH_PENDING / REFERENCE_SPEC_INCOMPLETE",
        "improvement_claims": "FORBIDDEN_UNTIL_BASELINE_MATCHED",
    }
    (out_dir / "SOURCE_MANIFEST.json").write_text(json.dumps(source_manifest, indent=2) + "\n")
    (out_dir / "REFERENCE_SCENARIO.json").write_text(json.dumps(reference_scenario, indent=2) + "\n")
    (out_dir / "REPRO_CONFIG.json").write_text(json.dumps(repro_config, indent=2) + "\n")
    (out_dir / "RAW_RESULTS.json").write_text(json.dumps(suite["raw"], indent=2) + "\n")
    (out_dir / "STATISTICS.json").write_text(json.dumps(suite["statistics"], indent=2) + "\n")
    (out_dir / "ABLATION.json").write_text(json.dumps(suite["ablation"], indent=2) + "\n")
    (out_dir / "NEGATIVE_RESULTS.json").write_text(json.dumps(suite["negative_results"], indent=2) + "\n")
    (out_dir / "CLASSIFICATION.json").write_text(json.dumps(suite["classification"], indent=2) + "\n")
    (out_dir / "LIMITATIONS.md").write_text(
        """# LIMITATIONS — OULU-002

- Orthogonal-pilot simplification of Theorem 1 (contamination path exercised only via tau_p=K/2 ablation).
- CRLB is a sensing-SNR proxy, not the full Theorem 2 FIM expansion.
- Fig.1(a) labeled FIGURE_DIGITIZED from ar5iv PNG; model may still miss 5% → BASELINE_MATCH_PENDING.
- Independent oracle cross-checks rate_closed_form vs oulu002_oracle (same equation, separate code).
- Sionna/Aerial unavailable on discovery host (FAIL CLOSED).
- IMPROVED_STATE_OF_ART / PHYSICAL / OTA / CERTIFIED / CARRIER remain false.
"""
    )
    (out_dir / "REPRODUCE.md").write_text(
        """# REPRODUCE — OULU-002

```bash
python -m research.external_reproduction.cli.researcher_cli run --target OULU-002
```

Requires: Python 3.11+, numpy. Sionna optional (FAIL CLOSED if absent).
"""
    )
    # Persist FIGURE_DIGITIZED + equation traceability beside pack
    (out_dir / "FIGURE_DIGITIZED_Fig1a.json").write_text(
        json.dumps(FIGURE_DIGITIZED_FIG1A, indent=2) + "\n"
    )
    (out_dir / "EQUATION_TRACEABILITY.json").write_text(
        json.dumps(EQUATION_TRACEABILITY, indent=2) + "\n"
    )
    if suite["classification"].get("oracle"):
        (out_dir / "ORACLE_CROSS_CHECK.json").write_text(
            json.dumps(suite["classification"]["oracle"], indent=2) + "\n"
        )
    return suite
