"""Field-kit contract tests."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / "contracts"
sys.path.insert(0, str(ROOT / "scripts"))
from validate_contract import ContractError, validate_document  # noqa: E402


def test_valid_fixtures_pass():
    for name in [
        "edge_measurement_batch.valid.json",
        "twin_state_bundle.valid.json",
        "airan_decision_bundle.valid.json",
        "resilience_decision_bundle.valid.json",
    ]:
        doc = json.loads((ROOT / "fixtures/valid" / name).read_text())
        validate_document(doc, SCHEMA, enforce_privacy=True)


@pytest.mark.parametrize(
    "path",
    sorted((ROOT / "fixtures/invalid/edge").glob("*.json")),
)
def test_invalid_edge_fixtures_fail(path: Path):
    doc = json.loads(path.read_text())
    with pytest.raises(ContractError):
        validate_document(doc, SCHEMA, enforce_privacy=True)


@pytest.mark.parametrize("family", ["twin", "airan", "resilience"])
def test_invalid_family_fixtures_fail(family: str):
    files = sorted((ROOT / f"fixtures/invalid/{family}").glob("*.json"))
    assert len(files) >= 5
    for path in files:
        doc = json.loads(path.read_text())
        with pytest.raises(ContractError):
            validate_document(doc, SCHEMA, enforce_privacy=False)


def test_each_invalid_has_reason():
    for family in ["edge", "twin", "airan", "resilience"]:
        for path in (ROOT / f"fixtures/invalid/{family}").glob("*.json"):
            reason = path.with_suffix(".reason.txt")
            assert reason.is_file(), f"missing reason for {path}"
            assert reason.read_text().strip()
