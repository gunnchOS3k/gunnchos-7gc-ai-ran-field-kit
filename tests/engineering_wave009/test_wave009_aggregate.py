"""Wave009 aggregate unit checks — no Baseline mutation."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_aggregate_pass_and_baseline_untouched() -> None:
    agg = json.loads((ROOT / "artifacts/engineering_wave009/WAVE009_AGGREGATE.json").read_text())
    assert agg["status"] == "PASS"
    assert agg["TARGET_REQUIREMENTS"] == 1
    assert agg["requirement_ids"] == ["OS-PLATFORM-020"]
    assert agg["BASELINE_COUNTS_UPDATED"] is False
    assert agg["DIGITAL_VALIDATION_QUEUE_UPDATED"] is False
    assert agg["OS_PLATFORM_020_BASELINE_STATE_UNCHANGED"] == "DIGITAL_VALIDATION_OPEN"
    assert agg["CLOSEOUT_NOT_PERFORMED"] is True


def test_mirror_kernel_sandbox() -> None:
    suite = json.loads(
        (ROOT / "artifacts/engineering_wave009/device_os_mirror/SANDBOX_ENFORCEMENT_RESULT.json").read_text()
    )
    assert suite["SANDBOX_BACKEND"] == "bubblewrap"
    assert suite["KERNEL_SANDBOX"] is True
    assert suite["SANDBOX_EXECUTED_AS_ROOT"] is False
    assert suite["BWRAP_INVOKED_WITH_SUDO"] is False
    assert suite["PLAIN_SUBPROCESS_COUNTS_AS_SANDBOX"] is False


def test_validate_script_exits_zero() -> None:
    proc = subprocess.run(
        ["python3", "scripts/engineering_wave009/validate_aggregate.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
