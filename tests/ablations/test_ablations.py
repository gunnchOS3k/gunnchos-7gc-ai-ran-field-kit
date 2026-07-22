from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from build_evaluation_splits import synthetic_manifest  # noqa: E402
from gate4_common import read_csv  # noqa: E402
from run_ablations import run  # noqa: E402


def test_privacy_ablation_keeps_actual_privacy_controls(tmp_path):
    output = tmp_path / "ablation_results.csv"
    run(synthetic_manifest(tmp_path / "manifest.json"), output, experiment_id="x")
    rows = read_csv(output)
    privacy = [r for r in rows if "privacy_constraint" in r["condition"]][0]
    assert privacy["privacy_controls_active"] == "true"
    assert "simulated decision constraint" in privacy["notes"]
