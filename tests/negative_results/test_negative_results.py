from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from build_evaluation_splits import synthetic_manifest  # noqa: E402
from generate_negative_results import generate  # noqa: E402


def test_negative_results_register_retains_entries(tmp_path):
    output = tmp_path / "NEGATIVE_RESULTS_REGISTER.md"
    result = generate(synthetic_manifest(tmp_path / "manifest.json"), output, experiment_id="x")
    text = output.read_text(encoding="utf-8")
    assert len(result["entries"]) >= 3
    assert "negative" in text
    assert "neutral" in text
