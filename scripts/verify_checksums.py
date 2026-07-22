#!/usr/bin/env python3
"""Verify SHA-256 checksum manifests."""
from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("checksum_file", type=Path)
    args = parser.parse_args(argv)
    base = args.checksum_file.parent
    errors = []
    for line in args.checksum_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        digest, name = line.split(None, 1)
        name = name.strip()
        path = base / name
        if not path.is_file():
            errors.append(f"missing file: {name}")
            continue
        actual = sha256_file(path)
        if actual != digest:
            errors.append(f"hash mismatch for {name}: expected={digest} actual={actual}")
    if errors:
        print("FAIL:\n- " + "\n- ".join(errors), file=sys.stderr)
        return 1
    print("checksums ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
