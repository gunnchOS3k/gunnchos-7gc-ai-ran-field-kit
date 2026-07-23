#!/usr/bin/env python3
"""Canonical assignment hashing shared with Edge-IO Android.

Algorithm: gunnchos-canonical-json-sha256-v1
See docs/PILOT_ASSIGNMENT_CANONICAL_HASHING.md
"""
from __future__ import annotations

import hashlib
import json
import math
import re
from typing import Any

ALGORITHM_V1 = "gunnchos-canonical-json-sha256-v1"


def _escape_string(value: str) -> str:
    """Match JSON RFC / Python json.dumps(ensure_ascii=True) string encoding."""
    return json.dumps(value, ensure_ascii=True, separators=(",", ":"))


def canonicalize_value(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int) and not isinstance(value, bool):
        return str(value)
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("non-finite JSON number is not allowed")
        # Integers must be emitted without a fractional part.
        if value.is_integer() and abs(value) < 1e15:
            return str(int(value))
        # Deterministic shortest decimal (no scientific notation).
        text = format(value, ".15g")
        if "e" in text.lower():
            text = format(value, "f").rstrip("0").rstrip(".")
            if text in {"", "-"}:
                text = "0"
        return text
    if isinstance(value, str):
        return _escape_string(value)
    if isinstance(value, list):
        return "[" + ",".join(canonicalize_value(v) for v in value) + "]"
    if isinstance(value, dict):
        parts = []
        for key in sorted(value.keys()):
            parts.append(_escape_string(key) + ":" + canonicalize_value(value[key]))
        return "{" + ",".join(parts) + "}"
    raise TypeError(f"unsupported JSON type: {type(value)!r}")


def hash_payload(doc: dict) -> tuple[str, bytes]:
    """Return (hex_digest, canonical_utf8_bytes) excluding assignment_hash."""
    payload = {k: v for k, v in doc.items() if k != "assignment_hash"}
    canonical = canonicalize_value(payload).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest(), canonical


def assignment_hash(doc: dict) -> str:
    digest, _ = hash_payload(doc)
    return digest


def normalize_for_emit(doc: dict) -> dict:
    """Apply emit-time normalizations required by the v1 contract."""
    out = dict(doc)
    out["assignment_hash_algorithm"] = ALGORITHM_V1
    if "planned_duration_seconds" in out:
        duration = out["planned_duration_seconds"]
        if isinstance(duration, bool) or not isinstance(duration, (int, float)):
            raise ValueError("planned_duration_seconds must be a number")
        if isinstance(duration, float) and not duration.is_integer():
            raise ValueError("planned_duration_seconds must be an integer number of seconds")
        out["planned_duration_seconds"] = int(duration)
    return out


def stamp_hash(doc: dict) -> dict:
    out = normalize_for_emit(doc)
    out.pop("assignment_hash", None)
    digest, _ = hash_payload(out)
    out["assignment_hash"] = digest
    return out


def verify_hash(doc: dict) -> dict:
    declared = doc.get("assignment_hash")
    algo = doc.get("assignment_hash_algorithm", ALGORITHM_V1)
    digest, canonical = hash_payload(doc)
    return {
        "ok": declared == digest and algo == ALGORITHM_V1,
        "declared": declared,
        "calculated": digest,
        "algorithm": algo,
        "canonical_byte_count": len(canonical),
        "canonical_sha256": hashlib.sha256(canonical).hexdigest(),
    }
