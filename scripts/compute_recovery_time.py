#!/usr/bin/env python3
"""Compute physical outage metrics from edge measurement batches.

Primary outcome (amended):
  total_service_outage_time_s — total duration the service is classified
  unavailable within the session (lower is better).

Secondary event-level metric:
  time_to_recovery_s — per-outage recovery duration; right-censored when the
  session ends while still unavailable (censored events are NOT treated as
  observed completed recoveries).

Unavailable classification:
  service_available==False when present, else probe_timeout in quality_flags,
  else latency_ms is null.

Interval construction uses observation timestamps; sampling cadence and
interval-censoring uncertainty are reported (half-interval bound heuristic).
"""
from __future__ import annotations

import argparse
import json
import statistics
from datetime import datetime
from pathlib import Path
from typing import Any


def _parse_ts(value: str) -> datetime:
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


def _cadence_stats(ordered: list[dict[str, Any]]) -> dict[str, Any]:
    if len(ordered) < 2:
        return {
            "median_probe_interval_s": None,
            "mean_probe_interval_s": None,
            "n_intervals": 0,
            "missing_probe_gaps": 0,
        }
    deltas = []
    for a, b in zip(ordered, ordered[1:]):
        deltas.append((_parse_ts(b["timestamp"]) - _parse_ts(a["timestamp"])).total_seconds())
    median = statistics.median(deltas)
    # Gaps > 2.5x median treated as missing-probe uncertainty markers
    missing = sum(1 for d in deltas if median and d > 2.5 * median)
    return {
        "median_probe_interval_s": float(median),
        "mean_probe_interval_s": float(sum(deltas) / len(deltas)),
        "n_intervals": len(deltas),
        "missing_probe_gaps": missing,
    }


def compute_outage_metrics(batch: dict[str, Any]) -> dict[str, Any]:
    measurements = list(batch.get("measurements") or [])
    if not measurements:
        return {
            "primary_metric": "total_service_outage_time_s",
            "total_service_outage_time_s": None,
            "time_to_recovery_events": [],
            "unit": "seconds",
            "lower_is_better": True,
            "unavailable_reason": "no_measurements",
            "outage_count": 0,
            "completed_outage_count": 0,
            "right_censored_outage_count": 0,
            "session_began_unavailable": None,
            "session_ended_unavailable": None,
        }

    try:
        ordered = sorted(measurements, key=lambda m: _parse_ts(m["timestamp"]))
    except Exception as exc:  # noqa: BLE001
        return {
            "primary_metric": "total_service_outage_time_s",
            "total_service_outage_time_s": None,
            "time_to_recovery_events": [],
            "unit": "seconds",
            "lower_is_better": True,
            "unavailable_reason": f"invalid_timestamps:{exc}",
            "outage_count": 0,
            "completed_outage_count": 0,
            "right_censored_outage_count": 0,
            "session_began_unavailable": None,
            "session_ended_unavailable": None,
        }

    cadence = _cadence_stats(ordered)
    half = (cadence["median_probe_interval_s"] or 0.0) / 2.0

    events: list[dict[str, Any]] = []
    in_outage = False
    start_ts: datetime | None = None
    start_idx = -1

    for idx, sample in enumerate(ordered):
        ts = _parse_ts(sample["timestamp"])
        unavailable = is_unavailable(sample)
        if unavailable and not in_outage:
            in_outage = True
            start_ts = ts
            start_idx = idx
        elif (not unavailable) and in_outage and start_ts is not None:
            recovery_s = (ts - start_ts).total_seconds()
            events.append(
                {
                    "metric": "time_to_recovery_s",
                    "start": start_ts.isoformat().replace("+00:00", "Z"),
                    "recovery": ts.isoformat().replace("+00:00", "Z"),
                    "time_to_recovery_s": recovery_s,
                    "outage_duration_s": recovery_s,
                    "censored": False,
                    "status": "completed",
                    "observation_bound_note": (
                        f"start/recovery observed at probe times; "
                        f"true transitions may lie within ±{half:.3f}s of probes"
                    ),
                }
            )
            in_outage = False
            start_ts = None
            start_idx = -1

    if in_outage and start_ts is not None:
        end_ts = _parse_ts(ordered[-1]["timestamp"])
        duration = (end_ts - start_ts).total_seconds()
        events.append(
            {
                "metric": "time_to_recovery_s",
                "start": start_ts.isoformat().replace("+00:00", "Z"),
                "recovery": None,
                "time_to_recovery_s": None,  # not an observed completed recovery
                "outage_duration_s": duration,
                "censored": True,
                "status": "right_censored_at_session_end",
                "observation_bound_note": (
                    f"outage ongoing at last probe; duration uses last timestamp; "
                    f"not counted as completed recovery"
                ),
                "start_sample_index": start_idx,
            }
        )

    # Primary: total unavailable duration within session
    total_outage = float(sum(e["outage_duration_s"] for e in events)) if events else 0.0

    completed = [e["time_to_recovery_s"] for e in events if not e["censored"]]
    censored_n = sum(1 for e in events if e["censored"])
    summary_secondary: dict[str, Any] = {
        "completed_recoveries_n": len(completed),
        "right_censored_n": censored_n,
        "censoring_rate": (censored_n / len(events)) if events else 0.0,
    }
    if completed:
        summary_secondary.update(
            {
                "mean_time_to_recovery_s": float(sum(completed) / len(completed)),
                "median_time_to_recovery_s": float(statistics.median(completed)),
                "max_time_to_recovery_s": float(max(completed)),
            }
        )
    else:
        summary_secondary.update(
            {
                "mean_time_to_recovery_s": None,
                "median_time_to_recovery_s": None,
                "max_time_to_recovery_s": None,
                "note": "No completed recoveries; do not impute censored events as observed recoveries",
            }
        )

    began = is_unavailable(ordered[0])
    ended = is_unavailable(ordered[-1])

    return {
        "primary_metric": "total_service_outage_time_s",
        "total_service_outage_time_s": total_outage,
        "secondary_metric": "time_to_recovery_s",
        "time_to_recovery_events": events,
        "time_to_recovery_summary": summary_secondary,
        "unit": "seconds",
        "lower_is_better": True,
        "outage_count": len(events),
        "completed_outage_count": len(completed),
        "right_censored_outage_count": censored_n,
        "session_began_unavailable": began,
        "session_ended_unavailable": ended,
        "probe_cadence": cadence,
        "interval_censoring_uncertainty_s": half,
        "practical_significance_threshold_s": 5.0,
        "practical_significance_applies_to": "total_service_outage_time_s",
        "definition": "physical_probe_outage_duration",
        "distinct_from_model_estimate": "expected_recovery_time_s",
        # Back-compat alias for older callers (not the primary scientific name)
        "metric": "total_service_outage_time_s",
        "value": total_outage,
        "censored": censored_n > 0,
    }


# Back-compat name used by older tests/CLI
def compute_recovery_time(batch: dict[str, Any]) -> dict[str, Any]:
    return compute_outage_metrics(batch)


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True)
    p.add_argument("--output", default=None)
    args = p.parse_args(argv)
    batch = json.loads(Path(args.input).read_text(encoding="utf-8"))
    result = compute_outage_metrics(batch)
    text = json.dumps(result, indent=2)
    print(text)
    if args.output:
        Path(args.output).write_text(text + "\n", encoding="utf-8")
    return 0 if result.get("total_service_outage_time_s") is not None else 2


if __name__ == "__main__":
    raise SystemExit(main())
