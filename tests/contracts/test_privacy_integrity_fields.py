"""Privacy scanner must not flag schema-valid integrity digests as IMEI/PII."""
from __future__ import annotations

import json
import sys
from copy import deepcopy
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from validate_contract import ContractError, validate_document

SCHEMA = ROOT / "contracts"

# Schema-valid SHA-256 containing a 15-digit decimal run (696957768804862).
UNLUCKY_SHA256 = "d0722eb9a69907512eca34cad696957768804862ff2aeebc0123456789abcdef"
assert len(UNLUCKY_SHA256) == 64
assert "696957768804862" in UNLUCKY_SHA256


def _optimization() -> dict:
    return json.loads((ROOT / "fixtures/valid/campus_optimization_result.valid.json").read_text())


def _design() -> dict:
    return json.loads((ROOT / "fixtures/valid/campus_design_bundle.valid.json").read_text())


def test_unlucky_sha256_in_integrity_field_passes():
    doc = _optimization()
    doc["input_twin_state_hash"] = UNLUCKY_SHA256
    validate_document(doc, SCHEMA, enforce_privacy=True)


def test_imei_like_value_in_notes_still_fails():
    doc = _optimization()
    doc["notes"] = "device 123456789012345 observed"
    with pytest.raises(ContractError, match="prohibited value pattern"):
        validate_document(doc, SCHEMA, enforce_privacy=True)


def test_email_in_notes_still_fails():
    doc = _optimization()
    doc["notes"] = "contact student@example.com"
    with pytest.raises(ContractError, match="prohibited value pattern"):
        validate_document(doc, SCHEMA, enforce_privacy=True)


def test_mac_in_notes_still_fails():
    doc = _optimization()
    doc["notes"] = "adapter aa:bb:cc:dd:ee:ff"
    with pytest.raises(ContractError, match="prohibited value pattern"):
        validate_document(doc, SCHEMA, enforce_privacy=True)


@pytest.mark.parametrize(
    "key",
    ["student_id", "latitude", "longitude", "trajectory", "minor_location"],
)
def test_prohibited_key_still_fails(key: str):
    doc = _optimization()
    extra = deepcopy(doc)
    # planning_variables allows additional properties, so key scanning is reached.
    extra["alternatives"][0]["planning_variables"][key] = "x"
    with pytest.raises(ContractError, match="prohibited key"):
        validate_document(extra, SCHEMA, enforce_privacy=True)


def test_malformed_hash_still_fails_schema():
    doc = _optimization()
    doc["input_twin_state_hash"] = "deadbeef"
    with pytest.raises(ContractError, match="Schema validation failed"):
        validate_document(doc, SCHEMA, enforce_privacy=True)


def test_malformed_hash_characters_still_fail_schema():
    doc = _optimization()
    doc["input_design_hash"] = "g" * 64
    with pytest.raises(ContractError, match="Schema validation failed"):
        validate_document(doc, SCHEMA, enforce_privacy=True)


def test_gaza_sensitive_export_still_fails():
    doc = json.loads((ROOT / "fixtures/invalid/campus/gaza_sensitive_export.json").read_text())
    with pytest.raises(ContractError):
        validate_document(doc, SCHEMA, enforce_privacy=True)


def test_graham_station_claim_still_fails():
    doc = _design()
    doc["site_id"] = "graham_land"
    doc["campus_slug"] = "graham-land"
    doc["privacy"]["graham_station_claim"] = True
    with pytest.raises(ContractError, match="Schema validation failed|Graham Land"):
        validate_document(doc, SCHEMA, enforce_privacy=True)
