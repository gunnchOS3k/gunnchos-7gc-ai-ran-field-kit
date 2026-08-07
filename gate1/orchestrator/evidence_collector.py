"""Collect, hash, and classify Gate 1 evidence artifacts."""

from __future__ import annotations

import hashlib
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from gate1.orchestrator import ACCEPTED, PENDING, RUNS

# Mutable write targets — may be redirected via configure_write_paths / --output-dir
_pending_override: Path | None = None
_runs_override: Path | None = None
_no_write: bool = False


def configure_write_paths(
    *,
    pending: Path | None = None,
    runs: Path | None = None,
    no_write: bool = False,
) -> None:
    """Redirect or disable evidence writes (for --output-dir / --no-write)."""
    global _pending_override, _runs_override, _no_write
    _pending_override = pending
    _runs_override = runs
    _no_write = no_write


def reset_write_paths() -> None:
    configure_write_paths(pending=None, runs=None, no_write=False)


def _pending_bucket() -> Path:
    return _pending_override if _pending_override is not None else PENDING


def _runs_bucket() -> Path:
    return _runs_override if _runs_override is not None else RUNS


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def tool_versions() -> dict[str, str]:
    return {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "gate1_orchestrator": "0.1.0",
    }


def content_digest(doc: dict[str, Any]) -> str:
    core = {k: v for k, v in doc.items() if k != "artifact_sha256"}
    return sha256_bytes(json.dumps(core, indent=2, sort_keys=True).encode("utf-8"))


def classify_evidence(doc: dict[str, Any]) -> str:
    """Return evidence_class; refuse silent physical claim upgrades."""
    cls = str(doc.get("evidence_class") or "").lower()
    if cls not in {"software", "simulated", "physical"}:
        raise ValueError(f"unsupported evidence_class: {cls!r}")
    claim = str(doc.get("claim_level") or "")
    if claim.startswith("PHYSICAL") and cls != "physical":
        raise ValueError(
            f"refuse claim upgrade: claim_level={claim} requires evidence_class=physical, got {cls}"
        )
    return cls


def _write_json(bucket: Path, name: str, payload: dict[str, Any]) -> Path | None:
    enriched = dict(payload)
    enriched.setdefault("tool_versions", tool_versions())
    enriched.setdefault("collected_at_utc", utc_now())
    enriched["artifact_sha256"] = content_digest(enriched)
    if _no_write:
        return None
    bucket.mkdir(parents=True, exist_ok=True)
    path = bucket / name
    path.write_text(json.dumps(enriched, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def write_pending(name: str, payload: dict[str, Any]) -> Path | None:
    """Write a Gate 1 evidence_event-shaped artifact into pending/."""
    return _write_json(_pending_bucket(), name, payload)


def write_run(name: str, payload: dict[str, Any]) -> Path | None:
    """Write orchestrator run/status aggregates outside evidence acceptance buckets."""
    return _write_json(_runs_bucket(), name, payload)


def ingest_path(src: Path) -> tuple[Path, str]:
    """Ingest an evidence JSON file into pending after classification."""
    raw = src.read_text(encoding="utf-8")
    doc = json.loads(raw)
    classify_evidence(doc)
    dest_name = f"ingested_{src.stem}_{sha256_bytes(raw.encode())[:12]}.json"
    dest = _pending_bucket() / dest_name
    if dest.exists():
        return dest, "idempotent_hit"
    enriched = dict(doc)
    enriched["artifact_path"] = str(src.resolve())
    written = write_pending(dest_name, enriched)
    if written is None:
        return dest, "no_write"
    return written, "ingested"


def list_bucket(bucket: Path) -> list[Path]:
    if not bucket.exists():
        return []
    return sorted(p for p in bucket.glob("*.json") if p.is_file())


def move_to(bucket: Path, path: Path) -> Path:
    bucket.mkdir(parents=True, exist_ok=True)
    dest = bucket / path.name
    dest.write_bytes(path.read_bytes())
    if path.resolve() != dest.resolve():
        path.unlink(missing_ok=True)
    return dest


def accepted_physical_workstreams() -> set[str]:
    found: set[str] = set()
    for path in list_bucket(ACCEPTED):
        try:
            doc = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if doc.get("evidence_class") != "physical":
            continue
        ws = doc.get("workstream")
        if ws:
            found.add(str(ws))
    return found


def verify_artifact_hash(path: Path) -> bool:
    doc = json.loads(path.read_text(encoding="utf-8"))
    claimed = doc.get("artifact_sha256")
    if not claimed:
        return False
    return claimed == content_digest(doc)
