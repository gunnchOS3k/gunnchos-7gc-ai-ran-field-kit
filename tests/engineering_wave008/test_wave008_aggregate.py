"""Wave008 aggregate unit checks."""
from pathlib import Path
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]


def test_validate_aggregate_script_passes():
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts/engineering_wave008/validate_aggregate.py")],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr
    assert "WAVE008_AGGREGATE_VALIDATION_PASS" in proc.stdout


def test_aggregate_flags():
    agg = json.loads((ROOT / "artifacts/engineering_wave008/WAVE008_AGGREGATE.json").read_text())
    assert agg["DO_NOT_MERGE_UNTIL_WAVE008_ARCHIVE_ACCEPTED"] is True
    assert agg["BASELINE_COUNTS_UPDATED"] is False
    assert agg["OS_PLATFORM_020_UNTOUCHED"] is True
    assert agg["READY_FOR_OWNER_MERGE"] is False
    assert agg["TARGET_REQUIREMENTS"] == 15
    assert agg["IMPLEMENTED_AND_VALIDATED"] == 15
