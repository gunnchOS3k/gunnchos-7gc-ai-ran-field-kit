"""Repo-lock verification tests — deterministic on Ubuntu CI."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from verify_repo_lock import verify, validate_lock_schema  # noqa: E402


def _base_lock():
    return json.loads((ROOT / "integration/repo-lock.json").read_text())


def _git(cwd: Path, *args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=cwd, text=True).strip()


def test_repo_lock_matches_current_checkouts():
    """Require exact SHA match for every present required sibling.

    Missing required siblings fail closed (CI must checkout locked SHAs first).
    """
    result = verify(ROOT / "integration/repo-lock.json", ROOT.parent, allow_dirty=True)
    missing = [
        c["repository"]
        for c in result["components"]
        if c.get("required") and not c.get("present")
    ]
    assert not missing, f"required siblings not checked out: {missing}"
    assert result["ok"] is True
    assert not result["failures"]
    for c in result["components"]:
        if c.get("required") and c.get("present"):
            assert c.get("match") is True


def test_dirty_tree_prohibition_on_isolated_temp_repo(tmp_path):
    """Dirty-tree policy must not depend on incidental field-kit dirt."""
    repo = tmp_path / "sibling"
    repo.mkdir()
    # --template= avoids writing default hooks (sandbox may block hooks/).
    subprocess.check_call(
        ["git", "-c", "init.defaultBranch=main", "init", "--template="],
        cwd=repo,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    _git(repo, "config", "user.email", "ci@example.com")
    _git(repo, "config", "user.name", "ci")
    (repo / "file.txt").write_text("clean\n", encoding="utf-8")
    _git(repo, "add", "file.txt")
    _git(repo, "commit", "-m", "init")
    commit = _git(repo, "rev-parse", "HEAD")
    lock = {
        "schema_version": "1.2.0",
        "locked_at": "2026-07-29T00:00:00Z",
        "dirty_tree_prohibition": True,
        "components": {
            "temp-required": {
                "path": "sibling",
                "local_path_hint": "sibling",
                "commit": commit,
                "required": True,
                "branch": "main",
            }
        },
    }
    lock_path = tmp_path / "lock.json"
    lock_path.write_text(json.dumps(lock))

    clean = verify(lock_path, tmp_path, allow_dirty=False)
    assert clean["ok"] is True

    (repo / "file.txt").write_text("dirty\n", encoding="utf-8")
    dirty = verify(lock_path, tmp_path, allow_dirty=False)
    assert dirty["ok"] is False
    assert "temp-required" in dirty["failures"]
    assert any(c.get("dirty_failure") for c in dirty["components"])

    _git(repo, "checkout", "--", "file.txt")
    restored = verify(lock_path, tmp_path, allow_dirty=False)
    assert restored["ok"] is True


def test_stale_edge_io_commit_fails(tmp_path):
    lock = _base_lock()
    lock["components"]["edge-io-measurement-node"]["commit"] = "0" * 40
    bad = tmp_path / "lock.json"
    bad.write_text(json.dumps(lock))
    result = verify(bad, ROOT.parent)
    assert result["ok"] is False


def test_stale_oulu_commit_fails(tmp_path):
    lock = _base_lock()
    assert "gunnchos-emergent-service-intent-protocols" in lock["components"]
    lock["components"]["gunnchos-emergent-service-intent-protocols"]["commit"] = "a" * 40
    bad = tmp_path / "lock.json"
    bad.write_text(json.dumps(lock))
    result = verify(bad, ROOT.parent)
    assert result["ok"] is False
    assert "gunnchos-emergent-service-intent-protocols" in result["failures"]


def test_stale_nvidia_commit_fails(tmp_path):
    lock = _base_lock()
    lock["components"]["gunnchos-gpu-nr-baseband-platform"]["commit"] = "b" * 40
    bad = tmp_path / "lock.json"
    bad.write_text(json.dumps(lock))
    result = verify(bad, ROOT.parent)
    assert result["ok"] is False
    assert "gunnchos-gpu-nr-baseband-platform" in result["failures"]


def test_missing_required_repository_fails(tmp_path):
    lock = _base_lock()
    lock["components"]["missing-required-phantom"] = {
        "path": "missing-required-phantom",
        "local_path_hint": "missing-required-phantom",
        "commit": "c" * 40,
        "required": True,
        "branch": "main",
    }
    bad = tmp_path / "lock.json"
    bad.write_text(json.dumps(lock))
    result = verify(bad, ROOT.parent)
    assert result["ok"] is False
    assert "missing-required-phantom" in result["failures"]


def test_malformed_lock_fails(tmp_path):
    bad = tmp_path / "lock.json"
    bad.write_text("{not json")
    result = verify(bad, ROOT.parent)
    assert result["ok"] is False
    assert "malformed_lock" in result["failures"]


def test_empty_commit_fails(tmp_path):
    lock = _base_lock()
    lock["components"]["ntn-resilience-sim"]["commit"] = ""
    bad = tmp_path / "lock.json"
    bad.write_text(json.dumps(lock))
    result = verify(bad, ROOT.parent)
    assert result["ok"] is False
    assert result["failures"]


def test_schema_requires_dirty_tree_prohibition():
    lock = _base_lock()
    assert lock.get("dirty_tree_prohibition") is True
    errs = validate_lock_schema(lock)
    assert errs == []


def test_write_lock_does_not_run_on_verify():
    lock_path = ROOT / "integration/repo-lock.json"
    before = lock_path.read_bytes()
    verify(lock_path, ROOT.parent)
    assert lock_path.read_bytes() == before


def test_readygary_is_optional():
    lock = _base_lock()
    assert lock["components"]["readygary-6g-beam-selection"]["required"] is False


def test_control_plane_metadata_present():
    lock = _base_lock()
    assert "control_plane" in lock
    assert lock["control_plane"]["repository_name"] == "gunnchos-7gc-ai-ran-field-kit"
    assert "gunnchos-7gc-ai-ran-field-kit" not in lock["components"]
