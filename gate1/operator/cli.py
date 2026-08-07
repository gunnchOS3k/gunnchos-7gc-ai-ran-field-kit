"""Operator CLI for Gate 1 physical evidence workflow."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from gate1 import (
    STATUS_GATE_1_PASS,
    STATUS_LOCAL_AUTOMATION_PASS,
    STATUS_PHYSICAL_EVIDENCE_PENDING,
    STATUS_REMOTE_CI_PASS,
    STATUS_REMOTE_CI_PENDING,
)
from gate1.operator.checklist import plan_from_inventory
from gate1.operator.evidence_session import (
    accept_bundle,
    finalize_session,
    run_check,
    start_session,
    validate_bundle,
)
from gate1.operator.inventory import collect_inventory
from gate1.orchestrator.evidence_collector import accepted_physical_workstreams
from gate1.orchestrator.evidence_validator import physical_evidence_complete
from gate1.orchestrator.result_aggregator import compute_status


def _print_json(doc: object) -> None:
    print(json.dumps(doc, indent=2, sort_keys=True))


def cmd_inventory(args: argparse.Namespace) -> int:
    inv = collect_inventory()
    if args.json:
        _print_json(inv)
    else:
        print(f"host: {inv['host']['platform']}")
        print(f"assumption: {inv['assumption']}")
        for item in inv["observed_items"]:
            print(f"  [{item['presence']}] {item['item_id']} — {item['label']}")
        print("gate1_capabilities:")
        for cap in inv["gate1_capabilities"]:
            print(f"  [{cap['presence']}] {cap['label']} ({cap['workstream']})")
        _print_json(inv["summary"])
    if args.output:
        Path(args.output).write_text(json.dumps(inv, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


def cmd_plan(args: argparse.Namespace) -> int:
    if args.inventory:
        inv = json.loads(Path(args.inventory).read_text(encoding="utf-8"))
    else:
        inv = collect_inventory()
    plan = plan_from_inventory(inv)
    _print_json(plan)
    return 0


def cmd_start_session(args: argparse.Namespace) -> int:
    session = start_session(args.workstream, operator=args.operator)
    _print_json(session)
    print(f"SESSION_ID={session['session_id']}")
    return 0


def cmd_run_check(args: argparse.Namespace) -> int:
    observation = {}
    if args.observation_json:
        observation = json.loads(Path(args.observation_json).read_text(encoding="utf-8"))
    try:
        entry = run_check(
            args.session,
            args.check,
            result=args.result,
            observation=observation,
            capability_presence=args.capability_presence,
        )
    except ValueError as exc:
        print(f"CHECK_REFUSED {exc}", file=sys.stderr)
        return 2
    _print_json(entry)
    return 0


def cmd_finalize(args: argparse.Namespace) -> int:
    bundle = finalize_session(args.session, claim_level=args.claim_level)
    _print_json({"bundle_id": bundle["bundle_id"], "evidence_class": bundle["evidence_class"], "claim_level": bundle["claim_level"]})
    print(f"BUNDLE={args.session}/bundle.json path hint under gate1/evidence/pending/sessions/")
    return 0


def cmd_validate_bundle(args: argparse.Namespace) -> int:
    ok, issues = validate_bundle(Path(args.bundle))
    _print_json({"ok": ok, "issues": issues})
    return 0 if ok else 1


def cmd_accept_bundle(args: argparse.Namespace) -> int:
    try:
        result = accept_bundle(Path(args.bundle), Path(args.decision_record))
    except ValueError as exc:
        print(f"ACCEPT_REFUSED {exc}", file=sys.stderr)
        return 2
    _print_json(result)
    print("ACCEPTED — physical claims updated only for this workstream")
    return 0


def cmd_final_status(_args: argparse.Namespace) -> int:
    status = compute_status(None)
    # Prefer latest run if present
    from gate1.orchestrator import RUNS
    from gate1.orchestrator.evidence_collector import list_bucket

    runs = [p for p in list_bucket(RUNS) if p.name.startswith("run_")]
    if runs:
        latest = max(runs, key=lambda p: p.stat().st_mtime)
        payload = json.loads(latest.read_text(encoding="utf-8"))
        status = compute_status(payload)

    phys = accepted_physical_workstreams()
    physical_complete = physical_evidence_complete(phys)
    software_ok = bool(status.get("software_ok"))

    local = STATUS_LOCAL_AUTOMATION_PASS if software_ok else status["overall"]
    evidence_md = Path(__file__).resolve().parents[1] / "reports" / "GATE_1_REMOTE_CI_EVIDENCE.md"
    remote = STATUS_REMOTE_CI_PENDING
    if evidence_md.is_file():
        text = evidence_md.read_text(encoding="utf-8")
        if "`GATE_1_REMOTE_CI_PASS`" in text or "GATE_1_REMOTE_CI_PASS" in text.split("## Status", 1)[-1][:200]:
            remote = STATUS_REMOTE_CI_PASS
    physical = (
        STATUS_GATE_1_PASS if physical_complete else STATUS_PHYSICAL_EVIDENCE_PENDING
    )
    # Never emit GATE_1_PASS as overall without physical
    overall = STATUS_GATE_1_PASS if physical_complete and software_ok else local
    if overall == STATUS_GATE_1_PASS and not physical_complete:
        overall = local

    doc = {
        "overall": overall if physical_complete else local,
        "tokens": {
            "local_automation": local,
            "remote_ci": remote,
            "physical": physical if not physical_complete else "GATE_1_PHYSICAL_EVIDENCE_ACCEPTED",
            "gate_1_pass_allowed": physical_complete and software_ok,
        },
        "physical_workstreams_accepted": sorted(phys),
        "physical_complete": physical_complete,
        "prohibited_without_physical": STATUS_GATE_1_PASS,
        "gate2_entry": (
            "GATE_2_ELIGIBLE"
            if physical_complete and software_ok
            else "GATE_2_NOT_STARTED_GATE_1_INCOMPLETE"
        ),
        "software_ok": software_ok,
        "orchestrator_overall": status["overall"],
        "orchestrator_secondary": status["secondary"],
    }
    _print_json(doc)
    print(doc["tokens"]["local_automation"], doc["tokens"]["remote_ci"], doc["tokens"]["physical"])
    print(doc["gate2_entry"])
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="gate1.operator.cli", description="Gate 1 operator physical system")
    sub = p.add_subparsers(dest="command", required=True)

    inv = sub.add_parser("inventory", help="Probe host/USB/ADB; never invent hardware")
    inv.add_argument("--json", action="store_true")
    inv.add_argument("--output", default=None)
    inv.set_defaults(func=cmd_inventory)

    plan = sub.add_parser("plan", help="Build workstream plan from inventory")
    plan.add_argument("--inventory", default=None, help="Path to inventory JSON")
    plan.set_defaults(func=cmd_plan)

    start = sub.add_parser("start-session", help="Start a physical evidence session")
    start.add_argument("--workstream", required=True, choices=["boot", "ring-auth", "dock", "ai-runtime", "games"])
    start.add_argument("--operator", default="operator")
    start.set_defaults(func=cmd_start_session)

    chk = sub.add_parser("run-check", help="Record a checklist observation")
    chk.add_argument("--session", required=True)
    chk.add_argument("--check", required=True)
    chk.add_argument("--result", required=True, choices=["pass", "fail", "blocked", "skipped"])
    chk.add_argument(
        "--capability-presence",
        default="MISSING_ASSUMED",
        choices=[
            "PRESENT_CONFIRMED",
            "MISSING",
            "MISSING_ASSUMED",
            "TOOLCHAIN_MISSING",
            "UNSUPPORTED_PLATFORM",
            "PERMISSION_DENIED",
            "INDETERMINATE",
        ],
    )
    chk.add_argument("--observation-json", default=None)
    chk.set_defaults(func=cmd_run_check)

    fin = sub.add_parser("finalize-session", help="Finalize + redact session into a bundle")
    fin.add_argument("--session", required=True)
    fin.add_argument("--claim-level", default=None)
    fin.set_defaults(func=cmd_finalize)

    val = sub.add_parser("validate-bundle", help="Validate bundle schema/hash (does not accept)")
    val.add_argument("--bundle", required=True)
    val.set_defaults(func=cmd_validate_bundle)

    acc = sub.add_parser("accept-bundle", help="Accept bundle with explicit Edmund decision record")
    acc.add_argument("--bundle", required=True)
    acc.add_argument("--decision-record", required=True)
    acc.set_defaults(func=cmd_accept_bundle)

    sub.add_parser("final-status", help="Print Gate 1 closure + Gate 2 entry tokens").set_defaults(
        func=cmd_final_status
    )
    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
