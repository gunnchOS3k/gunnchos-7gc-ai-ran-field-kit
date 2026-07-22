from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from build_evaluation_splits import build_splits, synthetic_manifest  # noqa: E402
from gate4_common import evaluate_artifact_status, required_gate4_artifacts  # noqa: E402


def test_synthetic_artifacts_can_only_be_evaluation_ready(tmp_path):
    manifest = synthetic_manifest(tmp_path / "manifest.json")
    split_summary = build_splits(manifest, tmp_path / "splits", allow_small=True)
    for path in required_gate4_artifacts(tmp_path).values():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("placeholder\n", encoding="utf-8")
    status = evaluate_artifact_status(
        manifest=manifest,
        sample_count=split_summary["sample_count"],
        split_summary=split_summary,
        run_dir=tmp_path,
    )
    assert status["gate4_status"] == "GATE4_EVALUATION_READY"
    assert status["gate4_status"] != "GATE_4_PASS"
    assert status["evaluation_label"] == "infrastructure_validation_only"
    assert status["inference_label"] == "insufficient_sample_size_for_inference"
