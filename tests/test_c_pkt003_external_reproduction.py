"""Tests for C-PKT-003 Oulu discrepancy resolution + NVIDIA fail-closed probe."""
from __future__ import annotations

import json
from pathlib import Path

from research.external_reproduction.adapters.nvidia_6g_probe import probe_host
from research.external_reproduction.adapters.probe import probe_all
from research.external_reproduction.oulu001_fr3_mmwave import range_resolution_m, run_suite as run_oulu001
from research.external_reproduction.oulu002_cfmimo_isac import (
    FIGURE_DIGITIZED_FIG1A,
    run_suite as run_oulu002,
)
from research.external_reproduction.oulu002_oracle import oracle_rate
import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def test_nvidia_probe_fail_closed_on_mac_or_no_gpu():
    payload = probe_host()
    assert payload["fake_forbidden"]["AODT"] is True
    assert payload["NVIDIA_AERIAL_VALIDATED"] is False
    assert payload["IMPROVED_STATE_OF_ART"] is False
    # On this discovery host we expect fail-closed
    assert payload["status"].startswith("FAIL_CLOSED") or payload["status"] == "GPU_STACK_DETECTABLE"


def test_oulu001_discrepancy_documented_not_forced():
    suite = run_oulu001(seeds=[7, 11])
    cls = suite["classification"]
    assert cls["classification"] == "REFERENCE_SPEC_INCOMPLETE"
    assert cls["forbid_aperture_fudge_to_force_pass"] is True
    assert cls["spec_discrepancy_resolution"] == "DOCUMENTED_C_PKT_003"
    assert abs(range_resolution_m(0.4) - 0.37474) < 0.01
    assert cls["qualitative"]["fr2_table_iii_vs_c_over_2B_discrepancy"] is True
    res = ROOT / "artifacts/external_reproduction/C_PKT_003/OULU-001/OULU001_SPEC_DISCREPANCY_RESOLUTION.md"
    assert res.is_file()


def test_oulu002_figure_digitized_and_oracle():
    assert FIGURE_DIGITIZED_FIG1A["label"] == "FIGURE_DIGITIZED"
    suite = run_oulu002(seeds=[7, 11])
    cls = suite["classification"]
    assert cls["baseline"]["digitized_points_available"] is True
    assert cls["baseline"]["label"] == "FIGURE_DIGITIZED"
    assert cls["IMPROVED_STATE_OF_ART"] is False
    assert cls["classification"] in (
        "BASELINE_MATCH_PENDING",
        "DIGITAL_REPRODUCTION_PASS",
        "REFERENCE_SPEC_INCOMPLETE",
    )
    # Oracle identity on a tiny synthetic case
    xi = np.ones((2, 3)) * 0.1
    beta = np.ones((2, 3)) * 0.2
    gamma = np.ones((2, 3)) * 0.01
    eta = np.ones((2, 3)) * 0.01
    r = oracle_rate(xi, beta, gamma, eta, N_t=4, sigma2=1e-6, tau_bar=0.98)
    assert r.shape == (2,)
    assert np.all(r >= 0)


def test_adapters_still_fail_closed():
    probe = probe_all()
    for _bid, rep in probe["adapters"].items():
        if not rep["present"]:
            assert rep["status"] == "UNAVAILABLE_FAIL_CLOSED"
