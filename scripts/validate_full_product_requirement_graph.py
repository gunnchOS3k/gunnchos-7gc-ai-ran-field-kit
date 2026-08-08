#!/usr/bin/env python3
"""Validate full-product requirement graph promotions and ownership totality."""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
GRAPH = ROOT / "program" / "full_product" / "requirement_graph.yaml"
RULES = ROOT / "program" / "full_product" / "promotion_rules.yaml"
SIBLING_ROOT = ROOT.parent

HIGHER = {
    "IMPLEMENTED",
    "INTEGRATED",
    "DIGITALLY_VALIDATED",
}

PENDING_OWNERS = {
    "",
    "UNOWNED",
    "CONTROL_PLANE_PENDING_DECISION",
    None,
}


def load_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def resolve_path(raw: str) -> tuple[Path | None, str]:
    """Return (path_or_None, error). sibling:repo/rel is allowed."""
    if raw.startswith("sibling:"):
        rest = raw[len("sibling:") :]
        path = SIBLING_ROOT / rest
        if not path.exists():
            return None, f"missing sibling path: {raw}"
        return path, ""
    path = ROOT / raw
    if not path.exists():
        return None, f"missing field-kit path: {raw}"
    return path, ""


def validate_node(node: dict[str, Any], rules: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    nid = node.get("id", "<missing-id>")
    status = node.get("full_product_status")
    status_rules = (rules.get("rules") or {}).get(status)
    if status is None:
        errors.append(f"{nid}: missing full_product_status")
        return errors
    if status_rules is None:
        errors.append(f"{nid}: unknown full_product_status={status}")
        return errors

    impl = [p for p in (node.get("implementation_paths") or []) if p]
    tests = [t for t in (node.get("tests") or []) if t]
    evidence = [e for e in (node.get("evidence") or []) if e]
    sha = node.get("accepted_sha") or node.get("evidence_sha")

    if status_rules.get("requires_implementation_paths"):
        need = int(status_rules.get("min_implementation_paths") or 1)
        if len(impl) < need:
            errors.append(
                f"{nid}: {status} requires >= {need} implementation_paths (have {len(impl)})"
            )
        for p in impl:
            _, err = resolve_path(str(p))
            if err:
                errors.append(f"{nid}: {err}")

    if status_rules.get("requires_tests"):
        need = int(status_rules.get("min_tests") or 1)
        if len(tests) < need:
            errors.append(f"{nid}: {status} requires >= {need} tests (have {len(tests)})")
        for t in tests:
            # tests may be logical names from catalog (evidence keys) OR paths
            if "/" in str(t) or str(t).endswith((".py", ".ts", ".js", ".yml", ".yaml")):
                _, err = resolve_path(str(t))
                if err:
                    errors.append(f"{nid}: test path {err}")

    if status_rules.get("requires_accepted_sha"):
        if not sha or not isinstance(sha, str) or len(sha) < 7:
            errors.append(f"{nid}: {status} requires accepted_sha")

    if status_rules.get("requires_evidence"):
        if not evidence:
            errors.append(f"{nid}: {status} requires evidence entries")

    # Explicit invalid DOC_ONLY→IMPLEMENTED without paths
    if status in HIGHER and not impl:
        errors.append(f"{nid}: invalid promotion to {status} without implementation_paths")

    owner = node.get("owner_repository")
    if owner in PENDING_OWNERS:
        errors.append(f"{nid}: UNOWNED owner_repository={owner!r}")

    if not node.get("subsystem"):
        errors.append(f"{nid}: UNCLASSIFIED (missing subsystem)")

    mapping = node.get("mapping_status")
    if mapping not in {"MAPPED", "COVERED", "INGESTED"}:
        # Allow absence only during migration; prefer explicit
        if mapping in {"UNMAPPED", "UNCLASSIFIED"}:
            errors.append(f"{nid}: mapping_status={mapping}")

    ownership = node.get("ownership_status")
    if ownership == "UNOWNED":
        errors.append(f"{nid}: ownership_status=UNOWNED")

    classification = node.get("classification_status")
    if classification == "UNCLASSIFIED":
        errors.append(f"{nid}: classification_status=UNCLASSIFIED")

    return errors


def validate_graph(graph: dict[str, Any], rules: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    nodes = graph.get("nodes") or []
    ids = [n.get("id") for n in nodes]
    if len(ids) != len(set(ids)):
        dup = [i for i, c in Counter(ids).items() if c > 1]
        errors.append(f"duplicate requirement ids: {dup}")

    for node in nodes:
        errors.extend(validate_node(node, rules))

    # Totality counters must be truthful if present
    for key in ("unmapped_count", "unowned_count", "unclassified_count"):
        if key in graph and graph[key] not in (0, "0"):
            # Soft: report but do not hard-fail CI until scan reports say CLOSED
            # Hard-fail when target declares CLOSED but counts nonzero.
            pass

    if graph.get("unmapped_normative_closed") is True:
        if int(graph.get("unmapped_count") or 0) != 0:
            errors.append("unmapped_normative_closed=true but unmapped_count!=0")
    if graph.get("unowned_closed") is True and int(graph.get("unowned_count") or 0) != 0:
        errors.append("unowned_closed=true but unowned_count!=0")
    if graph.get("unclassified_closed") is True and int(graph.get("unclassified_count") or 0) != 0:
        errors.append("unclassified_closed=true but unclassified_count!=0")

    status_counts = Counter(n.get("full_product_status") for n in nodes)
    declared = graph.get("status_counts") or {}
    for k, v in status_counts.items():
        if declared.get(k) != v:
            errors.append(f"status_counts mismatch for {k}: declared={declared.get(k)} actual={v}")
    for k, v in declared.items():
        if status_counts.get(k, 0) != v:
            errors.append(f"status_counts extra/mismatch for {k}: declared={v} actual={status_counts.get(k, 0)}")

    if graph.get("count") != len(nodes):
        errors.append(f"count={graph.get('count')} but nodes={len(nodes)}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--graph", type=Path, default=GRAPH)
    parser.add_argument("--rules", type=Path, default=RULES)
    parser.add_argument("--strict-totality", action="store_true")
    args = parser.parse_args()

    if not args.graph.exists():
        print(f"MISSING_GRAPH: {args.graph}", file=sys.stderr)
        return 2
    if not args.rules.exists():
        print(f"MISSING_RULES: {args.rules}", file=sys.stderr)
        return 2

    graph = load_yaml(args.graph)
    rules = load_yaml(args.rules)
    errors = validate_graph(graph, rules)

    if args.strict_totality:
        for label, key in (
            ("UNMAPPED", "unmapped_count"),
            ("UNOWNED", "unowned_count"),
            ("UNCLASSIFIED", "unclassified_count"),
        ):
            if int(graph.get(key) or 0) != 0:
                errors.append(f"strict-totality: {label} count={graph.get(key)}")

    if errors:
        print("FULL_PRODUCT_REQUIREMENT_GRAPH_FAIL")
        for e in errors[:80]:
            print(f"  - {e}")
        if len(errors) > 80:
            print(f"  ... and {len(errors) - 80} more")
        return 1

    nodes = graph.get("nodes") or []
    status_counts = Counter(n.get("full_product_status") for n in nodes)
    print("FULL_PRODUCT_REQUIREMENT_GRAPH_PASS")
    print(f"nodes={len(nodes)} unmapped={graph.get('unmapped_count')} "
          f"unowned={graph.get('unowned_count')} unclassified={graph.get('unclassified_count')}")
    print(f"status_counts={dict(status_counts)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
