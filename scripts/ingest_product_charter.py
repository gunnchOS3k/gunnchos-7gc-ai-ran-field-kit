#!/usr/bin/env python3
"""Ingest product charter into program/charters/ (verbatim copy + records)."""

from __future__ import annotations

import argparse
import hashlib
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = Path(
    "/Users/gunnchos/Downloads/gunnchos-7gc-research-product-scine/"
    "gunnchOS3k Carrier-Grade 6G Equitable Compute Ecosystem (1).md"
)
DEST = ROOT / "program" / "charters" / "GUNNCHOS3K_CARRIER_GRADE_6G_ECOSYSTEM.md"
INGESTION_SCRIPT_VERSION = "1.0.0"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    args = p.parse_args()
    if not args.source.exists():
        print(f"BLOCKED_MISSING_PRODUCT_CHARTER: {args.source}", file=sys.stderr)
        return 2
    DEST.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(args.source, DEST)
    text = DEST.read_text(encoding="utf-8")
    record = {
        "source_filename": args.source.name,
        "ingested_path": str(DEST.relative_to(ROOT)),
        "sha256": sha256(DEST),
        "ingestion_timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "line_count": len(text.splitlines()),
        "ingestion_script_version": INGESTION_SCRIPT_VERSION,
        "git_state": {"applicable": False, "notes": "Source charter outside git repo"},
    }
    (DEST.parent / "CHARTER_SOURCE_RECORD.yaml").write_text(
        yaml.safe_dump(record, sort_keys=False), encoding="utf-8"
    )
    approval = {
        "status": "PRODUCT_CHARTER_APPROVAL_PENDING_EDMUND",
        "approved": False,
        "approver": None,
        "approval_timestamp_utc": None,
        "notes": "Ingestion is not approval. GATE_0_PASS prohibited.",
    }
    (DEST.parent / "CHARTER_APPROVAL_RECORD.yaml").write_text(
        yaml.safe_dump(approval, sort_keys=False), encoding="utf-8"
    )
    print(f"INGESTED sha256={record['sha256']} lines={record['line_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
