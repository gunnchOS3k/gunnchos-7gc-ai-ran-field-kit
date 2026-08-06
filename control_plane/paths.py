"""Filesystem paths for the Gate 0 control plane."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROGRAM = ROOT / "program"
CHARTERS = PROGRAM / "charters"
REQUIREMENTS = PROGRAM / "requirements"
CLAIMS = PROGRAM / "claims"
GATES = PROGRAM / "gates"
REPOSITORIES = PROGRAM / "repositories"
EVIDENCE = PROGRAM / "evidence"
BACKLOG = PROGRAM / "backlog"
REPORTS = PROGRAM / "reports"
DECISIONS = PROGRAM / "decisions"
SCHEMAS = PROGRAM / "schemas"
SCRIPTS = ROOT / "scripts"
TESTS = ROOT / "tests" / "control_plane"

CHARTER_FILE = CHARTERS / "GUNNCHOS3K_CARRIER_GRADE_6G_ECOSYSTEM.md"
CHARTER_SOURCE_RECORD = CHARTERS / "CHARTER_SOURCE_RECORD.yaml"
CHARTER_APPROVAL_RECORD = CHARTERS / "CHARTER_APPROVAL_RECORD.yaml"

DEFAULT_REPOS_ROOT = ROOT.parent
_LOCAL_AUDIT = PROGRAM / "repositories" / "audits" / "branch_migration_audit.json"
BRANCH_AUDIT_PATH = _LOCAL_AUDIT if _LOCAL_AUDIT.exists() else Path("/tmp/branch_migration_audit.json")
