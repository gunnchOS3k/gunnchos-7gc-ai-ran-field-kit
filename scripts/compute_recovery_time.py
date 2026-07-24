#!/usr/bin/env python3
"""Compute physical recovery_time_s from edge measurement batches.

Operational definition (preregistered):
  service_unavailable(sample) iff:
    - latency_ms is null, OR
    - "probe_timeout" in quality_flags, OR
    - optional service_available is False when present

  start_event: first unavailable sample after an available sample,
               or first sample if session begins unavailable
  recovery_event: first subsequent available sample after start_event

  recovery_time_s = (recovery_event.timestamp - start_event.timestamp) in seconds

  If no outage occurs: recovery_time_s = 0.0 (lower is better)
  If outage never recovers before session end: censored=True,
               recovery_time_s = (last_timestamp - start_event.timestamp)
  If measurements empty / timestamps invalid: recovery_time_s = null

This is distinct from resilience_decision_bundle.expected_recovery_time_s
(model estimate). Primary evaluation outcome uses this measured metric.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any


def _parse_ts(value: str) -> datetime:
    # Accept Z suffix
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    return datetime.fromisoformat(value)


def is_unavailable(sample: dict[str, Any]) -> bool:
    if "service_available" in sample and sample["service_available"] is not None:
        return not bool(sample["service_available"])
    flags = sample.get("quality_flags") or []
    if "probe_timeout" in flags:
        return True
    if sample.get("latency_ms") is None:
        return True
    return False


def compute_recovery_time(batch: dict[str, Any]) -> dict[str, Any]:
    measurements = list(batch.get("measurements") or [])
    if not measurements:
        return {
            "metric": "recovery_time_s",
            "value": None,
            "unit": "seconds",
            "lower_is_better": True,
            "unavailable_reason": "no_measurements",
            "censored": False,
            "outage_count": 0,
            "definition": "physical_probe_recovery",
        }

    # Sort by timestamp
    try:
        ordered = sorted(measurements, key=lambda m: _parse_ts(m["timestamp"]))
    except Exception as exc:  # noqa: BLE001
        return {
            "metric": "recovery_time_s",
            "value": None,
            "unit": "seconds",
            "lower_is_better": True,
            "unavailable_reason": f"invalid_timestamps:{exc}",
            "censored": False,
            "outage_count": 0,
            "definition": "physical_probe_recovery",
        }

    outages: list[dict[str, Any]] = []
    in_outage = False
    start_ts: datetime | None = None

    for sample in ordered:
        ts = _parse_ts(sample["timestamp"])
        unavailable = is_unavailable(sample)
        if unavailable and not in_outage:
            in_outage = True
            start_ts = ts
        elif (not unavailable) and in_outage and start_ts is not None:
            recovery_s = (ts - start_ts).total_seconds()
            outages.append(
                {
                    "start": start_ts.isoformat().replace("+00:00", "Z"),
                    "recovery": ts.isoformat().replace("+00:00", "Z"),
                    "recovery_time_s": recovery_s,
                    "censored": False,
                }
            )
            in_outage = False
            start_ts = None

    censored = False
    if in_outage and start_ts is not None:
        end_ts = _parse_ts(ordered[-1]["timestamp"])
        recovery_s = (end_ts - start_ts).total_seconds()
        outages.append(
            {
                "start": start_ts.isoformat().replace("+00:00", "Z"),
                "recovery": None,
                "recovery_time_s": recovery_s,
                "censored": True,
            }
        )
        censored = True

    if not outages:
        value = 0.0
    else:
        # Primary session summary: total recovery time across outages
        value = float(sum(o["recovery_time_s"] for o in outages))

    return {
        "metric": "recovery_time_s",
        "value": value,
        "unit": "seconds",
        "lower_is_better": True,
        "censored": censored,
        "outage_count": len(outages),
        "outages": outages,
        "definition": "physical_probe_recovery",
        "start_event": "first_unavailable_sample",
        "recovery_event": "first_subsequent_available_sample",
        "timeout_behavior": "session_end_censoring",
        "failure_behavior": "null_only_when_no_valid_timestamps_or_empty",
        "unavailable_data_behavior": "null_latency_or_probe_timeout_counts_unavailable",
        "distinct_from_model_estimate": "expected_recovery_time_s",
    }


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True, help="edge measurement batch JSON")
    p.add_argument("--output", default=None)
    args = p.parse_args(argv)
    batch = json.loads(Path(args.input).read_text(encoding="utf-8"))
    result = compute_recovery_time(batch)
    text = json.dumps(result, indent=2)
    print(text)
    if args.output:
        Path(args.output).write_text(text + "\n", encoding="utf-8")
    return 0 if result.get("value") is not None else 2


if __name__ == "__main__":
    raise SystemExit(main())
