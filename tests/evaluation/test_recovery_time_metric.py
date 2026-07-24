#!/usr/bin/env python3
"""Boundary tests for total_service_outage_time_s and time_to_recovery_s."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from compute_recovery_time import (  # noqa: E402
    compute_outage_metrics,
    is_unavailable,
)


def _s(ts: str, latency, flags=None, service_available=None):
    sample = {
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
        "quality_flags": flags
        or (["ok"] if latency is not None else ["probe_timeout"]),
    }
    if service_available is not None:
        sample["service_available"] = service_available
    return sample


def test_no_outage_primary_zero():
    r = compute_outage_metrics(
        {
            "measurements": [
                _s("2026-07-24T10:00:00Z", 40.0),
                _s("2026-07-24T10:00:05Z", 42.0),
            ]
        }
    )
    assert r["total_service_outage_time_s"] == 0.0
    assert r["outage_count"] == 0
    assert r["primary_metric"] == "total_service_outage_time_s"


def test_completed_outage_primary_and_secondary():
    r = compute_outage_metrics(
        {
            "measurements": [
                _s("2026-07-24T10:00:00Z", 40.0),
                _s("2026-07-24T10:00:10Z", None, ["probe_timeout"]),
                _s("2026-07-24T10:00:25Z", 45.0, ["ok"]),
            ]
        }
    )
    assert r["total_service_outage_time_s"] == pytest.approx(15.0)
    assert r["completed_outage_count"] == 1
    assert r["right_censored_outage_count"] == 0
    ev = r["time_to_recovery_events"][0]
    assert ev["time_to_recovery_s"] == pytest.approx(15.0)
    assert ev["censored"] is False


def test_right_censored_not_observed_recovery():
    r = compute_outage_metrics(
        {
            "measurements": [
                _s("2026-07-24T10:00:00Z", 40.0),
                _s("2026-07-24T10:00:10Z", None, ["probe_timeout"]),
                _s("2026-07-24T10:00:40Z", None, ["probe_timeout"]),
            ]
        }
    )
    assert r["total_service_outage_time_s"] == pytest.approx(30.0)
    assert r["right_censored_outage_count"] == 1
    ev = r["time_to_recovery_events"][0]
    assert ev["censored"] is True
    assert ev["time_to_recovery_s"] is None
    assert r["time_to_recovery_summary"]["mean_time_to_recovery_s"] is None


def test_session_begins_unavailable():
    r = compute_outage_metrics(
        {
            "measurements": [
                _s("2026-07-24T10:00:00Z", None, ["probe_timeout"]),
                _s("2026-07-24T10:00:10Z", 40.0, ["ok"]),
            ]
        }
    )
    assert r["session_began_unavailable"] is True
    assert r["total_service_outage_time_s"] == pytest.approx(10.0)


def test_session_ends_unavailable():
    r = compute_outage_metrics(
        {
            "measurements": [
                _s("2026-07-24T10:00:00Z", 40.0),
                _s("2026-07-24T10:00:10Z", None, ["probe_timeout"]),
            ]
        }
    )
    assert r["session_ended_unavailable"] is True
    assert r["right_censored_outage_count"] == 1


def test_multiple_outage_events():
    r = compute_outage_metrics(
        {
            "measurements": [
                _s("2026-07-24T10:00:00Z", 40.0),
                _s("2026-07-24T10:00:05Z", None, ["probe_timeout"]),
                _s("2026-07-24T10:00:10Z", 40.0),
                _s("2026-07-24T10:00:20Z", None, ["probe_timeout"]),
                _s("2026-07-24T10:00:30Z", 40.0),
            ]
        }
    )
    assert r["outage_count"] == 2
    assert r["total_service_outage_time_s"] == pytest.approx(15.0)
    assert r["completed_outage_count"] == 2


def test_empty_null():
    r = compute_outage_metrics({"measurements": []})
    assert r["total_service_outage_time_s"] is None


def test_service_available_flag():
    assert is_unavailable(_s("2026-07-24T10:00:00Z", 40.0, ["ok"], False)) is True


def test_false_timeout_with_latency_still_unavailable_if_flagged():
    # Explicit probe_timeout dominates even if latency present (false timeout risk documented)
    s = _s("2026-07-24T10:00:00Z", 40.0, ["probe_timeout", "ok"])
    assert is_unavailable(s) is True


def test_missing_probe_gap_reported():
    r = compute_outage_metrics(
        {
            "measurements": [
                _s("2026-07-24T10:00:00Z", 40.0),
                _s("2026-07-24T10:00:05Z", 40.0),
                _s("2026-07-24T10:00:10Z", 40.0),
                _s("2026-07-24T10:01:40Z", 40.0),  # 90s gap vs ~5s cadence
            ]
        }
    )
    assert r["probe_cadence"]["missing_probe_gaps"] >= 1


def test_valid_fixture():
    fixture = ROOT / "fixtures" / "valid" / "edge_measurement_batch.valid.json"
    r = compute_outage_metrics(json.loads(fixture.read_text()))
    assert r["total_service_outage_time_s"] is not None
    assert r["total_service_outage_time_s"] >= 0.0
