#!/usr/bin/env python3
"""Select the intended Gate 2 integrated run directory.

CI previously used `ls results/integrated/* | head -n 1` and
`pathlib.Path(...).glob('*')[0]`. Those are order-dependent and can pick a
committed calibration artifact such as `calibration-cal-20260722T170604Z`
that has no `gate2_status.json`.

Selection is by Gate 2 contract artifacts, not glob/ls order. Missing the
intended run is a hard failure — this does not weaken Gate 2.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REQUIRED_MARKERS = (
    "gate2_status.json",
    "checksums.sha256",
    "manifest.json",
)


def _has_markers(path: Path) -> bool:
    return path.is_dir() and all((path / name).is_file() for name in REQUIRED_MARKERS)


def _describe_children(output_root: Path) -> str:
    lines: list[str] = []
    if not output_root.is_dir():
        return f"  (missing directory {output_root})"
    children = sorted(output_root.iterdir(), key=lambda p: p.name)
    if not children:
        return "  (empty)"
    for child in children:
        if not child.is_dir():
            lines.append(f"  {child.name}: not a directory")
            continue
        missing = [name for name in REQUIRED_MARKERS if not (child / name).is_file()]
        if missing:
            lines.append(f"  {child.name}: incomplete (missing {', '.join(missing)})")
        else:
            lines.append(f"  {child.name}: complete Gate 2 run")
    return "\n".join(lines)


def select_gate2_run_dir(
    output_root: Path,
    prefer_run_id: str | None = None,
) -> Path:
    """Return the intended Gate 2 run dir or raise ValueError."""
    output_root = output_root.resolve()
    if not output_root.is_dir():
        raise ValueError(
            f"Gate 2 output root does not exist: {output_root}\n"
            "Refusing glob/ls fallback."
        )

    candidates = sorted(
        (child for child in output_root.iterdir() if _has_markers(child)),
        key=lambda p: p.name,
    )
    inventory = _describe_children(output_root)

    if prefer_run_id:
        preferred = output_root / prefer_run_id
        if not _has_markers(preferred):
            raise ValueError(
                f"Preferred Gate 2 run_id {prefer_run_id!r} is not a complete "
                f"integrated result under {output_root}.\n"
                "Required: " + ", ".join(REQUIRED_MARKERS) + "\n"
                "Inventory:\n" + inventory + "\n"
                "Refusing glob/ls fallback (would pick stray calibration artifacts)."
            )
        return preferred

    if not candidates:
        raise ValueError(
            f"No complete Gate 2 integrated run under {output_root}.\n"
            "Required: " + ", ".join(REQUIRED_MARKERS) + "\n"
            "Inventory:\n" + inventory + "\n"
            "Refusing glob/ls fallback."
        )

    if len(candidates) == 1:
        return candidates[0]

    # Multiple complete runs: the CI pipeline just refreshed one. Prefer the
    # newest gate2_status.json rather than lexicographic glob/ls order.
    return max(candidates, key=lambda p: (p / "gate2_status.json").stat().st_mtime)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Select the intended Gate 2 integrated run directory"
    )
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument(
        "--prefer-run-id",
        default=None,
        help="Require this run_id (typically the fixture/pipeline run).",
    )
    parser.add_argument(
        "--edge-input",
        type=Path,
        default=None,
        help="Read run_id from an edge_measurement_batch JSON (sets prefer-run-id).",
    )
    parser.add_argument(
        "--github-env",
        type=Path,
        default=None,
        help="Append RUN_DIR=<abs path> to this file (GITHUB_ENV).",
    )
    args = parser.parse_args(argv)

    prefer = args.prefer_run_id
    if args.edge_input is not None:
        edge = json.loads(args.edge_input.read_text(encoding="utf-8"))
        edge_run_id = edge.get("run_id")
        if not edge_run_id:
            print(f"ERROR: {args.edge_input} has no run_id", file=sys.stderr)
            return 1
        if prefer and prefer != edge_run_id:
            print(
                f"ERROR: --prefer-run-id {prefer!r} != edge-input run_id {edge_run_id!r}",
                file=sys.stderr,
            )
            return 1
        prefer = edge_run_id

    try:
        selected = select_gate2_run_dir(args.output_root, prefer_run_id=prefer)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    resolved = str(selected.resolve())
    print(resolved)
    if args.github_env is not None:
        with args.github_env.open("a", encoding="utf-8") as fh:
            fh.write(f"RUN_DIR={resolved}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
