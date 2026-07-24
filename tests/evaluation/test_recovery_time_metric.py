#!/usr/bin/env python3
"""Tests for physical recovery_time_s computation from edge measurement batches."""
from __future__ import annotations

import json
import sys
from copy import deepcopy
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from compute_recovery_time import compute_recovery_time, is_unavailable  # noqa: E402


def _base_sample(ts: str, latency, flags=None):
    return {
        "timestamp": ts,
        "latency_ms": latency,
        "jitter_ms": 1.0 if latency is not None else None,
        "packet_loss_pct": 0.0 if latency is not None else None,
        "upload_mbps": None,
        "download_mbps": None,
        "network_type": "wifi",
        "cpu_pct": None,
        "memory_pct": None,
        "battery_pct": 80.0,
        "charging": False,
        "thermal_state": "nominal",
        "workload_profile": "learn",
        "service_profile": "learn_continuity",
        "local_edge_response_ms": latency,
        "quality_flags": flags or (["ok"] if latency is not None else ["probe_timeout"]),
    }


def test_no_outage_zero_recovery():
    batch = {
        "measurements": [
            _base_sample("2026-07-24T10:00:00Z", 40.0),
            _base_sample("2026-07-24T10:00:05Z", 42.0),
        ]
    }
    r = compute_recovery_time(batch)
    assert r["value"] == 0.0
    assert r["outage_count"] == 0
    assert r["censored"] is False
    assert r["lower_is_better"] is True


def test_outage_and_recovery():
    batch = {
        "measurements": [
            _base_sample("2026-07-24T10:00:00Z", 40.0),
            _base_sample("2026-07-24T10:00:10Z", None, ["probe_timeout"]),
            _base_sample("2026-07-24T10:00:25Z", 45.0, ["ok"]),
        ]
    }
    r = compute_recovery_time(batch)
    assert r["value"] == pytest.approx(15.0)
    assert r["outage_count"] == 1
    assert r["censored"] is False


def test_censored_outage_at_session_end():
    batch = {
        "measurements": [
            _base_sample("2026-07-24T10:00:00Z", 40.0),
            _base_sample("2026-07-24T10:00:10Z", None, ["probe_timeout"]),
            _base_sample("2026-07-24T10:00:40Z", None, ["probe_timeout"]),
        ]
    }
    r = compute_recovery_time(batch)
    assert r["value"] == pytest.approx(30.0)
    assert r["censored"] is True


def test_empty_measurements_null():
    r = compute_recovery_time({"measurements": []})
    assert r["value"] is None
    assert r["unavailable_reason"] == "no_measurements"


def test_service_available_flag_overrides():
    s = _base_sample("2026-07-24T10:00:00Z", 40.0, ["ok"])
    s["service_available"] = False
    assert is_unavailable(s) is True


def test_valid_fixture_computes():
    fixture = ROOT / "fixtures" / "valid" / "edge_measurement_batch.valid.json"
    batch = json.loads(fixture.read_text())
    r = compute_recovery_time(batch)
    assert r["value"] is not None
    assert r["value"] >= 0.0


def test_distinct_from_model_estimate_field():
    r = compute_recovery_time(
        {"measurements": [_base_sample("2026-07-24T10:00:00Z", 1.0)]}
    )
    assert r["distinct_from_model_estimate"] == "expected_recovery_time_s"
