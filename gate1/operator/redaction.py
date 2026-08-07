"""Redaction helpers for operator evidence bundles."""

from __future__ import annotations

import copy
import re
from typing import Any

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
MAC_RE = re.compile(r"\b([0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}\b")
SERIALISH_KEYS = {
    "serial",
    "hardware_serial",
    "udid",
    "imei",
    "mac",
    "mac_address",
    "email",
    "owner",
    "phone",
}


def _redact_string(value: str) -> str:
    value = EMAIL_RE.sub("[REDACTED_EMAIL]", value)
    value = MAC_RE.sub("[REDACTED_MAC]", value)
    return value


def redact_obj(obj: Any) -> Any:
    """Return a deep-copied object with common PII patterns redacted."""
    data = copy.deepcopy(obj)
    return _walk(data)


def _walk(node: Any, key: str | None = None) -> Any:
    if isinstance(node, dict):
        out = {}
        for k, v in node.items():
            if str(k).lower() in SERIALISH_KEYS and isinstance(v, str) and v:
                out[k] = "[REDACTED]"
            else:
                out[k] = _walk(v, key=str(k))
        return out
    if isinstance(node, list):
        return [_walk(v, key=key) for v in node]
    if isinstance(node, str):
        return _redact_string(node)
    return node
