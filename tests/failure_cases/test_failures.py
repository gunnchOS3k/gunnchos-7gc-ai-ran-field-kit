"""Integrated pipeline failure-case tests."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from validate_contract import ContractError, validate_document  # noqa: E402

SCHEMA = ROOT / "contracts"


def test_incompatible_schema_version_fails():
    doc = json.loads((ROOT / "fixtures/valid/edge_measurement_batch.valid.json").read_text())
    doc["schema_version"] = "2.0.0"
    with pytest.raises(ContractError, match="Unsupported"):
        validate_document(doc, SCHEMA)


def test_prohibited_identifier_fails():
    path = ROOT / "fixtures/invalid/edge/prohibited_direct_identifiers.json"
    doc = json.loads(path.read_text())
    with pytest.raises(ContractError, match="Prohibited"):
        validate_document(doc, SCHEMA, enforce_privacy=True)


def test_negative_latency_fails():
    doc = json.loads((ROOT / "fixtures/invalid/edge/negative_latency.json").read_text())
    with pytest.raises(ContractError):
        validate_document(doc, SCHEMA)


def test_packet_loss_over_100_fails():
    doc = json.loads((ROOT / "fixtures/invalid/edge/packet_loss_over_100.json").read_text())
    with pytest.raises(ContractError):
        validate_document(doc, SCHEMA)


def test_evidence_conflict_fails():
    doc = json.loads((ROOT / "fixtures/invalid/edge/evidence_provenance_conflict.json").read_text())
    with pytest.raises(ContractError):
        validate_document(doc, SCHEMA)
