#!/usr/bin/env python3
"""Canonical Gate 2 contract validation for the field-kit."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

try:
    import jsonschema
    from jsonschema import Draft202012Validator
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "jsonschema is required. Install with: pip install 'jsonschema>=4.20'"
    ) from exc

SCHEMA_FILES = {
    "gunnchos.edge_measurement_batch": "edge_measurement_batch.v1.schema.json",
    "gunnchos.twin_state_bundle": "twin_state_bundle.v1.schema.json",
    "gunnchos.airan_decision_bundle": "airan_decision_bundle.v1.schema.json",
    "gunnchos.resilience_decision_bundle": "resilience_decision_bundle.v1.schema.json",
    "gunnchos.integrated_run_manifest": "integrated_run_manifest.v1.schema.json",
    "gunnchos.measurement_session_context": "measurement_session_context.v1.schema.json",
    "gunnchos.controlled_dataset_manifest": "controlled_dataset_manifest.v1.schema.json",
    "gunnchos.external_dataset_record": "external_dataset_record.v1.schema.json",
    "gunnchos.gate3_evidence_report": "gate3_evidence_report.v1.schema.json",
}

PROHIBITED_KEY_PATTERNS = [
    re.compile(p, re.IGNORECASE)
    for p in (
        r"^gps$",
        r"^latitude$",
        r"^longitude$",
        r"^lat$",
        r"^lon$",
        r"^lng$",
        r"^email$",
        r"^e[-_]?mail$",
        r"^phone$",
        r"^phone[-_]?number$",
        r"^student[-_]?id$",
        r"^serial$",
        r"^serial[-_]?number$",
        r"^imei$",
        r"^imsi$",
        r"^mac$",
        r"^mac[-_]?address$",
        r"^advertising[-_]?id$",
        r"^aaid$",
        r"^idfa$",
        r"^persistent[-_]?device[-_]?id$",
        r"^device[-_]?serial$",
        r"^raw[-_]?gps$",
        r"^coordinates$",
    )
]

PROHIBITED_VALUE_PATTERNS = [
    re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE),
    re.compile(r"\b(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}\b"),
    re.compile(r"\b(?:[0-9A-F]{2}:){5}[0-9A-F]{2}\b", re.IGNORECASE),
    re.compile(r"\b\d{15}\b"),  # IMEI-like
]


class ContractError(ValueError):
    """Raised when a Gate 2 contract document is invalid."""


def parse_semver(version: str) -> tuple[int, int, int]:
    match = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)", version.strip())
    if not match:
        raise ContractError(f"Invalid semantic version: {version!r}")
    return int(match.group(1)), int(match.group(2)), int(match.group(3))


def check_compatible_version(
    document_version: str,
    supported_major: int = 1,
    *,
    label: str = "schema_version",
) -> None:
    major, _, _ = parse_semver(document_version)
    if major != supported_major:
        raise ContractError(
            f"Unsupported {label} major version {major} "
            f"(supported major={supported_major}); refusing silent ignore"
        )


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ContractError(f"Invalid JSON in {path}: {exc}") from exc


def resolve_schema_dir(schema_dir: Path | None = None) -> Path:
    if schema_dir is not None:
        return schema_dir.resolve()
    env = Path(__file__).resolve().parents[1] / "contracts"
    return env


def load_schema(schema_name: str, schema_dir: Path) -> dict[str, Any]:
    filename = SCHEMA_FILES.get(schema_name)
    if filename is None:
        raise ContractError(f"Unknown schema_name: {schema_name}")
    path = schema_dir / filename
    if not path.is_file():
        raise ContractError(f"Schema file not found: {path}")
    return load_json(path)


def find_prohibited_identifiers(
    obj: Any, path: str = "$"
) -> list[str]:
    """Recursively inspect nested objects for prohibited direct identifiers."""
    findings: list[str] = []
    if isinstance(obj, dict):
        for key, value in obj.items():
            child = f"{path}.{key}"
            if any(pat.search(str(key)) for pat in PROHIBITED_KEY_PATTERNS):
                findings.append(f"prohibited key at {child}")
            findings.extend(find_prohibited_identifiers(value, child))
    elif isinstance(obj, list):
        for idx, item in enumerate(obj):
            findings.extend(find_prohibited_identifiers(item, f"{path}[{idx}]"))
    elif isinstance(obj, str):
        for pat in PROHIBITED_VALUE_PATTERNS:
            if pat.search(obj):
                findings.append(f"prohibited value pattern at {path}: {obj[:48]}")
                break
    return findings


def validate_document(
    document: dict[str, Any],
    schema_dir: Path,
    *,
    expected_schema_name: str | None = None,
    enforce_privacy: bool = True,
) -> dict[str, Any]:
    if not isinstance(document, dict):
        raise ContractError("Document must be a JSON object")
    schema_name = document.get("schema_name")
    if not isinstance(schema_name, str):
        raise ContractError("Missing required field: schema_name")
    if expected_schema_name and schema_name != expected_schema_name:
        raise ContractError(
            f"Expected schema_name={expected_schema_name!r}, got {schema_name!r}"
        )
    version = document.get("schema_version")
    if not isinstance(version, str):
        raise ContractError("Missing required field: schema_version")
    check_compatible_version(version)

    for field in ("run_id", "site_id"):
        if field not in document or not str(document[field]).strip():
            # Session-context documents carry run_id but not always site_id.
            if schema_name == "gunnchos.measurement_session_context" and field == "site_id":
                continue
            if schema_name in {
                "gunnchos.controlled_dataset_manifest",
                "gunnchos.external_dataset_record",
                "gunnchos.gate3_evidence_report",
            }:
                continue
            raise ContractError(f"Missing required field: {field}")

    schema = load_schema(schema_name, schema_dir)
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(document), key=lambda e: list(e.path))
    if errors:
        messages = []
        for err in errors[:20]:
            loc = ".".join(str(p) for p in err.path) or "<root>"
            messages.append(f"{loc}: {err.message}")
        raise ContractError("Schema validation failed:\n- " + "\n- ".join(messages))

    if enforce_privacy and schema_name == "gunnchos.edge_measurement_batch":
        findings = find_prohibited_identifiers(document)
        if findings:
            raise ContractError(
                "Prohibited direct identifiers detected:\n- " + "\n- ".join(findings)
            )
        privacy = document.get("privacy") or {}
        if privacy.get("contains_direct_identifiers") is True:
            raise ContractError(
                "privacy.contains_direct_identifiers must be false for accepted batches"
            )
        evidence = document.get("evidence_level")
        collector = (document.get("provenance") or {}).get("collector")
        consent_status = (document.get("consent") or {}).get("status")
        if evidence == "controlled_device_measurement":
            if collector not in {"physical_device", "android_client"}:
                raise ContractError(
                    "evidence_level=controlled_device_measurement requires "
                    "provenance.collector in {physical_device, android_client}"
                )
            if consent_status != "active":
                raise ContractError(
                    "controlled_device_measurement requires consent.status=active"
                )
        if evidence == "synthetic" and collector != "deterministic_emulator":
            raise ContractError(
                "evidence_level=synthetic requires provenance.collector="
                "deterministic_emulator"
            )
        producer = document.get("producer") or {}
        commit = producer.get("commit")
        if not isinstance(commit, str) or not re.fullmatch(r"[0-9a-f]{40}", commit):
            raise ContractError("producer.commit must be a 40-char lowercase git SHA")

    return {"ok": True, "schema_name": schema_name, "schema_version": version}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate Gate 2 contract documents")
    parser.add_argument("path", type=Path, help="JSON document to validate")
    parser.add_argument(
        "--schema-dir",
        type=Path,
        default=None,
        help="Directory containing canonical *.schema.json files",
    )
    parser.add_argument(
        "--expected-schema",
        default=None,
        help="Optional expected schema_name constant",
    )
    parser.add_argument(
        "--no-privacy-scan",
        action="store_true",
        help="Skip recursive privacy identifier scan",
    )
    args = parser.parse_args(argv)
    schema_dir = resolve_schema_dir(args.schema_dir)
    document = load_json(args.path)
    try:
        result = validate_document(
            document,
            schema_dir,
            expected_schema_name=args.expected_schema,
            enforce_privacy=not args.no_privacy_scan,
        )
    except ContractError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
