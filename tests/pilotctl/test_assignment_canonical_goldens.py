#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from assignment_canonical import hash_payload  # noqa: E402
from pilotctl import validate_assignment, verify_roundtrip  # noqa: E402

FIX = ROOT / "fixtures" / "pilot_assignment"

# Frozen inside fixture [created_at, expires_at) — never regenerate golden for clock drift.
GOLDEN_NOW = datetime(2026, 7, 23, 23, 30, 0, tzinfo=timezone.utc)


def test_valid_rehearsal_golden():
    path = FIX / "valid_rehearsal.json"
    meta = json.loads((FIX / "valid_rehearsal.meta.json").read_text())
    doc = json.loads(path.read_text())
    digest, canon = hash_payload(doc)
    assert digest == meta["expected_hash"]
    assert len(canon) == meta["canonical_byte_count"]
    assert canon == (FIX / "valid_rehearsal.canonical.json").read_bytes()
    assert validate_assignment(path, now=GOLDEN_NOW)["ok"] is True
    assert verify_roundtrip(path)["ok"] is True


def test_valid_rehearsal_expired_under_post_expiry_now():
    path = FIX / "valid_rehearsal.json"
    after = datetime(2026, 7, 25, 0, 0, 0, tzinfo=timezone.utc)
    result = validate_assignment(path, now=after)
    assert result["ok"] is False
    assert any("expired" in e.lower() for e in result["errors"])


def test_reordered_and_producer_reorder_same_hash():
    base = json.loads((FIX / "valid_rehearsal.json").read_text())
    d1, _ = hash_payload(base)
    d2, _ = hash_payload(json.loads((FIX / "reordered_keys.json").read_text()))
    d3, _ = hash_payload(json.loads((FIX / "producer_reordered.json").read_text()))
    assert d1 == d2 == d3


def test_tampered_and_modified_fail():
    assert validate_assignment(FIX / "tampered_zone.json")["ok"] is False
    assert validate_assignment(FIX / "modified_value.json")["ok"] is False
    assert validate_assignment(FIX / "wrong_algorithm.json")["ok"] is False


def test_expired_hash_ok_but_validate_fails():
    result = validate_assignment(FIX / "expired.json")
    assert result["ok"] is False
    assert any("expired" in e.lower() for e in result["errors"])


def test_harmless_whitespace_same_hash():
    base = json.loads((FIX / "valid_rehearsal.json").read_text())
    d1, _ = hash_payload(base)
    # Re-dump with spaces then reload — JSON parse normalizes; hash of objects must match.
    spaced = json.dumps(base, indent=2)
    d2, _ = hash_payload(json.loads(spaced))
    assert d1 == d2


def test_one_byte_semantic_mutation_fails():
    base = json.loads((FIX / "valid_rehearsal.json").read_text())
    bad = dict(base)
    bad["named_test_zone"] = base["named_test_zone"] + "x"
    assert hash_payload(bad)[0] != hash_payload(base)[0]
    # Persist temporary file for validate_assignment
    import tempfile
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
        json.dump(bad, fh)
        path = Path(fh.name)
    try:
        assert validate_assignment(path, now=GOLDEN_NOW)["ok"] is False
    finally:
        path.unlink(missing_ok=True)
