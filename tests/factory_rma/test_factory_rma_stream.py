"""Field-kit honesty tests for factory / RMA / support STREAM."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
STREAM = ROOT / "program" / "streams" / "factory_rma_support"


def test_stream_files_exist():
    for name in ("STREAM.yaml", "CLAIM_BOUNDARY.md", "ops_schema.json", "WP_PACKET.md"):
        assert (STREAM / name).exists(), name


def test_stream_tokens_are_honest():
    data = yaml.safe_load((STREAM / "STREAM.yaml").read_text(encoding="utf-8"))
    assert data["PRODUCTION_RELEASE_CLAIMED"] is False
    assert data["cursor_merges"] is False
    assert data["commercial_warranty"] == "EXTERNAL"
    assert data["rfq_purchase_fab"] == "NOT_THIS_STREAM"
    assert data["production_keys"] is False
    assert data["production_ca"] is False
    assert data["status"] == "DIGITAL_PREPARATION"
    assert "gunnchos-device-os" in data["owner_repos"]
    assert "gunnchos-hardware-industrial-design" in data["supporting_repos"]
    assert data["honesty"]["does_not_invent_stock_or_price"] is True


def test_schema_const_false_production():
    schema = json.loads((STREAM / "ops_schema.json").read_text(encoding="utf-8"))
    assert schema["properties"]["PRODUCTION_RELEASE_CLAIMED"]["const"] is False
    assert schema["properties"]["commercial_warranty"]["const"] == "EXTERNAL"


def test_claim_boundary_rejects_factory_and_warranty_claims():
    text = (STREAM / "CLAIM_BOUNDARY.md").read_text(encoding="utf-8").lower()
    assert "production_release_claimed" in text
    assert "false" in text
    assert "external" in text
    assert "unknown" in text
    assert "cursor never merges" in text


def test_validator_script_passes():
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "validate_factory_rma_support_stream.py")],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
