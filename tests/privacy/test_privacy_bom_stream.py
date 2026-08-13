"""Field-kit honesty tests for privacy + digital inventory STREAM."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
STREAM = ROOT / "program" / "streams" / "privacy_bom_inventory"


def test_stream_files_exist():
    for name in (
        "STREAM.yaml",
        "CLAIM_BOUNDARY.md",
        "inventory_schema.json",
        "WP_PACKET.md",
    ):
        assert (STREAM / name).exists(), name


def test_stream_tokens_are_honest():
    data = yaml.safe_load((STREAM / "STREAM.yaml").read_text(encoding="utf-8"))
    assert data["EXTERNAL_PENTEST_COMPLETE"] is False
    assert data["e7_claimed"] is False
    assert data["legal_approval"] == "HUMAN/EXTERNAL"
    assert data["WP_006_started"] is False
    assert data["CYCLE_3_STARTED"] is False
    assert data["cursor_merges"] is False
    assert data["status"] == "DIGITAL_PREP"
    assert "gunnchos-device-os" in data["owner_repos"]
    assert "beatlink-party" in data["supporting_repos"]


def test_inventory_schema_forbids_pentest_complete():
    schema = json.loads((STREAM / "inventory_schema.json").read_text(encoding="utf-8"))
    assert schema["properties"]["EXTERNAL_PENTEST_COMPLETE"]["const"] is False
    assert schema["properties"]["legal_approval"]["const"] == "HUMAN/EXTERNAL"


def test_claim_boundary_rejects_fake_e7_and_legal():
    text = (STREAM / "CLAIM_BOUNDARY.md").read_text(encoding="utf-8").lower()
    assert "e7" in text
    assert "false" in text
    assert "human/external" in text
    assert "coppa" in text
    assert "not claimed" in text


def test_validator_script_passes():
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "validate_privacy_bom_stream.py")],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
