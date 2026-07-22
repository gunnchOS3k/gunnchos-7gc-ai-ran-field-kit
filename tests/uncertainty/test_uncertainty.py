from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from build_evaluation_splits import synthetic_manifest  # noqa: E402
from calculate_uncertainty import calculate  # noqa: E402
from run_baselines import run  # noqa: E402


def test_synthetic_uncertainty_is_insufficient_for_inference(tmp_path):
    manifest = synthetic_manifest(tmp_path / "manifest.json")
    baseline_csv = tmp_path / "baseline.csv"
    run(manifest, baseline_csv, experiment_id="x")
    report = calculate(manifest, baseline_csv, tmp_path / "uncertainty.json")
    assert report["evaluation_label"] == "infrastructure_validation_only"
    assert report["inference_label"] == "insufficient_sample_size_for_inference"
    assert report["interval"] == [None, None]
