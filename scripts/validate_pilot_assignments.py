#!/usr/bin/env python3
"""Validate 54-cell pilot assignment matrix coverage and uniqueness."""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MATRIX = ROOT / "pilot" / "54_CELL_ASSIGNMENT_MATRIX.csv"
FALLBACK = ROOT / "protocols" / "controlled_pilot_matrix.csv"

REQUIRED_CELLS = 54
WORKLOADS = {"learn", "create", "sense"}
DAYS = {"day_01", "day_02", "day_03"}


def load_rows(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def validate(path: Path) -> dict:
    errors: list[str] = []
    if not path.is_file():
        return {"ok": False, "errors": [f"missing {path}"], "n": 0}

    rows = load_rows(path)
    if len(rows) != REQUIRED_CELLS:
        errors.append(f"expected {REQUIRED_CELLS} rows, got {len(rows)}")

    cell_ids = [r.get("cell_id") for r in rows]
    if len(set(cell_ids)) != len(cell_ids):
        errors.append("duplicate cell_id values")

    keys = set()
    for r in rows:
        day = r.get("collection_day_id") or r.get("day")
        zone = r.get("zone_id") or r.get("zone")
        cond = r.get("network_condition") or r.get("condition")
        wl = r.get("workload_profile") or r.get("workload")
        if day not in DAYS:
            errors.append(f"invalid day: {day}")
        if wl not in WORKLOADS:
            errors.append(f"invalid workload: {wl}")
        key = (day, zone, cond, wl)
        if key in keys:
            errors.append(f"duplicate cell key {key}")
        keys.add(key)
        dur = r.get("planned_duration_seconds")
        if dur is not None and str(dur) not in {"300", "300.0"}:
            errors.append(f"invalid duration for {r.get('cell_id')}: {dur}")

    if len(keys) != REQUIRED_CELLS and not errors:
        errors.append(f"unique keys={len(keys)} expected {REQUIRED_CELLS}")

    pending_dates = sum(
        1
        for r in rows
        if str(r.get("date_token", "")).startswith("PENDING")
        or str(r.get("status", "")).startswith("pending")
    )

    return {
        "ok": not errors,
        "errors": errors,
        "n": len(rows),
        "unique_keys": len(keys),
        "pending_design_tokens": pending_dates,
        "design_approved": pending_dates == 0,
        "matrix": str(path.relative_to(ROOT)),
    }


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--matrix", default=str(DEFAULT_MATRIX if DEFAULT_MATRIX.is_file() else FALLBACK))
    args = p.parse_args(argv)
    result = validate(Path(args.matrix))
    print(json.dumps(result, indent=2))
    # Coverage structure can validate even when design dates pending.
    return 0 if result["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
