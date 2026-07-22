"""Provenance helper tests."""
from __future__ import annotations

import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_checksum_script_exists():
    assert (ROOT / "scripts/verify_checksums.py").is_file()
    assert (ROOT / "scripts/verify_provenance.py").is_file()


def test_repo_lock_has_components():
    import json

    lock = json.loads((ROOT / "integration/repo-lock.json").read_text())
    assert "edge-io-measurement-node" in lock["components"]
    assert "7gc-digital-twin" in lock["components"]
    assert "spectrumx-ai-ran-gary" in lock["components"]
    assert "ntn-resilience-sim" in lock["components"]
