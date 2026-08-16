"""Independent oracle for OULU-002 Theorem-1-style rate (separate implementation).

Must not import rate_closed_form from oulu002_cfmimo_isac — intentional duplication
for cross-check.
"""
from __future__ import annotations

import math
from typing import Any

import numpy as np


def oracle_rate(
    xi: np.ndarray,
    beta: np.ndarray,
    gamma: np.ndarray,
    eta: np.ndarray,
    *,
    N_t: int,
    sigma2: float,
    tau_bar: float,
) -> np.ndarray:
    """Re-derived from paper eq. (7) / Theorem 1 (orthogonal-pilot simplification).

    R_k = τ̄ log2( 1 + N_t² (ξ_k^T √γ_k)² / (N_t Σ_j (β̂_kj^T γ_j + β_k^T η_j) + σ²) )
    with β̂_kj,ℓ = β_kℓ ξ_jℓ.
    """
    K = xi.shape[0]
    rates = np.zeros(K)
    for k in range(K):
        desired = (N_t * float(np.dot(xi[k], np.sqrt(np.maximum(gamma[k], 0.0))))) ** 2
        interference = float(sigma2)
        for j in range(K):
            beta_hat = beta[k] * xi[j]
            interference += N_t * (
                float(np.dot(beta_hat, gamma[j])) + float(np.dot(beta[k], eta[j]))
            )
        rates[k] = tau_bar * math.log2(1.0 + desired / max(interference, 1e-30))
    return rates


def cross_check(
    xi: np.ndarray,
    beta: np.ndarray,
    gamma: np.ndarray,
    eta: np.ndarray,
    primary_rates: np.ndarray,
    *,
    N_t: int,
    sigma2: float,
    tau_bar: float,
    tol_rel: float = 1e-9,
) -> dict[str, Any]:
    oracle = oracle_rate(xi, beta, gamma, eta, N_t=N_t, sigma2=sigma2, tau_bar=tau_bar)
    abs_err = np.abs(oracle - primary_rates)
    rel = abs_err / np.maximum(np.abs(primary_rates), 1e-30)
    return {
        "oracle_impl": "oulu002_oracle.oracle_rate",
        "primary_impl": "oulu002_cfmimo_isac.rate_closed_form",
        "max_abs_err": float(np.max(abs_err)),
        "max_rel_err": float(np.max(rel)),
        "agree_within_tol": bool(np.all(rel <= tol_rel) or np.all(abs_err <= 1e-12)),
        "oracle_sum_rate": float(oracle.sum()),
        "primary_sum_rate": float(primary_rates.sum()),
    }
