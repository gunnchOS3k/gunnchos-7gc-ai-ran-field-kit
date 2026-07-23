"""Repo-lock verification tests."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from verify_repo_lock import verify  # noqa: E402


def test_repo_lock_matches_current_checkouts():
    result = verify(ROOT / "integration/repo-lock.json", ROOT.parent)
    assert result["ok"] is True
    assert not result["failures"]


def test_repo_lock_detects_drift(tmp_path):
    lock = json.loads((ROOT / "integration/repo-lock.json").read_text())
    # Corrupt a required commit
    lock["components"]["edge-io-measurement-node"]["commit"] = "0" * 40
    bad = tmp_path / "lock.json"
    bad.write_text(json.dumps(lock))
    result = verify(bad, ROOT.parent)
    assert result["ok"] is False
    assert "edge-io-measurement-node" in result["failures"]


def test_readygary_is_optional():
    lock = json.loads((ROOT / "integration/repo-lock.json").read_text())
    assert lock["components"]["readygary-6g-beam-selection"]["required"] is False
