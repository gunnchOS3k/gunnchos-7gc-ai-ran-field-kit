"""Main-branch policy validator tests."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate_main_branch_policy.py"


def test_policy_script_passes_on_repo():
    proc = subprocess.run(
        [sys.executable, str(SCRIPT)],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "MAIN_BRANCH_POLICY_OK" in proc.stdout


def test_policy_fails_on_master_default(tmp_path: Path):
    # Create a mini tree with active workflow using master as sole base
    wf = tmp_path / ".github" / "workflows"
    wf.mkdir(parents=True)
    (wf / "ci.yml").write_text(
        "on:\n  push:\n    branches:\n      - master\n",
        encoding="utf-8",
    )
    (tmp_path / "program" / "repositories").mkdir(parents=True)
    (tmp_path / "program" / "repositories" / "branch_policy.yaml").write_text(
        "new_master_references_prohibited: true\n"
        "allowlist_globs_for_master_mentions: []\n"
        "allowlist_workflow_dual_triggers: false\n",
        encoding="utf-8",
    )
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(tmp_path)],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert proc.returncode != 0
    assert "MAIN_BRANCH_POLICY_FAIL" in proc.stdout
