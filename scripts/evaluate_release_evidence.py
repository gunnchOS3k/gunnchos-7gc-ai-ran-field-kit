#!/usr/bin/env python3
"""Evaluate Gate 5/6 release-evidence status independently of Gate 2."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from evaluate_gate2_status import evaluate_release_evidence  # noqa: E402


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--checklist", type=Path, default=None)
    p.add_argument("--output", type=Path, default=None)
    args = p.parse_args(argv)
    flags = None
    if args.checklist and args.checklist.is_file():
        flags = json.loads(args.checklist.read_text(encoding="utf-8"))
    result = evaluate_release_evidence(flags)
    text = json.dumps(result, indent=2)
    print(text)
    if args.output:
        args.output.write_text(text + "\n", encoding="utf-8")
    return 0 if result["release_evidence_status"] == "RELEASE_EVIDENCE_COMPLETE" else 2


if __name__ == "__main__":
    raise SystemExit(main())
