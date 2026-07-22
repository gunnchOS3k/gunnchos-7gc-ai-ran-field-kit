"""Gate 3 evidence integrity tests."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from audit_collection_coverage import audit  # noqa: E402
from evaluate_gate3_status import evaluate  # noqa: E402
from gate3_common import recursive_privacy_scan  # noqa: E402
from validate_contract import ContractError, validate_document  # noqa: E402


def _synthetic_session(tmp_path: Path, *, relabel_physical: bool = False) -> Path:
    edge = json.loads((ROOT / "fixtures/valid/edge_measurement_batch.valid.json").read_text())
    if relabel_physical:
        edge["evidence_level"] = "controlled_device_measurement"
        # keep emulator provenance to prove relabel fails
    ctx = {
        "schema_name": "gunnchos.measurement_session_context",
        "schema_version": "1.0.0",
        "session_id": "s1",
        "run_id": edge["run_id"],
        "collection_day_id": "day_01",
        "location_category": "library_or_community_indoor",
        "named_test_zone": "zone_a",
        "indoor_outdoor": "indoor",
        "stationary_or_moving": "stationary",
        "network_condition": "wifi_normal",
        "network_type": "wifi",
        "workload_profile": "learn",
        "planned_duration_seconds": 300,
        "actual_duration_seconds": 300,
        "start_timestamp": "2026-07-22T10:00:00Z",
        "end_timestamp": "2026-07-22T10:05:00Z",
        "device_category": "laptop",
        "collector_version": "test",
        "consent_receipt_id": "rcpt_test_123456",
        "consent_captured_at": "2026-07-22T09:59:00Z",
        "environmental_notes": "",
        "degradation_method": "none",
        "operator_notes": "",
        "protocol_deviation": None,
        "evidence_level": edge["evidence_level"],
    }
    path = tmp_path / "sess.json"
    path.write_text(json.dumps({"measurement_batch": edge, "session_context": ctx}, indent=2))
    return path


def test_synthetic_does_not_count(tmp_path):
    sess_dir = tmp_path / "s"
    sess_dir.mkdir()
    p = _synthetic_session(tmp_path)
    (sess_dir / "a.json").write_text(p.read_text())
    cov = audit(ROOT / "protocols/controlled_pilot_matrix.csv", sess_dir)
    assert cov["eligible_physical_session_count"] == 0


def test_relabel_emulator_rejected(tmp_path):
    sess_dir = tmp_path / "s"
    sess_dir.mkdir()
    p = _synthetic_session(tmp_path, relabel_physical=True)
    (sess_dir / "a.json").write_text(p.read_text())
    cov = audit(ROOT / "protocols/controlled_pilot_matrix.csv", sess_dir)
    assert cov["eligible_physical_session_count"] == 0
    assert any(r["reason"] == "emulator_provenance" for r in cov["rejected"])


def test_privacy_detects_ssid_aliases():
    findings = recursive_privacy_scan({"network": {"Wi-Fi SSID": "HomeNet", "BSSID": "aa:bb:cc:dd:ee:ff"}})
    assert findings


def test_incomplete_matrix_cannot_pass():
    coverage = {
        "required_counts": {"locations": 3, "network_conditions": 2, "distinct_days": 3, "cells": 54},
        "observed_counts": {"locations": 0, "network_conditions": 0, "distinct_days": 0},
        "missing_cells": ["x"] * 54,
        "eligible_physical_session_count": 0,
        "physical_session_count": 0,
        "filled_cells": 0,
    }
    status = evaluate(
        coverage,
        android_builds=True,
        consent_deletion_ok=True,
        protocol_exists=True,
        matrix_exists=True,
        assemble_works=True,
        external_prepared=True,
        external_complete=True,
        physical_pipeline_ok=True,
        privacy_ok=True,
        consent_ok=True,
    )
    assert status["gate3_status"] == "GATE3_COLLECTION_READY"
    assert status["gate3_status"] != "GATE_3_PASS"


def test_session_context_schema():
    ctx = {
        "schema_name": "gunnchos.measurement_session_context",
        "schema_version": "1.0.0",
        "session_id": "s1",
        "run_id": "r1",
        "collection_day_id": "day_01",
        "location_category": "library_or_community_indoor",
        "named_test_zone": "zone_a",
        "indoor_outdoor": "indoor",
        "stationary_or_moving": "stationary",
        "network_condition": "wifi_normal",
        "network_type": "wifi",
        "workload_profile": "learn",
        "planned_duration_seconds": 300,
        "actual_duration_seconds": 300,
        "start_timestamp": "2026-07-22T10:00:00Z",
        "end_timestamp": "2026-07-22T10:05:00Z",
        "device_category": "laptop",
        "collector_version": "0.2.0",
        "consent_receipt_id": "rcpt_abcdefgh",
        "environmental_notes": "",
        "degradation_method": "none",
        "operator_notes": "",
        "protocol_deviation": None,
        "evidence_level": "controlled_device_measurement",
    }
    validate_document(ctx, ROOT / "contracts", expected_schema_name="gunnchos.measurement_session_context", enforce_privacy=False)


def test_matrix_has_54_rows():
    import csv
    rows = list(csv.DictReader((ROOT / "protocols/controlled_pilot_matrix.csv").open()))
    assert len(rows) == 54


def test_calibration_yields_partial_not_matrix_credit(tmp_path):
    sess_dir = tmp_path / "s"
    sess_dir.mkdir()
    edge = json.loads((ROOT / "fixtures/valid/edge_measurement_batch.valid.json").read_text())
    edge["evidence_level"] = "controlled_device_measurement"
    edge["provenance"] = {"collector": "physical_device", "collector_version": "test"}
    edge["consent"] = {"status": "active", "receipt_id": "rcpt_cal"}
    ctx = {
        "schema_name": "gunnchos.measurement_session_context",
        "schema_version": "1.0.0",
        "session_id": "cal1",
        "run_id": edge["run_id"],
        "collection_day_id": "calibration_day",
        "location_category": "home_or_private_indoor",
        "named_test_zone": "zone_calibration",
        "indoor_outdoor": "indoor",
        "stationary_or_moving": "stationary",
        "network_condition": "wifi_normal",
        "network_type": "wifi",
        "workload_profile": "learn",
        "planned_duration_seconds": 60,
        "actual_duration_seconds": 60,
        "start_timestamp": "2026-07-22T10:00:00Z",
        "end_timestamp": "2026-07-22T10:01:00Z",
        "device_category": "laptop",
        "collector_version": "test",
        "consent_receipt_id": "rcpt_cal_123456",
        "consent_captured_at": "2026-07-22T09:59:00Z",
        "environmental_notes": "",
        "degradation_method": "none",
        "operator_notes": "calibration_only=true",
        "protocol_deviation": "calibration_not_pilot",
        "evidence_level": "controlled_device_measurement",
    }
    (sess_dir / "cal.json").write_text(json.dumps({"measurement_batch": edge, "session_context": ctx}))
    cov = audit(ROOT / "protocols/controlled_pilot_matrix.csv", sess_dir)
    assert cov["calibration_session_count"] == 1
    assert cov["eligible_physical_session_count"] == 0
    status = evaluate(
        cov,
        android_builds=True,
        consent_deletion_ok=True,
        protocol_exists=True,
        matrix_exists=True,
        assemble_works=True,
        external_prepared=True,
        external_complete=True,
        physical_pipeline_ok=True,
        privacy_ok=True,
        consent_ok=True,
    )
    assert status["gate3_status"] == "GATE3_PARTIAL_EVIDENCE"
