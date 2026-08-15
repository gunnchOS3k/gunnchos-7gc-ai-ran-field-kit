"""Process-stable seed derivation — never use builtin hash() for experiment RNG.

Python's hash() is salted per process (PYTHONHASHSEED), which caused dual-tree
float drift between artifacts/r6g and artifacts/net_sec_rc001/r6g.
"""
from __future__ import annotations

import hashlib


def stable_int(label: str, *, mod: int = 10_000) -> int:
    """Deterministic non-negative int from a string label."""
    digest = hashlib.sha256(label.encode("utf-8")).hexdigest()
    return int(digest[:8], 16) % mod


def mix_seed(base: int, *labels: str, mod: int = 2_147_483_647) -> int:
    """Mix an integer seed with stable string labels."""
    h = hashlib.sha256(f"{base}|{'|'.join(labels)}".encode("utf-8")).hexdigest()
    return int(h[:8], 16) % mod
