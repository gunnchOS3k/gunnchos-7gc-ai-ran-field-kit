"""Descriptive replication stats — no p-value theater."""
from __future__ import annotations

from typing import Sequence


def mean(xs: Sequence[float]) -> float:
    return sum(xs) / max(1, len(xs))


def median(xs: Sequence[float]) -> float:
    s = sorted(xs)
    n = len(s)
    if n == 0:
        return 0.0
    if n % 2:
        return s[n // 2]
    return 0.5 * (s[n // 2 - 1] + s[n // 2])


def summarize(xs: Sequence[float]) -> dict:
    if not xs:
        return {"n": 0, "mean": None, "median": None, "min": None, "max": None}
    return {
        "n": len(xs),
        "mean": round(mean(xs), 6),
        "median": round(median(xs), 6),
        "min": round(min(xs), 6),
        "max": round(max(xs), 6),
        "note": "Descriptive only; no NHST / p-value claim",
    }


def win_rate(flags: Sequence[bool]) -> dict:
    n = len(flags)
    wins = sum(1 for f in flags if f)
    return {
        "n": n,
        "wins": wins,
        "win_rate": round(wins / max(1, n), 4),
        "note": "Fraction of seeds where predeclared win condition holds; not a p-value",
    }
