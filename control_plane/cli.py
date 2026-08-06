"""CLI for Gate 0 control plane."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from control_plane import STATUS_AUTOMATED_PASS, STATUS_CHARTER_PENDING
from control_plane.catalog.claims_catalog import is_transition_allowed
from control_plane.generate import generate_all
from control_plane.io_util import load_yaml
from control_plane.paths import BACKLOG, CLAIMS, GATES, REPOSITORIES, REQUIREMENTS, ROOT
from control_plane.reports import generate_reports
from control_plane.validators import issues_block_exit, validate_control_plane


def cmd_generate(_args: argparse.Namespace) -> int:
    meta = generate_all()
    paths = generate_reports(meta)
    print(f"Generated control plane: {meta['requirement_count']} requirements, {meta['claim_count']} claims")
    print(f"Reports: {len(paths)}")
    print(" ".join([STATUS_AUTOMATED_PASS, STATUS_CHARTER_PENDING]))
    return 0


def cmd_validate(_args: argparse.Namespace) -> int:
    issues = validate_control_plane()
    errors = [i for i in issues if i.severity == "error"]
    warnings = [i for i in issues if i.severity == "warning"]
    for i in issues:
        print(i)
    if errors:
        print(f"VALIDATE_FAIL errors={len(errors)} warnings={len(warnings)}")
        return 1
    print(f"VALIDATE_OK errors=0 warnings={len(warnings)}")
    print(" ".join([STATUS_AUTOMATED_PASS, STATUS_CHARTER_PENDING]))
    return 0


def cmd_audit(args: argparse.Namespace) -> int:
    # Ensure artifacts exist
    if not (REQUIREMENTS / "requirements.yaml").exists():
        generate_all()
        generate_reports()
    code = cmd_validate(args)
    inv = load_yaml(REPOSITORIES / "repository_inventory.yaml")
    print(f"Repositories audited: {len(inv.get('repositories') or [])}")
    return code


def cmd_status(_args: argparse.Namespace) -> int:
    gate = load_yaml(GATES / "gate_status.yaml")
    approval = load_yaml(ROOT / "program/charters/CHARTER_APPROVAL_RECORD.yaml")
    print(f"overall: {gate.get('overall_status_token')}")
    print(f"secondary: {gate.get('secondary_status_token')}")
    print(f"charter: {approval.get('status')}")
    print(f"prohibited: {gate.get('prohibited_status_token')} (must not be emitted)")
    criteria = gate.get("criteria") or []
    g0 = [c for c in criteria if c.get("gate") == 0]
    for c in g0:
        print(f"  {c['criterion_id']}: {c['status']}")
    return 0


def cmd_trace(args: argparse.Namespace) -> int:
    reqs = load_yaml(REQUIREMENTS / "requirements.yaml")["requirements"]
    rid = args.id
    match = next((r for r in reqs if r["id"] == rid), None)
    if not match:
        print(f"NOT_FOUND {rid}", file=sys.stderr)
        return 1
    print(json.dumps(match, indent=2, sort_keys=False))
    claims = load_yaml(CLAIMS / "claims.yaml")["claims"]
    clm = next((c for c in claims if c["requirement_id"] == rid), None)
    if clm:
        print("--- claim ---")
        print(json.dumps(clm, indent=2))
    return 0


def cmd_gate(args: argparse.Namespace) -> int:
    gate_n = int(args.n)
    criteria = load_yaml(GATES / "gate_status.yaml")["criteria"]
    rows = [c for c in criteria if int(c["gate"]) == gate_n]
    if not rows:
        print(f"No criteria for gate {gate_n}", file=sys.stderr)
        return 1
    for c in rows:
        print(
            f"{c['criterion_id']}\t{c['status']}\t{c['automatable']}\t"
            f"blockers={','.join(c.get('blockers') or []) or '-'}\t{c['criterion']}"
        )
    return 0


def cmd_repo(args: argparse.Namespace) -> int:
    name = args.name
    inv = load_yaml(REPOSITORIES / "repository_inventory.yaml")["repositories"]
    rows = [r for r in inv if r["name"] == name or r["name"].endswith(name)]
    if not rows:
        print(f"NOT_FOUND {name}", file=sys.stderr)
        return 1
    print(json.dumps(rows[0], indent=2))
    own = load_yaml(REPOSITORIES / "repository_ownership.yaml")
    reqs = own.get("owner_to_requirements", {}).get(name, [])
    print(f"owned_requirements: {len(reqs)}")
    return 0


def cmd_claims(_args: argparse.Namespace) -> int:
    claims = load_yaml(CLAIMS / "claims.yaml")["claims"]
    counts: dict[str, int] = {}
    for c in claims:
        counts[c["claim_state"]] = counts.get(c["claim_state"], 0) + 1
    for k in sorted(counts):
        print(f"{k}: {counts[k]}")
    return 0


def cmd_blockers(_args: argparse.Namespace) -> int:
    reqs = load_yaml(REQUIREMENTS / "requirements.yaml")["requirements"]
    counts: dict[str, int] = {}
    for r in reqs:
        for b in r.get("blockers") or []:
            counts[b] = counts.get(b, 0) + 1
    for k in sorted(counts, key=lambda x: (-counts[x], x)):
        print(f"{k}: {counts[k]}")
    return 0


def cmd_backlog(args: argparse.Namespace) -> int:
    cls = args.klass
    mapping = {
        "AUTOMATABLE_NOW": "cursor_automatable_backlog.yaml",
        "HUMAN": "human_action_backlog.yaml",
        "PHYSICAL": "physical_work_backlog.yaml",
        "EXTERNAL": "external_dependency_backlog.yaml",
        "MASTER": "master_gap_backlog.yaml",
    }
    # Also allow exact blocker class filter on master
    path = BACKLOG / mapping.get(cls, "master_gap_backlog.yaml")
    gaps = load_yaml(path)["gaps"]
    if cls not in mapping:
        gaps = [g for g in gaps if g.get("class") == cls or cls in (g.get("blockers") or [])]
    for g in gaps:
        print(f"{g['gap_id']}\t{g['class']}\t{g['requirement_id']}\t{g['title']}")
    print(f"count={len(gaps)}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="control_plane", description="Gate 0 ecosystem control plane")
    sub = p.add_subparsers(dest="command", required=True)

    sub.add_parser("generate", help="Generate YAML/JSON artifacts and reports").set_defaults(func=cmd_generate)
    sub.add_parser("validate", help="Validate schemas and control-plane invariants").set_defaults(func=cmd_validate)
    sub.add_parser("audit", help="Generate if needed and validate").set_defaults(func=cmd_audit)
    sub.add_parser("status", help="Show Gate 0 status tokens").set_defaults(func=cmd_status)

    t = sub.add_parser("trace", help="Trace a requirement ID")
    t.add_argument("id")
    t.set_defaults(func=cmd_trace)

    g = sub.add_parser("gate", help="Show gate criteria")
    g.add_argument("n")
    g.set_defaults(func=cmd_gate)

    r = sub.add_parser("repo", help="Show repository inventory entry")
    r.add_argument("name")
    r.set_defaults(func=cmd_repo)

    sub.add_parser("claims", help="Claim state histogram").set_defaults(func=cmd_claims)
    sub.add_parser("blockers", help="Blocker histogram").set_defaults(func=cmd_blockers)

    b = sub.add_parser("backlog", help="Show backlog by class")
    b.add_argument("--class", dest="klass", required=True)
    b.set_defaults(func=cmd_backlog)

    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))
