"""Attribute redaction — no PII by default."""
from __future__ import annotations

import re
from typing import Any, Mapping, MutableMapping

from .conventions import FORBIDDEN_DEFAULT_ATTRIBUTES

_EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
_PHONE = re.compile(r"\+?\d[\d\-\s]{7,}\d")


def redact_attributes(
    attrs: Mapping[str, Any],
    *,
    allow_pii: bool = False,
) -> dict[str, Any]:
    """Return a redacted copy. PII keys/values stripped unless allow_pii=True."""
    out: dict[str, Any] = {}
    for key, value in attrs.items():
        lk = str(key).lower()
        if not allow_pii and (
            key in FORBIDDEN_DEFAULT_ATTRIBUTES
            or lk in FORBIDDEN_DEFAULT_ATTRIBUTES
            or any(p in lk for p in ("email", "student", "password", "ssn", "phone"))
        ):
            out[key] = "[REDACTED]"
            continue
        if isinstance(value, str) and not allow_pii:
            v = _EMAIL.sub("[REDACTED_EMAIL]", value)
            v = _PHONE.sub("[REDACTED_PHONE]", v)
            out[key] = v
        else:
            out[key] = value
    return out
