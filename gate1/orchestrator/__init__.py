"""Gate 1 orchestrator package."""

from __future__ import annotations

from pathlib import Path

GATE1_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = GATE1_ROOT.parent
CONTRACTS = GATE1_ROOT / "contracts"
MANIFESTS = GATE1_ROOT / "manifests"
EVIDENCE = GATE1_ROOT / "evidence"
PENDING = EVIDENCE / "pending"
ACCEPTED = EVIDENCE / "accepted"
REJECTED = EVIDENCE / "rejected"
RUNS = EVIDENCE / "runs"
REPORTS = GATE1_ROOT / "reports"
DEFAULT_REPOS_ROOT = REPO_ROOT.parent
REPO_LOCK = REPO_ROOT / "integration" / "repo-lock.json"
COLLISION_AUDIT = Path("/tmp/gate1_collision_audit.json")

PHYSICAL_CLAIM_LEVELS = {
    "PHYSICAL_BOOT",
    "PHYSICAL_RING",
    "PHYSICAL_DOCK",
    "PHYSICAL_AI_DEVICE",
    "PHYSICAL_GAME_DEVICE",
}

REQUIRED_PHYSICAL_WORKSTREAMS = ("boot", "ring-auth", "dock", "ai-runtime", "games")
