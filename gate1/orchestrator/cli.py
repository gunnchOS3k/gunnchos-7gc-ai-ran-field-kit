"""CLI for Gate 1 integrated development platform orchestrator."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from gate1 import STATUS_AUTOMATED_PASS, STATUS_GATE_1_PASS, STATUS_PHYSICAL_PENDING
from gate1.orchestrator.component_runner import discover_sibling_repos, run_components
from gate1.orchestrator.evidence_collector import ingest_path
from gate1.orchestrator.evidence_validator import validate_all_contracts, validate_pending_and_accepted
from gate1.orchestrator.result_aggregator import (
    compute_status,
    equipment_inventory,
    generate_reports,
)


def cmd_run(args: argparse.Namespace) -> int:
    repos_root = Path(args.repos_root) if args.repos_root else None
    output_dir = Path(args.output_dir) if args.output_dir else None
    no_write = bool(args.no_write)
    payload = run_components(repos_root, output_dir=output_dir, no_write=no_write)
    status = compute_status(payload)
    paths = generate_reports(payload, status, output_dir=output_dir, no_write=no_write)
    print(
        json.dumps(
            {
                "ok": payload.get("ok"),
                "status": status["overall"],
                "secondary": status["secondary"],
                "write_mode": payload.get("write_mode"),
                "reports_written": len(paths),
            },
            indent=2,
        )
    )
    print(f"reports_written={len(paths)}")
    print(status["overall"], status["secondary"])
    if status["overall"] == STATUS_GATE_1_PASS:
        if not status["physical_complete"]:
            print("REFUSING GATE_1_PASS without physical evidence", file=sys.stderr)
            return 2
    if not payload.get("ok"):
        return 1
    return 0


def cmd_ingest(args: argparse.Namespace) -> int:
    src = Path(args.path)
    if not src.exists():
        print(f"NOT_FOUND {src}", file=sys.stderr)
        return 1
    try:
        dest, mode = ingest_path(src)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"INGEST_FAIL {exc}", file=sys.stderr)
        return 1
    print(f"INGEST_OK mode={mode} path={dest}")
    return 0


def cmd_validate(_args: argparse.Namespace) -> int:
    issues = validate_all_contracts()
    ev_issues, counts = validate_pending_and_accepted()
    issues.extend(ev_issues)
    errors = [i for i in issues if i.severity == "error"]
    for i in issues:
        print(i)
    print(json.dumps({"counts": counts, "errors": len(errors)}, indent=2))
    return 1 if errors else 0


def cmd_status(args: argparse.Namespace) -> int:
    if args.equipment_inventory:
        print(json.dumps(equipment_inventory(Path(args.repos_root) if args.repos_root else None), indent=2))
        return 0
    from gate1.orchestrator import PENDING, RUNS
    from gate1.orchestrator.evidence_collector import list_bucket

    run_payload = None
    runs = [p for p in list_bucket(RUNS) if p.name.startswith("run_")]
    if not runs:
        runs = [p for p in list_bucket(PENDING) if p.name.startswith("run_")]
    if runs:
        latest = max(runs, key=lambda p: p.stat().st_mtime)
        run_payload = json.loads(latest.read_text(encoding="utf-8"))
    status = compute_status(run_payload)
    discovery = discover_sibling_repos(Path(args.repos_root) if args.repos_root else None)
    print(f"overall: {status['overall']}")
    print(f"secondary: {status['secondary']}")
    print(f"software_ok: {status['software_ok']}")
    print(f"physical_complete: {status['physical_complete']}")
    print(f"prohibited_without_physical: {STATUS_GATE_1_PASS}")
    print(f"siblings: {discovery['sibling_count']}")
    print(f"repo_lock_present: {discovery['repo_lock_present']}")
    for row in status["gate1_criteria"]:
        print(f"  {row['criterion_id']} ({row['workstream']}): {row['status']}")
    if status["software_ok"] and not status["physical_complete"]:
        print(STATUS_AUTOMATED_PASS, STATUS_PHYSICAL_PENDING)
    else:
        print(status["overall"], status["secondary"])
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="gate1.orchestrator.cli", description="Gate 1 IDP orchestrator")
    p.add_argument("--repos-root", default=None, help="Sibling repos root (default: ROOT.parent)")
    sub = p.add_subparsers(dest="command", required=True)

    r = sub.add_parser("run", help="Discover, validate schemas, run software probes, write evidence")
    r.add_argument(
        "--output-dir",
        default=None,
        help="Write pending/runs/reports under this directory instead of gate1/evidence and gate1/reports",
    )
    r.add_argument(
        "--no-write",
        action="store_true",
        help="Dry-run: compute results without writing evidence or reports (keeps git clean)",
    )
    r.set_defaults(func=cmd_run)

    ing = sub.add_parser("ingest-evidence", help="Ingest an evidence JSON into pending/")
    ing.add_argument("path")
    ing.set_defaults(func=cmd_ingest)

    sub.add_parser("validate-evidence", help="Validate schemas and evidence hashes/classes").set_defaults(
        func=cmd_validate
    )

    st = sub.add_parser("status", help="Show Gate 1 status tokens")
    st.add_argument("--equipment-inventory", action="store_true")
    st.set_defaults(func=cmd_status)
    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
