#!/usr/bin/env python3
"""Validate a cross-device game contract snapshot against the canonical schema."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

try:
    from jsonschema import Draft202012Validator
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "jsonschema is required. Install with: pip install 'jsonschema>=4.20'"
    ) from exc

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / "program/contracts/cross_device_game_contract.v1.schema.json"
REQUIRED_PROBE_KEYS = (
    "core_loop",
    "save_roundtrip",
    "score",
    "input",
    "accessibility",
    "presentation",
    "quality",
    "multiplayer",
    "deterministic_replay",
)
PASS_STATUSES = {"pass", "not_applicable"}
OPEN_STATUSES = {"fail", "blocked_external", "blocked_environment"}


class ContractValidationError(Exception):
    pass


def load_schema() -> dict[str, Any]:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def validate_contract(doc: dict[str, Any], schema: dict[str, Any] | None = None) -> None:
    schema = schema or load_schema()
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(doc), key=lambda e: list(e.path))
    if errors:
        msg = "; ".join(f"{'/'.join(map(str, e.path))}: {e.message}" for e in errors[:5])
        raise ContractValidationError(msg)


def probe_summary(doc: dict[str, Any]) -> dict[str, str]:
    probes = doc.get("probes") or {}
    return {name: str((probes.get(name) or {}).get("status", "missing")) for name in REQUIRED_PROBE_KEYS}


def contract_is_operationally_valid(doc: dict[str, Any]) -> bool:
    probes = doc.get("probes") or {}
    for key in REQUIRED_PROBE_KEYS:
        status = (probes.get(key) or {}).get("status")
        if status not in PASS_STATUSES:
            return False
    return True


def validate_file(path: Path) -> dict[str, Any]:
    doc = json.loads(path.read_text(encoding="utf-8"))
    validate_contract(doc)
    return doc


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("contract_json", type=Path, help="Path to contract snapshot JSON")
    parser.add_argument(
        "--require-operational",
        action="store_true",
        help="Fail unless every probe is pass or not_applicable",
    )
    args = parser.parse_args(argv)

    doc = validate_file(args.contract_json)
    summary = probe_summary(doc)
    print(json.dumps({"game_id": doc["game_id"], "probes": summary}, indent=2))
    if args.require_operational and not contract_is_operationally_valid(doc):
        print("Operational probe failure", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
