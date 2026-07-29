#!/usr/bin/env python3
"""Verify inherited CI / status dependency graph — fail closed."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GRAPH = ROOT / "STATUS_DEPENDENCY_GRAPH.json"
LOCAL_CI = ROOT / "orchestration" / "gates_4_6" / "inherited_ci_status.json"


def load_graph() -> dict:
    return json.loads(GRAPH.read_text(encoding="utf-8"))


def evaluate(status_map: dict[str, str], *, graph: dict | None = None) -> dict:
    graph = graph or load_graph()
    failures: list[str] = []
    blocked: dict[str, list[str]] = {}
    # dependency keys in graph excluding notes/schema
    for node, deps in graph.items():
        if node in ("schema_version", "description", "notes") or not isinstance(deps, list):
            continue
        bad = []
        for dep in deps:
            st = status_map.get(dep)
            if st is None:
                bad.append(f"missing_ci_evidence:{dep}")
            elif st in ("red", "fail", "failed", "FAIL", "RED", "cancelled", "skipped_due_to_failure"):
                bad.append(f"inherited_failure:{dep}:{st}")
            elif st in ("pending", "queued", "in_progress", "running", "PENDING", "RUNNING"):
                bad.append(f"still_running:{dep}:{st}")
            elif st not in ("green", "pass", "passed", "PASS", "GREEN", "success", "SUCCESS"):
                bad.append(f"unknown_or_non_success:{dep}:{st}")
        if bad:
            failures.append(node)
            blocked[node] = bad
    return {
        "ok": not failures,
        "failures": failures,
        "blocked": blocked,
        "status_map": status_map,
        "rule": "inherited failure / missing / still-running blocks dependent PASS",
    }


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--status-json", default=str(LOCAL_CI), help="Machine-readable workflow statuses")
    p.add_argument("--require-file", action="store_true", help="Fail if status file missing")
    args = p.parse_args(argv)
    path = Path(args.status_json)
    if not path.is_file():
        result = {
            "ok": False if args.require_file else False,
            "failures": ["missing_ci_evidence"],
            "blocked": {"*": [f"missing status file: {path}"]},
            "notes": "Cannot award dependent Gates while inherited CI evidence is absent",
        }
        print(json.dumps(result, indent=2))
        return 2
    doc = json.loads(path.read_text(encoding="utf-8"))
    # Support either flat map or {workflows:{name:status}}
    status_map = doc.get("workflows") if isinstance(doc.get("workflows"), dict) else doc
    # Drop metadata keys
    status_map = {
        k: v
        for k, v in status_map.items()
        if k not in ("schema_version", "updated", "source", "notes") and isinstance(v, str)
    }
    result = evaluate(status_map)
    result["source"] = str(path)
    print(json.dumps(result, indent=2))
    return 0 if result["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
