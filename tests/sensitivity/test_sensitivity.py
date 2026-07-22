from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from build_evaluation_splits import synthetic_manifest  # noqa: E402
from gate4_common import SENSITIVITY_PARAMETERS, read_csv  # noqa: E402
from run_sensitivity import run  # noqa: E402


def test_sensitivity_covers_required_parameters(tmp_path):
    output = tmp_path / "sensitivity_results.csv"
    run(synthetic_manifest(tmp_path / "manifest.json"), output, experiment_id="x")
    conditions = {row["condition"] for row in read_csv(output)}
    assert set(SENSITIVITY_PARAMETERS) <= conditions
