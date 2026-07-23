#!/usr/bin/env python3
"""Pilot assignment emit/validate/rehearsal-exclusion tests."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from pilotctl import (  # noqa: E402
    assignment_hash,
    emit_assignment,
    emit_rehearsal,
    validate_assignment,
    validate_import,
)


def _write_session(path: Path, *, ctx: dict, batch: dict | None = None):
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
    if batch:
        edge.update(batch)
    doc = {
        "measurement_batch": edge,
        "session_context": ctx,
        "collection_mode_label": "PHYSICAL DEVICE COLLECTION",
    }
    path.write_text(json.dumps(doc, indent=2))
    return path


def test_emit_rehearsal_schema_and_hash(tmp_path):
    out = tmp_path / "rehearsal_assignment.json"
    result = emit_rehearsal(out)
    assert result["ok"] is True
    doc = json.loads(out.read_text())
    assert doc["session_mode"] == "PILOT_REHEARSAL"
    assert doc["rehearsal_only"] is True
    assert doc["calibration_only"] is False
    assert doc["collection_day_id"] == "rehearsal_day"
    assert doc["matrix_cell_id"] == "rehearsal_zone_rehearsal_wifi_normal_learn"
    assert doc["named_test_zone"] == "zone_rehearsal"
    assert doc["network_condition"] == "wifi_normal"
    assert doc["expected_network_transport"] == "wifi"
    assert doc["workload_profile"] == "learn"
    assert float(doc["planned_duration_seconds"]) == 300.0
    assert doc["assignment_hash"] == assignment_hash(doc)
    validated = validate_assignment(out)
    assert validated["ok"] is True, validated["errors"]


def test_emit_assignment_pilot_hash(tmp_path):
    out = tmp_path / "pilot_assignment.json"
    result = emit_assignment(out)
    assert result["ok"] is True
    doc = json.loads(out.read_text())
    assert doc["session_mode"] == "PILOT"
    assert doc["rehearsal_only"] is False
    assert doc["calibration_only"] is False
    assert doc["assignment_hash"] == assignment_hash(doc)
    assert validate_assignment(out)["ok"] is True


def test_tampered_assignment_hash_rejected(tmp_path):
    out = tmp_path / "bad.json"
    emit_rehearsal(out)
    doc = json.loads(out.read_text())
    doc["named_test_zone"] = "zone_a"
    out.write_text(json.dumps(doc, indent=2))
    result = validate_assignment(out)
    assert result["ok"] is False
    assert any("assignment_hash" in e for e in result["errors"])


def test_rehearsal_session_excluded_from_pilot_import(tmp_path, monkeypatch):
    monkeypatch.setattr("pilotctl.SANITIZED", tmp_path / "san")
    (tmp_path / "san").mkdir()
    sess = tmp_path / "reh.json"
    _write_session(
        sess,
        ctx={
            "schema_name": "gunnchos.measurement_session_context",
            "schema_version": "1.0.0",
            "session_id": "s_reh",
            "run_id": "pixel-rehearsal-1",
            "collection_day_id": "rehearsal_day",
            "location_category": "home_or_private_indoor",
            "named_test_zone": "zone_rehearsal",
            "indoor_outdoor": "indoor",
            "stationary_or_moving": "stationary",
            "network_condition": "wifi_normal",
            "network_type": "wifi",
            "detected_network_transport": "wifi",
            "session_mode": "PILOT_REHEARSAL",
            "calibration_only": False,
            "rehearsal_only": True,
            "workload_profile": "learn",
            "planned_duration_seconds": 300,
            "actual_duration_seconds": 300,
            "start_timestamp": "2026-07-23T10:00:00Z",
            "end_timestamp": "2026-07-23T10:05:00Z",
            "device_category": "phone",
            "collector_version": "test",
            "consent_receipt_id": "rcpt_test_123456",
            "consent_captured_at": "2026-07-23T09:59:00Z",
            "environmental_notes": "",
            "degradation_method": "none",
            "operator_notes": "rehearsal_only=true",
            "protocol_deviation": "rehearsal_not_pilot",
            "evidence_level": "controlled_device_measurement",
            "matrix_cell_id": "rehearsal_zone_rehearsal_wifi_normal_learn",
            "assignment_id": "asn_testhash12abcd",
            "assignment_hash": "a" * 64,
            "protocol_version": "gate3-pilot-v1",
        },
    )
    result = validate_import(sess)
    assert result["ok"] is False
    assert any("rehearsal" in e.lower() for e in result["errors"])
    assert result["session_mode"] == "PILOT_REHEARSAL"


def test_modes_not_silently_reclassified(tmp_path, monkeypatch):
    """A CALIBRATION session cannot be imported as counting pilot evidence."""
    monkeypatch.setattr("pilotctl.SANITIZED", tmp_path / "san")
    (tmp_path / "san").mkdir()
    sess = tmp_path / "cal.json"
    _write_session(
        sess,
        ctx={
            "schema_name": "gunnchos.measurement_session_context",
            "schema_version": "1.0.0",
            "session_id": "s_cal",
            "run_id": "pixel-cal-1",
            "collection_day_id": "calibration_day",
            "location_category": "home_or_private_indoor",
            "named_test_zone": "zone_calibration",
            "indoor_outdoor": "indoor",
            "stationary_or_moving": "stationary",
            "network_condition": "wifi_normal",
            "network_type": "wifi",
            "session_mode": "CALIBRATION",
            "calibration_only": True,
            "rehearsal_only": False,
            "workload_profile": "learn",
            "planned_duration_seconds": 60,
            "actual_duration_seconds": 60,
            "start_timestamp": "2026-07-23T10:00:00Z",
            "end_timestamp": "2026-07-23T10:01:00Z",
            "device_category": "phone",
            "collector_version": "test",
            "consent_receipt_id": "rcpt_test_123456",
            "consent_captured_at": "2026-07-23T09:59:00Z",
            "environmental_notes": "",
            "degradation_method": "none",
            "operator_notes": "calibration_only=true",
            "protocol_deviation": "calibration_not_pilot",
            "evidence_level": "controlled_device_measurement",
        },
    )
    result = validate_import(sess)
    assert result["ok"] is False
    assert any("calibration" in e.lower() for e in result["errors"])


def _pilot_ctx(**overrides):
    ctx = {
        "schema_name": "gunnchos.measurement_session_context",
        "schema_version": "1.0.0",
        "session_id": "s_pilot",
        "run_id": "pixel-pilot-1",
        "collection_day_id": "day_01",
        "location_category": "library_or_community_indoor",
        "named_test_zone": "zone_a",
        "indoor_outdoor": "indoor",
        "stationary_or_moving": "stationary",
        "network_condition": "wifi_normal",
        "declared_network_condition": "wifi_normal",
        "network_type": "wifi",
        "detected_network_transport": "wifi",
        "session_mode": "PILOT",
        "calibration_only": False,
        "rehearsal_only": False,
        "workload_profile": "learn",
        "planned_duration_seconds": 300,
        "actual_duration_seconds": 300,
        "start_timestamp": "2026-07-23T10:00:00Z",
        "end_timestamp": "2026-07-23T10:05:00Z",
        "device_category": "phone",
        "collector_version": "0.4.0-gate3-pilot",
        "consent_receipt_id": "rcpt_test_123456",
        "consent_captured_at": "2026-07-23T09:59:00Z",
        "environmental_notes": "",
        "degradation_method": "none",
        "operator_notes": "",
        "protocol_deviation": None,
        "evidence_level": "controlled_device_measurement",
        "matrix_cell_id": "day_01_zone_a_wifi_normal_learn",
        "assignment_id": "asn_pilotcell000001",
        "assignment_hash": "a" * 64,
        "protocol_version": "gate3-pilot-v1",
    }
    ctx.update(overrides)
    return ctx


def _pilot_batch(**overrides):
    edge = json.loads((ROOT / "fixtures/valid/edge_measurement_batch.valid.json").read_text())
    edge["evidence_level"] = "controlled_device_measurement"
    edge["provenance"] = {
        "collector": "android_client",
        "generated_at": "2026-07-23T10:05:00Z",
        "source": "PhysicalMetricsSampler",
        "build_dirty": False,
    }
    edge["consent"] = {
        "status": "active",
        "receipt_id": "rcpt_test_123456",
        "withdrawal_supported": True,
        "captured_at": "2026-07-23T09:59:00Z",
    }
    edge["device"]["device_class"] = "phone"
    edge["device"]["os_family"] = "android"
    edge["device"]["model_label"] = "pixel_6a"
    edge["producer"] = {
        "repository": "edge-io-measurement-node",
        "commit": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        "client_version": "0.4.0-gate3-pilot",
    }
    edge["workload"] = {"profile": "learn", "service_profile": "learn_continuity", "duration_s": 300}
    edge.update(overrides)
    return edge


def test_expired_assignment_rejected(tmp_path):
    out = tmp_path / "expired.json"
    emit_rehearsal(out)
    doc = json.loads(out.read_text())
    doc["expires_at"] = "2020-01-01T00:00:00Z"
    # Recompute hash after expiry change so only expiry fails (not hash).
    from pilotctl import assignment_hash as ah

    doc["assignment_hash"] = ah(doc)
    out.write_text(json.dumps(doc, indent=2))
    result = validate_assignment(out)
    assert result["ok"] is False
    assert any("expired" in e.lower() for e in result["errors"])


def test_assignment_reuse_rejected(tmp_path, monkeypatch):
    monkeypatch.setattr("pilotctl.SANITIZED", tmp_path / "san")
    monkeypatch.setattr("pilotctl.ASSIGNMENT_LEDGER", tmp_path / "used.json")
    (tmp_path / "san").mkdir()
    from pilotctl import save_used_assignments

    save_used_assignments(
        {
            "used_assignment_ids": {
                "asn_pilotcell000001": {"session_file": "prior.json", "cell_id": "day_01_zone_a_wifi_normal_learn"}
            },
            "used_hashes": {},
        }
    )
    sess = tmp_path / "reuse.json"
    _write_session(sess, ctx=_pilot_ctx(), batch=_pilot_batch())
    result = validate_import(sess)
    assert result["ok"] is False
    assert any("already used" in e.lower() for e in result["errors"])


def test_day_zone_network_workload_mismatches(tmp_path, monkeypatch):
    monkeypatch.setattr("pilotctl.SANITIZED", tmp_path / "san")
    monkeypatch.setattr("pilotctl.ASSIGNMENT_LEDGER", tmp_path / "used.json")
    (tmp_path / "san").mkdir()

    cases = [
        ({"collection_day_id": "day_02"}, "day"),
        ({"named_test_zone": "zone_b"}, "zone"),
        ({"network_condition": "wifi_degraded"}, "network_condition"),
        ({"workload_profile": "create"}, "workload"),
    ]
    for overrides, needle in cases:
        sess = tmp_path / f"bad_{needle}.json"
        _write_session(sess, ctx=_pilot_ctx(**overrides), batch=_pilot_batch())
        result = validate_import(sess)
        assert result["ok"] is False, needle
        assert any(needle in e.lower() for e in result["errors"]), (needle, result["errors"])


def test_short_duration_rejected(tmp_path, monkeypatch):
    monkeypatch.setattr("pilotctl.SANITIZED", tmp_path / "san")
    monkeypatch.setattr("pilotctl.ASSIGNMENT_LEDGER", tmp_path / "used.json")
    (tmp_path / "san").mkdir()
    sess = tmp_path / "short.json"
    _write_session(
        sess,
        ctx=_pilot_ctx(actual_duration_seconds=120),
        batch=_pilot_batch(),
    )
    result = validate_import(sess)
    assert result["ok"] is False
    assert any("undersized" in e.lower() or "duration" in e.lower() for e in result["errors"])


def test_deleted_session_rejected(tmp_path, monkeypatch):
    monkeypatch.setattr("pilotctl.SANITIZED", tmp_path / "san")
    (tmp_path / "san").mkdir()
    sess = tmp_path / "deleted.json"
    doc = {
        "deleted": True,
        "measurement_batch": _pilot_batch(),
        "session_context": _pilot_ctx(),
        "collection_mode_label": "PHYSICAL DEVICE COLLECTION",
    }
    sess.write_text(json.dumps(doc, indent=2))
    result = validate_import(sess)
    assert result["ok"] is False
    assert any("deleted" in e.lower() for e in result["errors"])


def test_missing_producer_commit_rejected(tmp_path, monkeypatch):
    monkeypatch.setattr("pilotctl.SANITIZED", tmp_path / "san")
    monkeypatch.setattr("pilotctl.ASSIGNMENT_LEDGER", tmp_path / "used.json")
    (tmp_path / "san").mkdir()
    batch = _pilot_batch()
    batch["producer"] = {"repository": "edge-io-measurement-node", "commit": "unknown_local_build"}
    sess = tmp_path / "bad_commit.json"
    _write_session(sess, ctx=_pilot_ctx(), batch=batch)
    result = validate_import(sess)
    assert result["ok"] is False
    assert any("producer" in e.lower() or "unknown_local_build" in e.lower() for e in result["errors"])


def test_duplicate_evidence_hash_rejected(tmp_path, monkeypatch):
    monkeypatch.setattr("pilotctl.SANITIZED", tmp_path / "san")
    monkeypatch.setattr("pilotctl.ASSIGNMENT_LEDGER", tmp_path / "used.json")
    (tmp_path / "san").mkdir()
    sess = tmp_path / "dup.json"
    _write_session(sess, ctx=_pilot_ctx(), batch=_pilot_batch())
    # Place an identical hash already in sanitized store.
    import hashlib
    from shutil import copyfile

    digest = hashlib.sha256(sess.read_bytes()).hexdigest()
    prior = tmp_path / "san" / "prior.json"
    copyfile(sess, prior)
    assert hashlib.sha256(prior.read_bytes()).hexdigest() == digest
    result = validate_import(sess)
    assert result["ok"] is False
    assert any("duplicate" in e.lower() for e in result["errors"])


def test_matrix_still_has_54_cells():
    from pilotctl import load_matrix

    assert len(load_matrix()) == 54
