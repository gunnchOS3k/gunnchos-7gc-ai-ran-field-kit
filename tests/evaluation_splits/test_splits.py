from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from build_evaluation_splits import build_splits, synthetic_manifest  # noqa: E402


def test_synthetic_splits_are_infrastructure_only(tmp_path):
    manifest_path = tmp_path / "manifest.json"
    manifest = synthetic_manifest(manifest_path)
    summary = build_splits(manifest, tmp_path / "splits", allow_small=True)
    assert summary["ok"] is True
    assert summary["evaluation_label"] == "infrastructure_validation_only"
    assert summary["too_small"] is True


def test_duplicate_hashes_block_splits(tmp_path):
    manifest = synthetic_manifest(tmp_path / "manifest.json")
    manifest["session_hashes"]["duplicate.json"] = manifest["session_hashes"]["synthetic_session_1.json"]
    summary = build_splits(manifest, tmp_path / "splits", allow_small=True)
    assert summary["ok"] is False
    assert summary["duplicate_hashes"]
