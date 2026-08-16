"""Reproduce a single registered R6G packet into raw digests (digital-only)."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from research.r6g.claim_firewall import assert_no_soa
from research.r6g.experiments.r6g006_cellfree_mimo_contract import run_r6g006
from research.r6g.experiments.r6g007_adaptive_ris_contract import run_r6g007
from research.r6g.experiments.r6g011_imt2030_harness import run_r6g011
from research.r6g.replication.reproduce import run_replication_suite
from research.r6g.replication.seed_registry import SEED_REGISTRY

ROOT = Path(__file__).resolve().parents[2]

RUNNERS = {
    "R6G-006": run_r6g006,
    "R6G-007": run_r6g007,
    "R6G-011": lambda seed=1: run_r6g011(),
}


def reproduce_one(packet: str, out: Path) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    if packet in ("R6G-003", "R6G-005", "R6G-009") or packet == "ALL":
        suite = run_replication_suite(out)
        assert_no_soa(suite)
        return {"ok": True, "mode": "full_or_candidate_suite", "packet": packet, "IMPROVED_STATE_OF_ART": False}

    runner = RUNNERS.get(packet)
    if runner is None:
        return {"ok": False, "error": f"no single-packet runner for {packet}; use make r6g-reproduce"}

    seeds = (SEED_REGISTRY.get("candidates") or {}).get(packet, {}).get("primary_seeds") or [1]
    rows = []
    raw = out / "raw" / packet
    raw.mkdir(parents=True, exist_ok=True)
    for seed in seeds:
        report = runner(seed=seed) if packet != "R6G-011" else runner()
        assert_no_soa(report)
        path = raw / f"seed_{seed}.json"
        path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        rows.append({"seed": seed, "path": str(path.relative_to(ROOT)), "claim_state": report.get("claim_state")})

    # Mirror pointer under research/reproduce/
    ptr = ROOT / "research" / "reproduce" / packet
    ptr.mkdir(parents=True, exist_ok=True)
    summary = {
        "packet": packet,
        "rows": rows,
        "IMPROVED_STATE_OF_ART": False,
        "PHYSICAL_REPRODUCTION_PENDING": True,
    }
    (ptr / "LAST_RUN.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"ok": True, "mode": "single_packet", **summary}


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--packet", required=True)
    p.add_argument("--out", type=Path, default=ROOT / "artifacts" / "r6g" / "replication")
    args = p.parse_args()
    result = reproduce_one(args.packet, args.out)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
