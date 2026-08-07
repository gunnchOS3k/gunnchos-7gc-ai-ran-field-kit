"""Gate 1 operator-grade physical evidence system."""

from __future__ import annotations

from pathlib import Path

OPERATOR_ROOT = Path(__file__).resolve().parent
GATE1_ROOT = OPERATOR_ROOT.parent
REPO_ROOT = GATE1_ROOT.parent
SCHEMAS = OPERATOR_ROOT / "schemas"
EVIDENCE = GATE1_ROOT / "evidence"
SESSIONS = EVIDENCE / "pending" / "sessions"
ACCEPTED = EVIDENCE / "accepted"
REJECTED = EVIDENCE / "rejected"

PRESENCE_TOKENS = (
    "PRESENT_CONFIRMED",
    "MISSING",
    "MISSING_ASSUMED",
    "TOOLCHAIN_MISSING",
    "UNSUPPORTED_PLATFORM",
    "PERMISSION_DENIED",
    "INDETERMINATE",
)
