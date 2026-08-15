"""Executable IMT-2030 evaluation harness entrypoint."""
from __future__ import annotations

import json
from pathlib import Path

from net_sec_rc001.imt2030_eval import run_imt2030_eval_harness

ROOT = Path(__file__).resolve().parents[2]


def evaluate(out_dir: Path | None = None) -> dict:
    report = run_imt2030_eval_harness()
    if out_dir is not None:
        out_dir = Path(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "IMT2030_EVAL_HARNESS.json").write_text(
            json.dumps(report, indent=2) + "\n", encoding="utf-8"
        )
    return report


def main() -> int:
    report = evaluate(ROOT / "artifacts" / "standards")
    print("IMT2030_EVAL_HARNESS_PASS" if report["ok"] else "IMT2030_EVAL_HARNESS_FAIL")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
