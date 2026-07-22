from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from build_evaluation_splits import synthetic_manifest  # noqa: E402
from gate4_common import read_csv  # noqa: E402
from run_baselines import run  # noqa: E402


def test_baselines_include_oracle_as_analysis_only(tmp_path):
    output = tmp_path / "baseline_results.csv"
    rows = run(synthetic_manifest(tmp_path / "manifest.json"), output, experiment_id="x")
    assert len(rows) == 11
    csv_rows = read_csv(output)
    oracle = [r for r in csv_rows if r["condition"] == "oracle_hindsight_analysis_only"][0]
    assert oracle["deployable"] == "false"
    assert oracle["evaluation_label"] == "infrastructure_validation_only"
