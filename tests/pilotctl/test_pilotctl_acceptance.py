#!/usr/bin/env python3
"""Pilotctl acceptance tests: calibration/synthetic exclusion and matrix integrity."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from audit_collection_coverage import audit  # noqa: E402
from pilotctl import load_matrix, next_cell, status, validate_import  # noqa: E402


def _base_ctx(**overrides):
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
        "device_category": "phone",
        "collector_version": "test",
        "consent_receipt_id": "rcpt_test_123456",
        "consent_captured_at": "2026-07-22T09:59:00Z",
        "environmental_notes": "",
        "degradation_method": "none",
        "operator_notes": "",
        "protocol_deviation": None,
        "evidence_level": "controlled_device_measurement",
    }
    ctx.update(overrides)
    return ctx


def _base_batch(**overrides):
    edge = json.loads((ROOT / "fixtures/valid/edge_measurement_batch.valid.json").read_text())
    edge["evidence_level"] = "controlled_device_measurement"
    edge["provenance"] = {
        "collector": "physical_device",
        "generated_at": "2026-07-22T10:05:00Z",
        "source": "test",
    }
    edge["consent"] = {
        "status": "active",
        "receipt_id": "rcpt_test_123456",
        "withdrawal_supported": True,
        "captured_at": "2026-07-22T09:59:00Z",
    }
    edge["device"]["device_class"] = "phone"
    edge["device"]["os_family"] = "android"
    edge["device"]["model_label"] = "pixel_6a"
    edge.update(overrides)
    return edge


def _write_session(path: Path, *, ctx=None, batch=None):
    doc = {
        "measurement_batch": batch or _base_batch(),
        "session_context": ctx or _base_ctx(),
        "collection_mode_label": "PHYSICAL DEVICE COLLECTION",
    }
    path.write_text(json.dumps(doc, indent=2))
    return path


def test_matrix_has_exactly_54_cells():
    assert len(load_matrix()) == 54


def test_calibration_cannot_satisfy_cell(tmp_path, monkeypatch):
    sess = tmp_path / "cal.json"
    _write_session(
        sess,
        ctx=_base_ctx(
            collection_day_id="calibration_day",
            named_test_zone="zone_calibration",
            protocol_deviation="calibration_not_pilot",
            operator_notes="calibration_only=true",
            planned_duration_seconds=60,
            actual_duration_seconds=60,
        ),
    )
    monkeypatch.setattr("pilotctl.SANITIZED", tmp_path / "san")
    (tmp_path / "san").mkdir()
    result = validate_import(sess)
    assert result["ok"] is False
    assert any("matrix cell" in e or "calibration" in e.lower() for e in result["errors"])


def test_synthetic_rejected(tmp_path, monkeypatch):
    batch = _base_batch(evidence_level="synthetic")
    batch["provenance"]["collector"] = "deterministic_emulator"
    sess = tmp_path / "syn.json"
    _write_session(sess, batch=batch, ctx=_base_ctx(evidence_level="synthetic"))
    monkeypatch.setattr("pilotctl.SANITIZED", tmp_path / "san")
    (tmp_path / "san").mkdir()
    result = validate_import(sess)
    assert result["ok"] is False


def test_wrong_zone_rejected(tmp_path, monkeypatch):
    sess = tmp_path / "badzone.json"
    _write_session(sess, ctx=_base_ctx(named_test_zone="zone_zzz"))
    monkeypatch.setattr("pilotctl.SANITIZED", tmp_path / "san")
    (tmp_path / "san").mkdir()
    assert validate_import(sess)["ok"] is False


def test_withdrawn_rejected(tmp_path, monkeypatch):
    batch = _base_batch()
    batch["consent"]["status"] = "withdrawn"
    sess = tmp_path / "wd.json"
    _write_session(sess, batch=batch)
    monkeypatch.setattr("pilotctl.SANITIZED", tmp_path / "san")
    (tmp_path / "san").mkdir()
    assert validate_import(sess)["ok"] is False


def test_privacy_fail_rejected(tmp_path, monkeypatch):
    batch = _base_batch()
    batch["annotations"] = {"ssid": "HomeNet"}
    sess = tmp_path / "priv.json"
    _write_session(sess, batch=batch)
    monkeypatch.setattr("pilotctl.SANITIZED", tmp_path / "san")
    (tmp_path / "san").mkdir()
    assert validate_import(sess)["ok"] is False


def test_next_cell_deterministic():
    a = next_cell()
    b = next_cell()
    assert a["next"]["cell_id"] == b["next"]["cell_id"]
    assert a["next"]["cell_id"]


def test_status_reports_zero_eligible_with_calibration_present():
    st = status()
    assert st["matrix_rows"] == 54
    assert st["eligible_physical_session_count"] == 0
    assert st["missing_cells"] == 54
