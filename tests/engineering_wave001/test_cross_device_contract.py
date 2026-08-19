"""Wave 001 cross-device contract schema and aggregate verifier tests."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = Path(__file__).resolve().parent / "fixtures"
SCRIPTS = ROOT / "scripts" / "engineering_wave001"
sys.path.insert(0, str(SCRIPTS))

from verify_cross_device_contract import validate_contract, contract_is_operationally_valid  # noqa: E402
from run_full_ops_wave001 import build_parity_matrix, run_full_ops_verifier  # noqa: E402


@pytest.fixture(scope="module")
def schema() -> dict:
    return json.loads(
        (ROOT / "program/contracts/cross_device_game_contract.v1.schema.json").read_text()
    )


def test_valid_fixtures_validate(schema):
    for path in sorted(FIXTURES.glob("*.cross_device_contract.json")):
        doc = json.loads(path.read_text())
        validate_contract(doc, schema)
        assert doc["game_id"] in path.name


def test_invalid_fixture_rejected(schema):
    bad = json.loads((FIXTURES / "invalid_missing_probes.json").read_text())
    with pytest.raises(Exception):
        validate_contract(bad, schema)


def test_parity_matrix_from_fixtures():
    contracts_dir = FIXTURES
    paths = {
        gid: contracts_dir / f"{gid}.cross_device_contract.json"
        for gid in (
            "anime-aggressors",
            "pedestrian-pursuit",
            "archive-of-life-artifact-world",
            "beatlink-party",
        )
    }
    result = run_full_ops_verifier(paths)
    matrix = result["parity_matrix"]
    assert "requirements" in matrix
    assert matrix["requirements"]["GAME-CROSS-001"]["anime-aggressors"] is True


def test_cli_verifier_on_fixture():
    sample = FIXTURES / "anime-aggressors.cross_device_contract.json"
    proc = subprocess.run(
        [sys.executable, str(SCRIPTS / "verify_cross_device_contract.py"), str(sample)],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "anime-aggressors" in proc.stdout


def test_operational_fixture_flags():
    sample = json.loads((FIXTURES / "anime-aggressors.cross_device_contract.json").read_text())
    assert contract_is_operationally_valid(sample)
