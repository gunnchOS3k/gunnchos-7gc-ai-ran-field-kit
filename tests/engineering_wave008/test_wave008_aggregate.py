"""Wave008 aggregate unit checks (post-acceptance)."""
from pathlib import Path
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
EXPECTED_HEAD = "0a8089ad50df36a738743e358dcc039f97a004cb"
EXPECTED_MERGE = "069243c365552f00707650e9d81a8046ba3075d8"


def test_validate_aggregate_script_passes():
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts/engineering_wave008/validate_aggregate.py")],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr
    assert "WAVE008_AGGREGATE_POST_ACCEPTANCE_VALIDATION_PASS" in proc.stdout


def test_aggregate_post_acceptance_flags():
    agg = json.loads((ROOT / "artifacts/engineering_wave008/WAVE008_AGGREGATE.json").read_text())
    assert agg["DO_NOT_MERGE_UNTIL_WAVE008_ARCHIVE_ACCEPTED"] is False
    assert agg["ARCHIVE_ACCEPTANCE_CONDITION_SATISFIED"] is True
    assert agg["archive_accepted_main"] is True
    assert agg["archive_accepted_main_verified"] is True
    assert agg["archive_tree_equivalence"] is True
    assert agg["archive_head_sha"] == EXPECTED_HEAD
    assert agg["archive_merge_sha"] == EXPECTED_MERGE
    assert agg["BASELINE_COUNTS_UPDATED"] is False
    assert agg["OS_PLATFORM_020_UNTOUCHED"] is True
    assert agg["READY_FOR_OWNER_MERGE"] is True
    assert agg["READY_FOR_OWNER_MERGE_SEQUENCE"] is True
    assert agg["TARGET_REQUIREMENTS"] == 15
    assert agg["IMPLEMENTED_AND_VALIDATED"] == 15
    assert agg["FIXTURE_ONLY_SOURCE_VERIFIED_COUNT"] == 0
    assert agg["AUTHENTIC_EXTERNAL_SOURCE_SNAPSHOTS_PRESENT"] is False
    assert agg["SOURCE_VERIFIED_REQUIRES_VERIFIED_INTEGRATION"] is True
    assert agg["BEHAVIORAL_NEGATIVE_CONTROL_COUNT"] >= 22
    assert agg["UNCONDITIONAL_TRUE_CLASSIFIERS"] == 0
    before = agg["sequencing_guard_history"]["before_archive_35_accepted"]
    assert before["DO_NOT_MERGE_UNTIL_WAVE008_ARCHIVE_ACCEPTED"] is True
    assert before["READY_FOR_OWNER_MERGE"] is False
