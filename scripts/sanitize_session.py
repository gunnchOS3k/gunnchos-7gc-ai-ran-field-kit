#!/usr/bin/env python3
"""Sanitize a raw session: strip prohibited fields, preserve hash linkage."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from gate3_common import (  # noqa: E402
    PROHIBITED_ALIASES,
    normalize_key,
    recursive_privacy_scan,
    sha256_bytes,
    sha256_file,
    write_json,
)


def strip_prohibited(obj):
    removed = []
    def _walk(node, path="$"):
        if isinstance(node, dict):
            out = {}
            for k, v in node.items():
                child = f"{path}.{k}"
                if normalize_key(k) in PROHIBITED_ALIASES:
                    removed.append(child)
                    continue
                out[k] = _walk(v, child)
            return out
        if isinstance(node, list):
            return [_walk(x, f"{path}[{i}]") for i, x in enumerate(node)]
        return node
    return _walk(obj), removed


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True)
    p.add_argument("--output", required=True)
    args = p.parse_args(argv)
    src = Path(args.input)
    raw = json.loads(src.read_text(encoding="utf-8"))
    source_hash = sha256_file(src)
    cleaned, removed = strip_prohibited(raw)
    # Never overwrite raw
    out = Path(args.output)
    if out.resolve() == src.resolve():
        raise SystemExit("Refusing to overwrite raw source")
    cleaned.setdefault("sanitization", {})
    cleaned["sanitization"] = {
        "source_path": str(src),
        "source_hash": source_hash,
        "removed_paths": removed,
        "sanitized_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    }
    write_json(out, cleaned)
    remaining = recursive_privacy_scan(cleaned)
    report = {
        "ok": not remaining,
        "output": str(out),
        "output_hash": sha256_file(out),
        "source_hash": source_hash,
        "removed_paths": removed,
        "remaining_findings": remaining,
    }
    print(json.dumps(report, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
