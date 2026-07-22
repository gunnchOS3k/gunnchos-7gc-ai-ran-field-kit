#!/usr/bin/env python3
"""Build the controlled pilot collection matrix CSV."""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def build_matrix(path: Path) -> int:
    zones = [
        ("zone_a", "library_or_community_indoor"),
        ("zone_b", "campus_or_office_indoor"),
        ("zone_c", "home_or_private_indoor"),
    ]
    networks = ["wifi_normal", "wifi_degraded"]
    days = ["day_01", "day_02", "day_03"]
    workloads = ["learn", "create", "sense"]
    rows = []
    for day in days:
        for zone_id, loc in zones:
            for net in networks:
                for wl in workloads:
                    rows.append(
                        {
                            "cell_id": f"{day}_{zone_id}_{net}_{wl}",
                            "collection_day_id": day,
                            "zone_id": zone_id,
                            "location_category": loc,
                            "network_condition": net,
                            "workload_profile": wl,
                            "planned_duration_seconds": 300,
                            "status": "pending",
                            "session_file": "",
                            "validation_status": "not_run",
                            "privacy_status": "not_run",
                            "notes": "",
                        }
                    )
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    return len(rows)


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--output", default=str(ROOT / "protocols" / "controlled_pilot_matrix.csv"))
    args = p.parse_args(argv)
    n = build_matrix(Path(args.output))
    print(f"wrote {n} rows to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
