"""Validate Gate 1 schemas and evidence acceptance rules."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from gate1.orchestrator import ACCEPTED, CONTRACTS, PHYSICAL_CLAIM_LEVELS, REJECTED
from gate1.orchestrator.evidence_collector import (
    classify_evidence,
    content_digest,
    list_bucket,
    move_to,
    verify_artifact_hash,
)


class ValidationIssue:
    def __init__(self, code: str, message: str, severity: str = "error") -> None:
        self.code = code
        self.message = message
        self.severity = severity

    def __str__(self) -> str:
        return f"[{self.severity.upper()}] {self.code}: {self.message}"


def load_schema(name: str) -> dict[str, Any]:
    path = CONTRACTS / name
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def validate_against_schema(doc: dict[str, Any], schema_name: str) -> list[ValidationIssue]:
    schema = load_schema(schema_name)
    validator = Draft202012Validator(schema)
    return [
        ValidationIssue("SCHEMA_INVALID", f"{schema_name}: {err.message}")
        for err in sorted(validator.iter_errors(doc), key=lambda e: list(e.path))
    ]


def validate_all_contracts() -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    expected = [
        "device_identity.schema.json",
        "authenticated_input.schema.json",
        "dock_session.schema.json",
        "local_ai_runtime.schema.json",
        "game_core_loop.schema.json",
        "evidence_event.schema.json",
    ]
    for name in expected:
        path = CONTRACTS / name
        if not path.exists():
            issues.append(ValidationIssue("SCHEMA_MISSING", f"Missing {name}"))
            continue
        try:
            Draft202012Validator.check_schema(json.loads(path.read_text(encoding="utf-8")))
        except Exception as exc:  # noqa: BLE001 — surface schema errors
            issues.append(ValidationIssue("SCHEMA_BROKEN", f"{name}: {exc}"))
    return issues


def refuse_unsupported_upgrade(doc: dict[str, Any]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    try:
        classify_evidence(doc)
    except ValueError as exc:
        issues.append(ValidationIssue("CLAIM_UPGRADE_REFUSED", str(exc)))
    claim = str(doc.get("claim_level") or "")
    if claim in PHYSICAL_CLAIM_LEVELS and doc.get("evidence_class") != "physical":
        issues.append(
            ValidationIssue(
                "PHYSICAL_CLAIM_WITHOUT_PHYSICAL_EVIDENCE",
                f"claim_level={claim} rejected without physical evidence_class",
            )
        )
    return issues


def validate_evidence_file(path: Path) -> list[ValidationIssue]:
    # Orchestrator run/status aggregates are not evidence_event documents.
    if path.name.startswith(("run_", "status_")):
        return []
    issues: list[ValidationIssue] = []
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [ValidationIssue("EVIDENCE_UNREADABLE", f"{path.name}: {exc}")]
    issues.extend(refuse_unsupported_upgrade(doc))
    if "artifact_sha256" in doc and not verify_artifact_hash(path):
        issues.append(ValidationIssue("TAMPER_OR_HASH_MISMATCH", f"{path.name} hash mismatch"))
    # Optional schema if shaped like evidence_event
    if {"evidence_id", "workstream", "evidence_class", "claim_level"} <= set(doc):
        issues.extend(validate_against_schema(doc, "evidence_event.schema.json"))
    return issues


def validate_pending_and_accepted() -> tuple[list[ValidationIssue], dict[str, int]]:
    from gate1.orchestrator import PENDING

    issues: list[ValidationIssue] = []
    counts = {"pending": 0, "accepted": 0, "rejected_moved": 0}
    for path in list_bucket(PENDING) + list_bucket(ACCEPTED):
        bucket = "accepted" if path.parent == ACCEPTED else "pending"
        counts[bucket] = counts.get(bucket, 0) + 1
        file_issues = validate_evidence_file(path)
        errors = [i for i in file_issues if i.severity == "error"]
        if errors and bucket == "pending":
            move_to(REJECTED, path)
            counts["rejected_moved"] += 1
        issues.extend(file_issues)
    return issues, counts


def physical_evidence_complete(accepted_ws: set[str]) -> bool:
    required = {"boot", "ring-auth", "dock", "ai-runtime", "games"}
    return required.issubset(accepted_ws)
