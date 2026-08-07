"""Evidence session lifecycle — start, check, finalize, validate, accept."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from gate1.operator import ACCEPTED, REJECTED, SCHEMAS, SESSIONS
from gate1.operator.checklist import get_check
from gate1.operator.redaction import redact_obj
from gate1.orchestrator.evidence_collector import content_digest


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_schema(name: str) -> dict[str, Any]:
    return json.loads((SCHEMAS / name).read_text(encoding="utf-8"))


def validate_against(doc: dict[str, Any], schema_name: str) -> list[str]:
    schema = _load_schema(schema_name)
    validator = Draft202012Validator(schema)
    return [e.message for e in sorted(validator.iter_errors(doc), key=lambda x: list(x.path))]


def start_session(workstream: str, operator: str = "operator") -> dict[str, Any]:
    if workstream not in {"boot", "ring-auth", "dock", "ai-runtime", "games"}:
        raise ValueError(f"unsupported workstream: {workstream}")
    session_id = f"sess-{workstream}-{uuid.uuid4().hex[:10]}"
    session = {
        "schema_version": "1.0.0",
        "session_id": session_id,
        "workstream": workstream,
        "operator": operator,
        "started_at_utc": utc_now(),
        "status": "open",
        "checks": [],
        "notes": [],
    }
    path = SESSIONS / session_id
    path.mkdir(parents=True, exist_ok=True)
    (path / "session.json").write_text(json.dumps(session, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return session


def _session_dir(session_id: str) -> Path:
    path = SESSIONS / session_id
    if not path.exists():
        raise FileNotFoundError(f"session not found: {session_id}")
    return path


def load_session(session_id: str) -> dict[str, Any]:
    return json.loads((_session_dir(session_id) / "session.json").read_text(encoding="utf-8"))


def save_session(session: dict[str, Any]) -> Path:
    path = _session_dir(session["session_id"]) / "session.json"
    path.write_text(json.dumps(session, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def run_check(
    session_id: str,
    check_id: str,
    *,
    result: str,
    observation: dict[str, Any] | None = None,
    capability_presence: str = "MISSING_ASSUMED",
) -> dict[str, Any]:
    session = load_session(session_id)
    if session.get("status") != "open":
        raise RuntimeError(f"session not open: {session.get('status')}")
    meta = get_check(session["workstream"], check_id)
    if meta is None:
        raise ValueError(f"unknown check_id={check_id} for workstream={session['workstream']}")
    if result == "pass" and capability_presence != "PRESENT_CONFIRMED":
        raise ValueError(
            f"refuse PASS for {check_id}: capability_presence={capability_presence} "
            "(requires PRESENT_CONFIRMED; do not invent hardware)"
        )
    entry = {
        "check_id": check_id,
        "description": meta["description"],
        "result": result,
        "capability_presence": capability_presence,
        "observed_at_utc": utc_now(),
        "observation": observation or {},
    }
    session["checks"].append(entry)
    save_session(session)
    return entry


def finalize_session(session_id: str, *, claim_level: str | None = None) -> dict[str, Any]:
    session = load_session(session_id)
    ws = session["workstream"]
    claim = claim_level or {
        "boot": "PHYSICAL_BOOT",
        "ring-auth": "PHYSICAL_RING",
        "dock": "PHYSICAL_DOCK",
        "ai-runtime": "PHYSICAL_AI_DEVICE",
        "games": "PHYSICAL_GAME_DEVICE",
    }[ws]
    # Only mark physical if at least one check passed with PRESENT_CONFIRMED
    physical_ok = any(
        c.get("result") == "pass" and c.get("capability_presence") == "PRESENT_CONFIRMED"
        for c in session.get("checks") or []
    )
    if not physical_ok:
        evidence_class = "software"
        claim = "SOFTWARE_SLICE"
        note = "No PRESENT_CONFIRMED passing checks; refusing physical classification."
    else:
        evidence_class = "physical"
        note = "Physical classification earned from PRESENT_CONFIRMED checks."

    redacted_session = redact_obj(session)
    bundle = {
        "schema_version": "1.0.0",
        "bundle_id": f"bundle-{session_id}",
        "session_id": session_id,
        "workstream": ws,
        "evidence_class": evidence_class,
        "claim_level": claim,
        "finalized_at_utc": utc_now(),
        "session": redacted_session,
        "acceptance": {"accepted": False, "decision_record": None},
        "notes": note,
    }
    bundle["artifact_sha256"] = content_digest(bundle)
    session["status"] = "finalized"
    session["bundle_id"] = bundle["bundle_id"]
    save_session(session)
    out = _session_dir(session_id) / "bundle.json"
    out.write_text(json.dumps(bundle, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return bundle


def validate_bundle(bundle_path: Path) -> tuple[bool, list[str]]:
    doc = json.loads(bundle_path.read_text(encoding="utf-8"))
    issues = validate_against(doc, "evidence_bundle.schema.json")
    claimed = doc.get("artifact_sha256")
    if claimed != content_digest(doc):
        issues.append("artifact_sha256 mismatch")
    if doc.get("claim_level", "").startswith("PHYSICAL") and doc.get("evidence_class") != "physical":
        issues.append("PHYSICAL claim without physical evidence_class")
    return (len(issues) == 0), issues


def accept_bundle(bundle_path: Path, decision_record_path: Path) -> dict[str, Any]:
    ok, issues = validate_bundle(bundle_path)
    if not ok:
        raise ValueError(f"bundle invalid: {issues}")
    decision = json.loads(decision_record_path.read_text(encoding="utf-8"))
    d_issues = validate_against(decision, "edmund_decision_record.schema.json")
    if d_issues:
        raise ValueError(f"decision record invalid: {d_issues}")
    if decision.get("decision") != "ACCEPT":
        raise ValueError(f"decision is {decision.get('decision')!r}; ACCEPT required")
    if str(decision.get("authority") or "") not in {"Edmund Gunn Jr.", "Edmund"}:
        raise ValueError("accept-bundle requires Edmund authority on decision record")
    if not decision.get("explicit_human_decision"):
        raise ValueError("accept-bundle requires explicit_human_decision=true")

    bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
    if bundle.get("evidence_class") != "physical":
        raise ValueError("refusing accept: bundle evidence_class is not physical")

    bundle["acceptance"] = {
        "accepted": True,
        "accepted_at_utc": utc_now(),
        "decision_record": decision,
    }
    # Recompute hash after acceptance stamp
    bundle.pop("artifact_sha256", None)
    bundle["artifact_sha256"] = content_digest(bundle)

    ACCEPTED.mkdir(parents=True, exist_ok=True)
    dest = ACCEPTED / f"{bundle['bundle_id']}.json"
    dest.write_text(json.dumps(bundle, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"accepted_path": str(dest), "bundle_id": bundle["bundle_id"], "workstream": bundle["workstream"]}


def reject_bundle(bundle_path: Path, reason: str) -> Path:
    REJECTED.mkdir(parents=True, exist_ok=True)
    dest = REJECTED / bundle_path.name
    doc = json.loads(bundle_path.read_text(encoding="utf-8"))
    doc["rejection_reason"] = reason
    dest.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return dest
