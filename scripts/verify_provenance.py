#!/usr/bin/env python3
"""Verify provenance hashes and run IDs across integrated artifacts."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", type=Path, required=True)
    args = parser.parse_args(argv)
    d = args.run_dir
    edge = json.loads((d / "01_edge_measurements.json").read_text())
    twin = json.loads((d / "02_twin_state.json").read_text())
    airan = json.loads((d / "03_airan_twin_informed_decision.json").read_text())
    ntn = json.loads((d / "04_resilience_decision.json").read_text())

    errors = []
    if twin["run_id"] != edge["run_id"] or airan["run_id"] != edge["run_id"] or ntn["run_id"] != edge["run_id"]:
        errors.append("run_id mismatch across chain")
    edge_hash = sha256_file(d / "01_edge_measurements.json")
    if twin["source_measurement"]["sha256"] != edge_hash:
        errors.append("twin source_measurement.sha256 does not match 01_edge_measurements.json")
    twin_hash = sha256_file(d / "02_twin_state.json")
    if airan["input_twin_state_hash"] != twin_hash:
        errors.append("airan input_twin_state_hash mismatch")
    if ntn["input_twin_state_hash"] != twin_hash:
        errors.append("ntn input_twin_state_hash mismatch")
    airan_hash = sha256_file(d / "03_airan_twin_informed_decision.json")
    if ntn["input_airan_decision_hash"] != airan_hash:
        errors.append("ntn input_airan_decision_hash mismatch")
    if errors:
        print("FAIL:\n- " + "\n- ".join(errors), file=sys.stderr)
        return 1
    print(json.dumps({"ok": True, "run_id": edge["run_id"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
